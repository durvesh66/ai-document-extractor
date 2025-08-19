import os
import time
import google.generativeai as genai
from src.models import ExtractedField, ExtractionResult, QualityAssurance
from src.processor import get_text_and_type
from src.prompts import DOC_TYPE_PROMPT, EXTRACTION_PROMPT_TEMPLATE
from src.confidence import score_confidence, aggregate_confidence, validate_fields

class DocumentExtractionAgent:
    def __init__(self, gemini_api_key: str):
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        self.gemini_api_key = gemini_api_key

    def extract(self, file_bytes, filename, field_list=None):
        start = time.time()
        text, file_type = get_text_and_type(file_bytes, filename, self.gemini_api_key)
        doc_type = self.classify_doc_type(text)
        fields_to_extract = field_list if field_list else self.default_fields(doc_type)
        fields = self.extract_fields(text, doc_type, fields_to_extract)
        for f in fields:
            f.confidence = score_confidence(f)
        qa = validate_fields(fields, doc_type)
        overall_conf = aggregate_confidence(fields, qa)
        end = time.time()
        return ExtractionResult(
            doc_type=doc_type,
            fields=fields,
            overall_confidence=overall_conf,
            qa=qa,
            processing_time=end-start
        )

    def classify_doc_type(self, text):
        response = self.model.generate_content(DOC_TYPE_PROMPT.format(doc_text=text[:2000]))
        doc_type = response.text.strip().lower()
        if doc_type not in ["invoice", "medical_bill", "prescription"]:
            doc_type = "invoice"
        return doc_type

    def default_fields(self, doc_type):
        if doc_type == "invoice":
            return ["invoice_number","date","vendor_name","total_amount"]
        elif doc_type == "medical_bill":
            return ["patient_name","provider_name","total_charges"]
        elif doc_type == "prescription":
            return ["patient_name","prescriber_name","medications"]
        return []

    def extract_fields(self, doc_text, doc_type, fields):
        fields_list = ", ".join(fields)
        
        prompt = f"""Extract these fields from this {doc_type} document: {fields_list}

Document text:
{doc_text[:3000]}

Return only a JSON array like this:
[{{"name":"patient_name","value":"Sarah Johnson","confidence":0.9}}]

Extract the actual values you see in the document. Use confidence 0.8-0.9 for clear values."""
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Find JSON array in response
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                
                import json
                results = json.loads(json_str)
                
                extracted_fields = []
                for item in results:
                    if isinstance(item, dict) and "name" in item and "value" in item:
                        extracted_fields.append(ExtractedField(
                            name=item["name"],
                            value=item["value"],
                            confidence=item.get("confidence", 0.7)
                        ))
                
                return extracted_fields
                
        except Exception as e:
            print(f"Extraction error: {e}")
            
        return []

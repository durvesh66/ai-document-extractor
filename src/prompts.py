DOC_TYPE_PROMPT = """
Classify this document as one of these types: invoice, medical_bill, or prescription.
Look for key indicators:
- Invoice: invoice number, vendor, billing address, line items, totals
- Medical_bill: patient name, provider, medical procedures, charges, insurance
- Prescription: patient, prescriber, medications, dosage, pharmacy

Document text:
{doc_text}

Respond with ONLY the document type: invoice, medical_bill, or prescription
"""

EXTRACTION_PROMPT_TEMPLATE = """
You are an expert at extracting structured data from documents.

Document Type: {doc_type}
Document Text:
{doc_text}

Extract the following fields and return them as a JSON array:
{fields}

For each field, provide:
- name: the field name exactly as listed above
- value: the extracted value (or "NOT_FOUND" if missing)
- confidence: a score from 0.0 to 1.0 based on how clear/certain the extraction is

Example format:
[
  {{"name": "patient_name", "value": "John Smith", "confidence": 0.95}},
  {{"name": "provider_name", "value": "ABC Medical Center", "confidence": 0.90}}
]

Important:
- Extract values exactly as they appear in the document
- Use "NOT_FOUND" for missing fields
- Be conservative with confidence scores
- Return only valid JSON array format
"""

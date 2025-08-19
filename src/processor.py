import io
from PIL import Image
import PyPDF2
import google.generativeai as genai

def extract_text_from_pdf(file_bytes):
    pdf = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    text = ""
    for i, page in enumerate(pdf.pages):
        t = page.extract_text()
        text += f"\n--- Page {i+1} ---\n{t if t else ''}\n"
    return text

def process_image_with_gemini(file_bytes, api_key):
    """Use Gemini for image OCR - better than Tesseract"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Upload image to Gemini
        image = Image.open(io.BytesIO(file_bytes))
        
        prompt = """
        Extract all text from this image. 
        Preserve formatting, numbers, dates, and structure.
        If this appears to be an invoice, medical bill, or prescription, 
        focus on key fields like names, dates, amounts, and addresses.
        """
        
        response = model.generate_content([prompt, image])
        return response.text
        
    except Exception as e:
        return f"[Gemini OCR Error: {str(e)}]"

def get_text_and_type(file_bytes, filename, api_key=None):
    ext = filename.split('.')[-1].lower()
    if ext == "pdf":
        return extract_text_from_pdf(file_bytes), "pdf"
    elif ext in ["jpg", "jpeg", "png", "bmp", "gif"]:
        if api_key:
            return process_image_with_gemini(file_bytes, api_key), "image"
        else:
            return "[Error: API key required for image processing]", "image"
    else:
        raise ValueError(f"Unsupported file type: {ext}")


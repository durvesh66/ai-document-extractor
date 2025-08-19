import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the parent directory to Python path to find src module
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import streamlit as st
from src.agent import DocumentExtractionAgent

st.set_page_config(page_title="AI Document Extractor", layout="wide")
st.title("🚀 AI-Powered Document Extraction (Gemini)")

# Try to load API key from environment, otherwise ask user
default_api_key = os.getenv('GEMINI_API_KEY', '')
api_key = st.sidebar.text_input("Gemini API Key", value=default_api_key, type="password")

uploaded = st.file_uploader("Upload PDF or Image", type=["pdf", "jpg", "jpeg", "png"])
custom_fields = st.text_input("List fields to extract, comma separated (optional)")

if api_key and uploaded:
    try:
        agent = DocumentExtractionAgent(api_key)
        fields = [f.strip() for f in custom_fields.split(",") if f.strip()] if custom_fields else None
        
        with st.spinner("Extracting..."):
            result = agent.extract(uploaded.read(), uploaded.name, fields)

        st.subheader(f"Detected Document Type: {result.doc_type}")
        
        # Display results
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Extracted Fields")
            for f in result.fields:
                st.write(f"**{f.name}**: {f.value}")
                st.progress(f.confidence, text=f"Confidence: {f.confidence:.2f}")
        
        with col2:
            st.subheader("Full JSON Output")
            st.json(result.model_dump())

        st.subheader(f"Overall Confidence: {result.overall_confidence:.2f}")
        st.progress(result.overall_confidence)
        
        st.write("**Validation Notes:**", result.qa.notes)
        
        # Download button
        json_data = result.model_dump_json(indent=2)
        st.download_button(
            label="📥 Download Result JSON",
            data=json_data,
            file_name="extraction_result.json",
            mime="application/json"
        )
        
    except Exception as e:
        st.error(f"Error during extraction: {str(e)}")
        st.write("Please check your API key and try again.")

elif not api_key:
    st.warning("⚠️ Please enter your Gemini API Key in the sidebar to proceed.")
    st.info("Get your free API key from: https://makersuite.google.com/app/apikey")
elif not uploaded:
    st.info("📄 Please upload a PDF or image file to extract data.")

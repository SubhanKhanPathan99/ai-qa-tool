import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="AI QA Assistant", layout="wide", page_icon="🤖")

# 2. Secure API Key Management
# This block prevents NameError by defining api_key at the start
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    # If the key is missing from secrets, show a clear error and stop
    st.error("❌ API Key not found! Please add 'GEMINI_API_KEY' to your Streamlit Secrets.")
    st.stop()

# 3. Header and UI
st.title("📄 BRD to Test Case Generator")
st.markdown("Upload a Business Requirement Document to generate structured test cases automatically.")

# Sidebar for feedback/status
st.sidebar.header("System Status")
st.sidebar.success("API Key loaded securely ✅")
st.sidebar.info("Model: Gemini-1.5-Flash")

# 4. File Uploader
uploaded_file = st.file_uploader("Upload BRD (PDF Format)", type="pdf")

if uploaded_file:
    try:
        # Initialize Gemini with the secret key
        genai.configure(api_key=api_key)
        # Using the most stable flash model name
        model = genai.GenerativeModel('gemini-flash-latest')

        # Extract Text from PDF
        reader = PdfReader(uploaded_file)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text()

        if st.button("Generate Test Cases"):
            with st.spinner("Analyzing requirements and generating test cases..."):
                # Enhanced AI Prompt for Negative and Positive cases
                prompt = f"""
                Act as a Senior QA Engineer. Analyze the following Business Requirement Document (BRD) 
                and generate a comprehensive test case matrix.
                
                Include BOTH Positive (Happy Path) and Negative (Invalid/Boundary) test cases.
                Focus Negative cases on: missing data, unauthorized access, and invalid formats.

                Format the output as a clean table with these columns: 
                Test Case ID, Type (Positive/Negative), Requirement Reference, Description, Expected Result, Priority.
                
                BRD Text:
                {full_text[:15000]} 
                """
                
                response = model.generate_content(prompt)
                st.subheader("Generated Test Case Matrix")
                st.markdown(response.text) # Using markdown for table rendering
                
                # Optional: Add a simple way to copy/download
                st.download_button(
                    label="📥 Download Results as Text",
                    data=response.text,
                    file_name="test_cases.txt",
                    mime="text/plain"
                )
                
    except Exception as e:
        st.error(f"An error occurred: {e}")
else:
    st.info("👋 Welcome! Please upload a PDF file to begin generating test cases.")
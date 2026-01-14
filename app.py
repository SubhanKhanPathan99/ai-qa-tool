import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="AI QA Assistant", layout="wide")
st.title("📄 BRD to Test Case Generator")
st.markdown("Upload a Business Requirement Document to generate structured test cases automatically.")

# 2. Sidebar for Configuration
st.sidebar.header("Settings")
api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")
st.sidebar.info("Get your key at: https://aistudio.google.com/")

# 3. File Uploader
uploaded_file = st.file_uploader("Upload BRD (PDF Format)", type="pdf")

if uploaded_file and api_key:
    try:
        # Initialize Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')

        # Extract Text from PDF
        reader = PdfReader(uploaded_file)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text()

        if st.button("Generate Test Cases"):
            with st.spinner("Analyzing requirements and generating test cases..."):
                # AI Prompt
                prompt = f"""
                Act as a Senior QA Engineer. Analyze the following Business Requirement Document (BRD) 
                and generate a comprehensive test case matrix.
                
                IMPORTANT: You must include both Positive (Happy Path) and Negative (Boundary/Invalid/Error) test cases.
                
                For Negative Test Cases, focus on:
                - Invalid data formats or missing mandatory fields.
                - Exceeding character limits or unauthorized access.
                - System behavior when external services fail.

                Include the following columns: 
                Test Case ID, Type (Positive/Negative), Requirement Reference, Description, Expected Result, and Priority.
                
                BRD Text:
                {full_text[:15000]} 
                """
                
                response = model.generate_content(prompt)
                st.subheader("Generated Test Cases")
                st.write(response.text)
                
    except Exception as e:
        st.error(f"An error occurred: {e}")
else:
    st.warning("Please provide both an API Key and a PDF file to proceed.")
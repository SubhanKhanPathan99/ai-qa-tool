import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import pandas as pd
import io

# 1. PAGE CONFIGURATION & THEME
st.set_page_config(
    page_title="TestcaseCraft AI",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS for a professional look
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: 800;
        color: #007BFF;
        text-align: center;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #6c757d;
        text-align: center;
        margin-bottom: 30px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #007BFF;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. SECURE API KEY INITIALIZATION
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    # Using stable model alias
    model = genai.GenerativeModel('gemini-flash-latest')
else:
    st.error("⚠️ API Key not found in Secrets! Please add 'GEMINI_API_KEY' to your Streamlit Cloud settings.")
    st.stop()

# 3. FRONT-END UI ELEMENTS
st.markdown('<p class="main-header">TestcaseCraft AI</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Professional QA Requirement Analysis & Test Matrix Generator</p>', unsafe_allow_html=True)

# Tabs for a clean interface
tab1, tab2 = st.tabs(["🚀 Generator", "📖 Help & Instructions"])

with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Upload Requirements")
        uploaded_file = st.file_uploader("Upload BRD (PDF Format)", type="pdf", help="Upload a business requirement document to start.")

    with col2:
        st.subheader("Analysis Settings")
        priority_level = st.select_slider("Select Detail Level", options=["Standard", "Detailed", "Exhaustive"])
        include_neg = st.checkbox("Include Negative Test Cases", value=True)

    if uploaded_file:
        # Extract Text
        reader = PdfReader(uploaded_file)
        full_text = "".join([page.extract_text() for page in reader.pages])

        if st.button("Generate Test Matrix"):
            with st.spinner("🤖 AI is analyzing requirements..."):
                # Enhanced Prompt for structured output
                prompt = f"""
                Act as a Senior QA Manager. Analyze the attached BRD and generate a professional test case matrix.
                Include columns: ID, Type, Requirement, Description, Expected Result, Priority.
                Include both Positive and {'Negative' if include_neg else ''} scenarios.
                Focus on {priority_level} depth.
                
                BRD CONTENT:
                {full_text[:15000]}
                """
                
                response = model.generate_content(prompt)
                
                st.divider()
                st.subheader("✅ Generated Test Case Matrix")
                st.markdown(response.text)
                
                # DOWNLOAD FEATURE
                st.download_button(
                    label="📥 Download Test Cases as CSV",
                    data=response.text,
                    file_name="QA_Test_Matrix.csv",
                    mime="text/csv"
                )

with tab2:
    st.markdown("""
    ### How to use this tool:
    1. **Upload**: Drag and drop your Business Requirement Document (PDF).
    2. **Configure**: Choose the detail level and whether you want negative cases.
    3. **Generate**: Click the button and wait for the AI to build your table.
    4. **Export**: Use the download button to save your cases for Excel or Jira.
    
    *Privacy Note: Your documents are processed in real-time and not stored on our servers.*
    """)

# Sidebar for branding/status
st.sidebar.title("App Info")
st.sidebar.success("Connection: Stable ✅")
st.sidebar.info("Model: Gemini 1.5 Flash")
st.sidebar.write("Developed for QA Professionals")
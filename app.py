import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import pandas as pd
import io

# 1. PAGE SETUP
st.set_page_config(page_title="TestcaseCraft Pro", layout="wide", page_icon="🧪")

# 2. CUSTOM CSS FOR TABLE STYLING
st.markdown("""
    <style>
    .stDataFrame { border: 1px solid #e6e9ef; border-radius: 10px; }
    .main-title { font-size: 3rem; font-weight: 800; color: #1E3A8A; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 3. API INITIALIZATION
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("Missing GEMINI_API_KEY in Secrets.")
    st.stop()

# 4. SIDEBAR CONFIG
with st.sidebar:
    st.title("Settings")
    detail_level = st.select_slider("Granularity", options=["High-Level", "Detailed"])
    include_neg = st.toggle("Negative Scenarios", value=True)
    st.info("Engine: Gemini 1.5 Flash ✅")

# 5. MAIN INTERFACE
st.markdown('<p class="main-title">TestcaseCraft Pro</p>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload Business Requirement Document (PDF)", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    text = "".join([p.extract_text() for p in reader.pages])

    if st.button("🚀 Generate Structured Test Matrix"):
        with st.status("Analyzing and Formatting Table...") as status:
            # THE PROMPT IS KEY: We specify Markdown Table format explicitly
            prompt = f"""
            Act as a Senior QA Lead. Create a structured Test Case Matrix from this BRD.
            OUTPUT ONLY A MARKDOWN TABLE. Do not include conversational text.
            
            Columns: ID, Type (Positive/Negative), Requirement Reference, Description, Expected Result, Priority.
            Detail Level: {detail_level}. Include Negative Scenarios: {include_neg}.
            
            BRD Content: {text[:10000]}
            """
            
            response = model.generate_content(prompt)
            status.update(label="Table Generated!", state="complete", expanded=False)

        # 6. ORGANIZED DISPLAY SECTION
        st.subheader("📊 Final Test Case Matrix")
        
        # We display the raw markdown as a table
        st.markdown(response.text)
        
        # 7. EXPORT SECTION (Download as CSV)
        st.divider()
        st.download_button(
            label="📥 Download Matrix for Excel/Jira",
            data=response.text,
            file_name="QA_Test_Matrix.csv",
            mime="text/csv"
        )
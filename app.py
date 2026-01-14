import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import pandas as pd
import time

# 1. PAGE SETUP
st.set_page_config(page_title="TestcaseCraft Pro", layout="wide", page_icon="🧪")

# 2. ADVANCED CSS (Glassmorphism & Professional Styling)
st.markdown("""
    <style>
    .stApp { background: #fdfdfd; }
    .main-title { font-size: 3.5rem; font-weight: 800; color: #1E3A8A; text-align: center; padding-top: 2rem; }
    .stButton>button { width: 100%; border-radius: 20px; border: none; background: linear-gradient(90deg, #1E3A8A 0%, #3B82F6 100%); color: white; transition: 0.3s; }
    .stButton>button:hover { transform: scale(1.02); }
    </style>
    """, unsafe_allow_html=True)

# 3. SECURE API LOADING
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-flash-latest')
else:
    st.error("Secrets missing: GEMINI_API_KEY")
    st.stop()

# 4. SIDEBAR BRANDING
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2092/2092215.png", width=80)
    st.title("Settings")
    detail_level = st.radio("Test Granularity", ["High-Level", "Detailed", "Technical"])
    include_negative = st.toggle("Negative Scenarios", value=True)
    st.divider()
    st.info("Status: Engine Online ✅")

# 5. MAIN CONTENT
st.markdown('<p class="main-title">TestcaseCraft Pro</p>', unsafe_allow_html=True)

# Advanced Metrics Row
m1, m2, m3 = st.columns(3)
m1.metric("Model", "Gemini 1.5 Flash")
m2.metric("Speed", "Instant")
m3.metric("Type", "QA Expert")

uploaded_file = st.file_uploader("", type="pdf")

if uploaded_file:
    # PDF Processing
    reader = PdfReader(uploaded_file)
    text = "".join([p.extract_text() for p in reader.pages])
    
    # Progress Container
    if st.button("🚀 Generate Professional Matrix"):
        with st.status("Analyzing Document...", expanded=True) as status:
            st.write("Reading PDF content...")
            time.sleep(1)
            st.write("Identifying functional requirements...")
            time.sleep(1)
            st.write("Generating positive and negative paths...")
            
            prompt = f"Act as a Senior QA Manager. Analyze this BRD and generate a test matrix in CSV format (ID, Type, Desc, Expected, Priority). Detail: {detail_level}. Negative cases: {include_negative}. BRD: {text[:10000]}"
            response = model.generate_content(prompt)
            status.update(label="Analysis Complete!", state="complete", expanded=False)

        # 6. RESULTS SECTION
        st.subheader("📊 Requirement Coverage Matrix")
        
        # Display as a clean table (AI needs to output markdown table for this to work best)
        st.markdown(response.text)
        
        # Download Action
        st.download_button(
            label="📥 Export to CSV / Excel",
            data=response.text,
            file_name="QA_Matrix_Pro.csv",
            mime="text/csv"
        )




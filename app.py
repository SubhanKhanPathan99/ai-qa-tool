import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import pandas as pd
import io

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="TestcaseCraft Pro | Enterprise QA",
    page_icon="🧪",
    layout="wide"
)

# 2. ADVANCED CSS: FIXING TITLE & SIDEBAR GAPS
st.markdown("""
    <style>
    /* REMOVE GLOBAL TOP PADDING */
    .block-container {
        padding-top: 1rem !important;
        max-width: 95%;
    }

    /* FIX SIDEBAR: Remove the empty top-margin/box */
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 0rem !important;
    }

    /* ANIMATED PROFESSIONAL BACKGROUND */
    .stApp {
        background: linear-gradient(-45deg, #f8fafc, #f1f5f9, #e2e8f0, #cbd5e1);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
    }
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* HERO TITLE STYLING - Ensures visibility */
    .hero-title {
        font-size: 3.5rem;
        font-weight: 900;
        color: #1e293b;
        text-align: center;
        margin-top: 0px;
        margin-bottom: 0px;
        padding-top: 0px;
    }

    .hero-tagline {
        font-size: 1.2rem;
        color: #475569;
        text-align: center;
        margin-bottom: 2rem;
    }

    /* BUTTON STYLING */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.5rem;
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        font-weight: bold;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. SECURE API INITIALIZATION
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-flash-latest')
else:
    st.error("API Key Missing in Secrets.")
    st.stop()

# 4. SIDEBAR - CLEAN CONTROL PANEL
# We start immediately with the title to avoid the 'empty box' at the top
with st.sidebar:
    st.title("Control Panel")
    st.divider()

    st.subheader("🛠️ Core Settings")
    detail_level = st.select_slider("Analysis Depth", options=["Standard", "Detailed", "Exhaustive"])
    
    st.subheader("🎯 Test Strategy")
    test_framework = st.selectbox("Preferred Framework", ["Standard Manual", "Cucumber/Gherkin", "PyTest/Robot"])
    priority_focus = st.multiselect("Priority Focus", ["Security", "UI/UX", "API", "Performance"], default=["UI/UX"])
    
    st.subheader("🧪 Scenarios")
    include_neg = st.toggle("Negative Scenarios", value=True)
    include_edge = st.toggle("Edge Case Analysis", value=True)
    
    st.divider()
    st.success("System: Ready ✅")

# 5. MAIN PAGE TITLE (Visible & Centered)
st.markdown('<h1 class="hero-title">TestcaseCraft Pro</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-tagline">Enterprise-Grade AI Engine for QA Requirement Analysis</p>', unsafe_allow_html=True)

# 6. MAIN WORKSPACE
uploaded_file = st.file_uploader("Upload Business Requirement Document (PDF)", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    text = "".join([p.extract_text() for p in reader.pages])

    if st.button("🚀 Analyze and Generate Matrix"):
        with st.status("AI Analysis in Progress...", expanded=True) as status:
            prompt = f"""
            Act as a Senior QA Lead. Generate a professional test case matrix.
            OUTPUT ONLY A MARKDOWN TABLE.
            Style: {test_framework}. Focus: {priority_focus}. Depth: {detail_level}.
            Include Negative: {include_neg}. Include Edge: {include_edge}.
            Columns: ID, Type, Requirement Ref, Description, Expected Result, Priority.
            BRD CONTENT: {text[:12000]}
            """
            try:
                response = model.generate_content(prompt)
                status.update(label="Analysis Complete!", state="complete", expanded=False)
                
                st.markdown("---")
                st.subheader("📊 Generated Test Matrix")
                st.markdown(response.text)
                
                st.download_button(
                    label="📥 Export Matrix to CSV",
                    data=response.text,
                    file_name="QA_Matrix.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"Error: {e}")
else:
    st.info("👋 Welcome! Please upload your PDF document to activate the analysis engine.")
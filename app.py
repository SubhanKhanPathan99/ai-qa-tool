import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import pandas as pd
import io

# 1. PAGE CONFIGURATION & THEME
st.set_page_config(
    page_title="TestcaseCraft Pro",
    page_icon="🧪",
    layout="wide"
)

# Professional CSS Styling
st.markdown("""
    <style>
    .main-header { font-size: 3rem; font-weight: 800; color: #1E3A8A; text-align: center; }
    .stButton>button { width: 100%; border-radius: 20px; background: linear-gradient(90deg, #1E3A8A 0%, #3B82F6 100%); color: white; border: none; }
    .stDataFrame { border: 1px solid #e6e9ef; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. SECURE API INITIALIZATION
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    # Configure safety settings to prevent unnecessary blocks
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
    ]
    model = genai.GenerativeModel('gemini-1.5-flash', safety_settings=safety_settings)
else:
    st.error("⚠️ GEMINI_API_KEY not found in Secrets. Please add it to Streamlit Cloud settings.")
    st.stop()

# 3. UI LAYOUT
st.markdown('<p class="main-header">TestcaseCraft Pro</p>', unsafe_allow_html=True)

with st.sidebar:
    st.title("Settings")
    detail_level = st.radio("Granularity", ["High-Level", "Detailed"])
    include_neg = st.toggle("Negative Scenarios", value=True)
    st.info("Engine: Gemini 1.5 Flash ✅")

uploaded_file = st.file_uploader("Upload Business Requirement Document (PDF)", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    text = "".join([p.extract_text() for p in reader.pages])

    if st.button("🚀 Generate Structured Test Matrix"):
        with st.status("Analyzing and Formatting Table...") as status:
            prompt = f"""
            Act as a Senior QA Lead. Analyze this BRD and generate a professional test case matrix.
            OUTPUT ONLY A MARKDOWN TABLE. No conversational text.
            
            Columns: ID, Type (Positive/Negative), Requirement, Description, Expected Result, Priority.
            Detail Level: {detail_level}. Include Negative Scenarios: {include_neg}.
            
            BRD Content: {text[:10000]}
            """
            
            try:
                response = model.generate_content(prompt)
                
                # --- SAFETY CHECK: Prevents ValueError ---
                if not response.candidates or not response.candidates[0].content.parts:
                    status.update(label="Generation Blocked", state="error")
                    st.error("⚠️ The AI response was blocked by safety filters. Try a different document or simplify the prompt.")
                    if response.prompt_feedback:
                        st.warning(f"Reason: {response.prompt_feedback}")
                    st.stop()
                
                status.update(label="Table Generated!", state="complete", expanded=False)
                
                # 4. RESULTS DISPLAY
                st.subheader("📊 Final Test Case Matrix")
                # Using st.markdown to render the AI's markdown table cleanly
                st.markdown(response.text)
                
                # 5. EXPORT FEATURE
                st.download_button(
                    label="📥 Download Matrix (CSV)",
                    data=response.text,
                    file_name="QA_Test_Matrix.csv",
                    mime="text/csv"
                )
                
            except Exception as e:
                st.error(f"An error occurred: {e}")

else:
    st.info("👋 Welcome! Upload a PDF to start generating professional test matrices.")
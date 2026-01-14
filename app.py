import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import pandas as pd
import io

# 1. PAGE CONFIGURATION & BRANDING
st.set_page_config(
    page_title="TestcaseCraft Pro | AI QA Engineer",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. ADVANCED CSS FOR A "SAAS" LOOK
# This overrides default Streamlit styles to create a polished, branded interface.
st.markdown("""
    <style>
    /* Main Background and Font */
    .stApp { background-color: #f8fafc; font-family: 'Inter', sans-serif; }
    
    /* Center and Style Header */
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #1E3A8A 0%, #3B82F6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .tagline {
        font-size: 1.2rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 3rem;
    }

    /* Style Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.5em;
        background: #1E3A8A;
        color: white;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: #3B82F6;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    }

    /* Professional Card Containers */
    div[data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {
        background: white;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. SECURE API INITIALIZATION
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    # Balanced safety settings to allow technical analysis while blocking harmful content
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"}
    ]
    model = genai.GenerativeModel('gemini-1.5-flash', safety_settings=safety_settings)
else:
    st.error("⚠️ GEMINI_API_KEY is missing from Secrets Management.")
    st.stop()

# 4. SIDEBAR - PROFESSIONAL SETTINGS
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2092/2092215.png", width=80)
    st.title("Configuration")
    st.markdown("---")
    
    detail_level = st.select_slider(
        "Analysis Depth",
        options=["Overview", "Standard", "Exhaustive"],
        value="Standard"
    )
    
    include_neg = st.toggle("Negative Path Scenarios", value=True, help="Enable this to test invalid inputs and error handling.")
    
    st.markdown("---")
    st.caption("Engine: Google Gemini 1.5 Flash")
    st.success("System Status: Online")

# 5. MAIN WEBSITE CONTENT
st.markdown('<p class="main-header">TestcaseCraft Pro</p>', unsafe_allow_html=True)
st.markdown('<p class="tagline">Enterprise-grade AI for generating professional Test Case Matrices from BRDs.</p>', unsafe_allow_html=True)

# Layout: Upload on the left, Instructions on the right
col_upload, col_info = st.columns([2, 1], gap="large")

with col_info:
    st.markdown("### 📖 Quick Start")
    st.info("""
    1. **Upload** your Business Requirement Document (PDF).
    2. **Configure** depth and negative scenarios in the sidebar.
    3. **Generate** to receive a structured, organized table.
    4. **Download** the CSV for Jira, Excel, or TestRail.
    """)

with col_upload:
    uploaded_file = st.file_uploader("Drop your PDF document here", type="pdf")

if uploaded_file:
    # PDF Processing
    reader = PdfReader(uploaded_file)
    text = "".join([p.extract_text() for p in reader.pages])
    
    # Action Button
    if st.button("🚀 Start AI Requirement Analysis"):
        # Professional Step-by-Step Feedback
        with st.status("AI Engineer at work...", expanded=True) as status:
            st.write("Parsing document structure...")
            st.write(f"Identifying functional requirements for {detail_level} depth...")
            
            prompt = f"""
            Act as a Senior QA Lead. Analyze the provided BRD content and generate a professional test case matrix.
            OUTPUT ONLY A MARKDOWN TABLE.
            
            Columns: ID, Type (Positive/Negative), Requirement Ref, Description, Expected Result, Priority.
            Depth: {detail_level}. Include Negative Scenarios: {include_neg}.
            
            BRD Content: {text[:10000]}
            """
            
            try:
                response = model.generate_content(prompt)
                
                # SAFETY & NULL CHECK
                if not response.candidates or not response.candidates[0].content.parts:
                    status.update(label="Analysis Blocked", state="error")
                    st.error("The content of this document triggered AI safety filters. Please try another file.")
                    st.stop()

                status.update(label="Analysis Complete!", state="complete", expanded=False)

                # 6. RESULTS SECTION
                st.markdown("---")
                st.subheader("📊 Generated Test Case Matrix")
                
                # Render the Markdown table cleanly
                st.markdown(response.text)
                
                # 7. EXPORT ACTION
                st.divider()
                st.download_button(
                    label="📥 Export Matrix to CSV",
                    data=response.text,
                    file_name="QA_Test_Matrix_Export.csv",
                    mime="text/csv",
                    use_container_width=False
                )
                
            except Exception as e:
                st.error(f"Critical System Error: {e}")
else:
    st.markdown("---")
    st.warning("Please upload a PDF document to activate the AI Analysis engine.")
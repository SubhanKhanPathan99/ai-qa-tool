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

# 2. ADVANCED CSS: REMOVING TOP WHITE SPACE & BACKGROUND ANIMATION
st.markdown("""
    <style>
    /* REMOVE TOP EMPTY SPACE */
    .block-container {
        padding-top: 0rem !important;
        margin-top: -2rem !important;
        max-width: 95%;
    }

    /* ANIMATED PROFESSIONAL BACKGROUND */
    .stApp {
        background: linear-gradient(-45deg, #f1f5f9, #e2e8f0, #cbd5e1, #94a3b8);
        background-size: 400% 400%;
        animation: gradientBG 20s ease infinite;
    }
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* GLASSMORPHISM BOXES - Prevents 'Empty Box' look */
    .stMarkdown div[data-testid="stVerticalBlock"] {
        gap: 0rem;
    }
    
    .glass-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }

    /* HEADER STYLING */
    .hero-title {
        font-size: 3.8rem;
        font-weight: 900;
        color: #0f172a;
        text-align: center;
        letter-spacing: -1px;
        margin-bottom: 0px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. SECURE API INITIALIZATION
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
else:
    st.error("API Key Missing in Secrets.")
    st.stop()

# 4. SIDEBAR - CONTROL PANEL
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2092/2092215.png", width=60)
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

# 5. MAIN HEADER SECTION
# We wrap the title in a container to ensure proper spacing
st.markdown('<p class="hero-title">TestcaseCraft Pro</p>', unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#475569; font-size:1.2rem; margin-bottom:2rem;'>Enterprise-Grade AI Engine for QA Requirement Analysis</p>", unsafe_allow_html=True)

# 6. FILE UPLOAD INTERFACE
# Only show the upload card initially
with st.container():
    uploaded_file = st.file_uploader("Upload BRD (PDF Format)", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    text = "".join([p.extract_text() for p in reader.pages])

    if st.button("🚀 Analyze and Generate Matrix"):
        with st.status("AI Analysis in Progress...", expanded=True) as status:
            st.write("Reading PDF content...")
            
            prompt = f"""
            Act as a Senior QA Lead. Generate a professional test case matrix.
            OUTPUT ONLY A MARKDOWN TABLE.
            
            Style: {test_framework}. Focus: {priority_focus}. Depth: {detail_level}.
            Include Negative: {include_neg}. Include Edge: {include_edge}.
            
            Columns: ID, Type, Requirement Ref, Description, Expected Result, Priority.
            
            BRD: {text[:12000]}
            """
            
            try:
                response = model.generate_content(prompt)
                status.update(label="Analysis Complete!", state="complete", expanded=False)

                # 7. DYNAMIC RESULTS - Only appears when ready
                st.markdown("---")
                st.subheader("📊 Generated Test Matrix")
                
                # Render table
                st.markdown(response.text)
                
                # EXPORT ACTION
                st.download_button(
                    label="📥 Download CSV",
                    data=response.text,
                    file_name="QA_Matrix.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"Error: {e}")
else:
    # This info box replaces the "Empty Box" until a file is uploaded
    st.info("👋 Welcome! Please upload your PDF document to activate the analysis engine.")
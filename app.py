import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import google.api_core.exceptions
import io

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="TestcaseCraft Pro | Enterprise QA",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. ADVANCED CSS: ENTERPRISE UI & GAP REMOVAL
st.markdown("""
    <style>
    /* HIDE TOP ICONS & MANAGE APP BUTTON */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display: none;}
    #MainMenu {visibility: hidden;}
    [data-testid="stStatusWidget"] {visibility: hidden;}
    
    /* HIDE 'MANAGE APP' BUTTON AT BOTTOM RIGHT */
    button[data-testid="manage-app-button"] {
        display: none !important;
    }

    /* REMOVE TOP WHITESPACE (ABOVE TITLE) */
    .block-container {
        padding-top: 0rem !important;
        margin-top: -3.5rem !important; /* Pulls title to the very top */
        max-width: 95%;
    }

    /* FIX SIDEBAR GAPS (BETWEEN CONTROL PANEL & SETTINGS) */
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 0.5rem !important;
    }
    .st-emotion-cache-16idsys p {
        margin-bottom: -1rem !important; /* Reduces gap after labels */
    }
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: 0.5rem !important; /* Tightens the vertical space in sidebar */
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

    /* GLASSMORPHISM BOXES */
    div[data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {
        background: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    /* CUSTOM TITLE STYLING */
    .hero-title {
        font-size: 3.2rem;
        font-weight: 900;
        color: #1e293b;
        text-align: center;
        margin-bottom: 0px;
    }

    /* FOOTER DISCLAIMER STYLING */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: transparent;
        color: #64748b;
        text-align: center;
        font-size: 0.8rem;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. SECURE API INITIALIZATION
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-flash-latest')
else:
    st.error("API Key Missing in Secrets Management.")
    st.stop()

# 4. SIDEBAR - CLEAN CONTROL PANEL
with st.sidebar:
    st.title("Control Panel")
    # Reducing gap manually by avoiding extra dividers or markdown if not needed
    st.subheader("🛠️ Core Settings")
    detail_level = st.select_slider("Analysis Depth", options=["Standard", "Detailed", "Exhaustive"])
    
    st.subheader("🎯 Test Strategy")
    test_framework = st.selectbox("Preferred Framework", ["Standard Manual", "Cucumber/Gherkin", "PyTest/Robot"])
    priority_focus = st.multiselect("Priority Focus", ["Security", "UI/UX", "API", "Performance"], default=["UI/UX"])
    
    st.subheader("🧪 Scenarios")
    include_neg = st.toggle("Negative Scenarios", value=True)
    include_edge = st.toggle("Edge Case Analysis", value=True)
    st.success("System: Ready ✅")

# 5. MAIN WEBSITE TITLE
st.markdown('<h1 class="hero-title">TestcaseCraft Pro</h1>', unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#475569; font-size:1rem; margin-bottom:1rem;'>Enterprise-Grade AI Engine for QA Requirement Analysis</p>", unsafe_allow_html=True)

# 6. CACHED GENERATION
@st.cache_data(show_spinner=False, ttl=3600)
def generate_cached_matrix(pdf_text, detail, framework, neg, edge, focus):
    prompt = f"Act as a QA Lead. Generate a markdown table matrix for this BRD. Style: {framework}. Focus: {focus}. Depth: {detail}. Include Negative: {neg}. Edge: {edge}. Content: {pdf_text[:12000]}"
    try:
        return model.generate_content(prompt)
    except google.api_core.exceptions.ResourceExhausted:
        return "QUOTA_ERROR"

# 7. MAIN WORKSPACE
uploaded_file = st.file_uploader("Upload BRD (PDF)", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    text = "".join([p.extract_text() for p in reader.pages])

    if st.button("🚀 Analyze and Generate Matrix"):
        with st.status("AI Analysis in Progress...", expanded=True) as status:
            response = generate_cached_matrix(text, detail_level, test_framework, include_neg, include_edge, priority_focus)
            
            if response == "QUOTA_ERROR":
                st.error("⚠️ Quota Exceeded. Please wait 60 seconds.")
                st.stop()
            
            status.update(label="Analysis Complete!", state="complete", expanded=False)

        st.markdown("### 📊 Generated Test Matrix")
        st.markdown(response.text)
        st.download_button("📥 Export Matrix to CSV", response.text, "QA_Matrix.csv", "text/csv")

else:
    st.info("👋 Welcome! Please upload your PDF document to activate the analysis engine.")

# 8. FOOTER DISCLAIMER
st.markdown(
    '<div class="footer">© 2026 TestcaseCraft Pro. All rights reserved. | Developed by Subhan Khan Pathan</div>', 
    unsafe_allow_html=True
)
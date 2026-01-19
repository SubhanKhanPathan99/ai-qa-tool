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
    /* HIDE TOP ICONS (Deploy, GitHub, Menu) */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display: none;}
    
    /* REMOVE TOP WHITESPACE & SIDEBAR GAPS */
    .block-container {
        padding-top: 0rem !important;
        margin-top: -1.5rem !important;
        max-width: 95%;
    }
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

    /* GLASSMORPHISM BOXES */
    div[data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {
        background: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 30px;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    /* CUSTOM TITLE STYLING */
    .hero-title {
        font-size: 3.5rem;
        font-weight: 900;
        color: #1e293b;
        text-align: center;
        margin-bottom: 0px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. SECURE API INITIALIZATION
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Using the stable latest alias to avoid 'NotFound' errors
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
else:
    st.error("API Key Missing in Secrets Management.")
    st.stop()

# 4. SIDEBAR - CLEAN CONTROL PANEL
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

# 5. MAIN WEBSITE TITLE
st.markdown('<h1 class="hero-title">TestcaseCraft Pro</h1>', unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#475569; font-size:1.1rem;'>Professional AI Engine for QA Requirement Analysis</p>", unsafe_allow_html=True)

# 6. CACHED GENERATION (Fixes 429 Quota Error & Saves Quota)
@st.cache_data(show_spinner=False, ttl=3600)
def generate_cached_matrix(pdf_text, detail, framework, neg, edge, focus):
    """Stores results for 1 hour. Repeat clicks won't waste API quota."""
    prompt = f"""
    Act as a Senior QA Lead. Generate a professional test case matrix.
    OUTPUT ONLY A MARKDOWN TABLE.
    Style: {framework}. Focus: {focus}. Depth: {detail}.
    Include Negative: {neg}. Include Edge: {edge}.
    Columns: ID, Type, Requirement Ref, Description, Expected Result, Priority.
    BRD CONTENT: {pdf_text[:12000]}
    """
    try:
        return model.generate_content(prompt)
    except google.api_core.exceptions.ResourceExhausted:
        return "QUOTA_ERROR"

# 7. MAIN WORKSPACE
uploaded_file = st.file_uploader("Upload Business Requirement Document (PDF)", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    text = "".join([p.extract_text() for p in reader.pages])

    if st.button("🚀 Analyze and Generate Matrix"):
        with st.status("AI Analysis in Progress...", expanded=True) as status:
            response = generate_cached_matrix(text, detail_level, test_framework, include_neg, include_edge, priority_focus)
            
            if response == "QUOTA_ERROR":
                status.update(label="Quota Exceeded", state="error")
                st.error("⚠️ Free Tier limit reached. Please wait 60 seconds and try again.")
                st.stop()
            
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
else:
    st.info("👋 Welcome! Please upload your PDF document to activate the analysis engine.")
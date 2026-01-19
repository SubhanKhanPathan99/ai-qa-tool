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

# 2. ADVANCED CSS: BURGUNDY THEME, GAP REMOVAL & HIDING MANAGE APP
st.markdown("""
    <style>
    /* HIDE TOP ICONS & STREAMLIT FOOTER/TOOLBAR */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display: none;}
    #MainMenu {visibility: hidden;}
    
    /* CRITICAL: HIDES THE 'MANAGE APP' BUTTON FOR END USERS */
    [data-testid="stStatusWidget"] {display: none !important;}
    footer {display: none !important;}
    .viewerBadge_container__1QSob {display: none !important;}
    button[data-testid="manage-app-button"] {display: none !important;}

    /* REMOVE TOP WHITESPACE (ABOVE TITLE) */
    .block-container {
        padding-top: 0rem !important;
        margin-top: -3.5rem !important; 
        max-width: 95%;
    }

    /* FIX SIDEBAR GAPS */
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 0.5rem !important;
    }
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: 0.5rem !important;
    }

    /* PROFESSIONAL BURGUNDY GRADIENT BACKGROUND */
    .stApp {
        background: linear-gradient(-45deg, #4a0404, #630d0d, #800000, #a52a2a);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
    }
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* GLASSMORPHISM BOXES (ADJUSTED FOR DARK THEME) */
    div[data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .hero-title {
        font-size: 3.2rem;
        font-weight: 900;
        color: #ffffff;
        text-align: center;
        margin-bottom: 0px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }

    .hero-tagline {
        text-align: center; 
        color: #fca5a5; 
        font-size: 1rem; 
        margin-bottom: 1rem;
    }

    /* FOOTER WITH SOCIAL LINKS */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: rgba(0, 0, 0, 0.3);
        color: #ffffff;
        text-align: center;
        font-size: 0.85rem;
        padding: 12px;
        z-index: 100;
    }
    .footer a {
        color: #fca5a5;
        text-decoration: none;
        margin: 0 10px;
        font-weight: bold;
    }
    .footer a:hover {
        color: #ffffff;
        text-decoration: underline;
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
    st.title("Control Panel")
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
st.markdown('<p class="hero-tagline">Enterprise AI Engine for QA Requirement Analysis</p>', unsafe_allow_html=True)

# 6. CACHED GENERATION
@st.cache_data(show_spinner=False, ttl=3600)
def generate_cached_matrix(pdf_text, detail, framework, neg, edge, focus):
    prompt = f"QA Lead: Generate a markdown matrix for this BRD. Style: {framework}. Focus: {focus}. Depth: {detail}. Include Negative: {neg}. Edge: {edge}. Content: {pdf_text[:12000]}"
    try:
        return model.generate_content(prompt)
    except Exception as e:
        return f"ERROR: {str(e)}"

# 7. MAIN WORKSPACE
uploaded_file = st.file_uploader("Upload BRD (PDF)", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    text = "".join([p.extract_text() for p in reader.pages])

    if st.button("🚀 Analyze and Generate Matrix"):
        with st.status("AI Analysis in Progress...", expanded=True) as status:
            response = generate_cached_matrix(text, detail_level, test_framework, include_neg, include_edge, priority_focus)
            
            if "ERROR" in str(response):
                st.error(f"⚠️ System Error: {response}")
                st.stop()
            
            status.update(label="Analysis Complete!", state="complete", expanded=False)

        st.markdown("### 📊 Generated Test Matrix")
        st.markdown(response.text)
        st.download_button("📥 Export Matrix to CSV", response.text, "QA_Matrix.csv", "text/csv")
else:
    st.info("👋 Welcome! Please upload your PDF document to activate the analysis engine.")

# 8. FOOTER WITH PERSONAL LINKS
st.markdown(
    f"""
    <div class="footer">
        © 2026 TestcaseCraft Pro. All rights reserved. | Developed by Subhan Khan Pathan 
        <a href="https://www.linkedin.com/in/pathan-subhan-khan-256547147/" target="_blank">🔗 LinkedIn</a>
        <a href="https://subhankhanpathan99.github.io/" target="_blank">📂 Portfolio</a>
    </div>
    """, 
    unsafe_allow_html=True
)
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

# 2. ADVANCED CSS: CUSTOM COLOR, GAP FIXES & FLOATING SOCIALS
st.markdown("""
    <style>
    /* HIDE ALL STREAMLIT DEVELOPER OVERLAYS */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display: none;}
    #MainMenu {visibility: hidden;}
    [data-testid="stStatusWidget"] {display: none !important;}
    
    /* ABSOLUTE HIDE FOR 'MANAGE APP' AND VIEWER BADGE */
    button[data-testid="manage-app-button"] {display: none !important;}
    .viewerBadge_container__1QSob {display: none !important;}
    .st-emotion-cache-zq5wms {display: none !important;}

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
        gap: 0.8rem !important;
    }

    /* CUSTOM BACKGROUND COLOR: #A0A300 */
    .stApp {
        background-color: #A0A300;
        background-attachment: fixed;
    }

    /* GLASSMORPHISM BOXES - High contrast for the new background */
    div[data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(0, 0, 0, 0.1);
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .hero-title {
        font-size: 3.2rem;
        font-weight: 900;
        color: #ffffff;
        text-align: center;
        margin-bottom: 0px;
        text-shadow: 2px 2px 10px rgba(0,0,0,0.2);
    }

    /* FLOATING ACTION BUTTONS (SOCIALS) WITH SPACING */
    .float-container {
        position: fixed;
        bottom: 30px;
        right: 30px;
        z-index: 1000;
        display: flex;
        flex-direction: row; 
        gap: 20px; /* Increased space between buttons */
    }

    .float-btn {
        padding: 12px 25px;
        border-radius: 50px;
        color: white !important;
        text-decoration: none;
        font-weight: bold;
        font-size: 14px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.4);
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
    }

    .float-btn:hover {
        transform: scale(1.1);
        color: white;
    }

    .linkedin-btn { background-color: #0077b5; }
    .portfolio-btn { background-color: #24292e; }

    /* COPYRIGHT TEXT */
    .copyright {
        position: fixed;
        bottom: 30px;
        left: 30px;
        color: #ffffff;
        font-weight: 500;
        font-size: 0.9rem;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.2);
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

# 4. SIDEBAR - CONTROL PANEL (FORCED LEFT BAR)
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
    st.divider()
    st.success("Engine Status: Online ✅")

# 5. MAIN WEBSITE TITLE
st.markdown('<h1 class="hero-title">TestcaseCraft Pro</h1>', unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#ffffff; font-size:1.1rem; font-weight: 500;'>Enterprise AI Engine for QA Requirement Analysis</p>", unsafe_allow_html=True)

# 6. CACHED GENERATION (Prevents 429 Errors)
@st.cache_data(show_spinner=False, ttl=3600)
def generate_cached_matrix(pdf_text, detail, framework, neg, edge, focus):
    prompt = f"QA Lead: Generate a markdown matrix for this BRD. Style: {framework}. Focus: {focus}. Depth: {detail}. Include Negative: {neg}. Edge: {edge}. Content: {pdf_text[:12000]}"
    try:
        return model.generate_content(prompt)
    except Exception as e:
        return f"ERROR: {str(e)}"

# 7. MAIN WORKSPACE
uploaded_file = st.file_uploader("Upload Business Requirement Document (PDF)", type="pdf")

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

# 8. FLOATING SOCIAL BUTTONS & COPYRIGHT
st.markdown(
    f"""
    <div class="copyright">© 2026 | Subhan Khan Pathan</div>
    <div class="float-container">
        <a href="https://www.linkedin.com/in/pathan-subhan-khan-256547147/" class="float-btn linkedin-btn" target="_blank">LinkedIn</a>
        <a href="https://subhankhanpathan99.github.io/" class="float-btn portfolio-btn" target="_blank">Portfolio</a>
    </div>
    """, 
    unsafe_allow_html=True
)
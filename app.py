import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import google.api_core.exceptions
import io

# 1. PAGE CONFIGURATION - MANDATORY FOR SIDEBAR
st.set_page_config(
    page_title="TestcaseCraft Pro | Enterprise QA",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded" # This FORCES the left bar to stay open
)

# 2. ADVANCED CSS: COLOR #27F5C2 & ALIGNMENT FIXES
st.markdown("""
    <style>
    /* HIDE DEVELOPER TOOLS & MANAGE APP */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display: none;}
    #MainMenu {visibility: hidden;}
    [data-testid="stStatusWidget"] {display: none !important;}
    button[data-testid="manage-app-button"] {display: none !important;}
    .st-emotion-cache-zq5wms {display: none !important;}

    /* BACKGROUND COLOR #27F5C2 */
    .stApp {
        background-color: #27F5C2;
    }

    /* REMOVE GAPS ABOVE TITLE */
    .block-container {
        padding-top: 0rem !important;
        margin-top: -3.5rem !important; 
        max-width: 95%;
    }

    /* GLASSMORPHISM WORKSPACE */
    div[data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(0, 0, 0, 0.05);
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 900;
        color: #1e293b;
        text-align: center;
        margin-bottom: 0px;
    }

    /* PERFECTLY ALIGNED BOTTOM BAR */
    .fixed-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(5px);
        display: flex;
        justify-content: space-between; /* Pushes text left, buttons right */
        align-items: center;
        padding: 10px 40px;
        z-index: 9999;
    }

    .footer-text {
        color: #1e293b;
        font-weight: 600;
        font-size: 0.95rem;
    }

    .footer-buttons {
        display: flex;
        gap: 15px; /* PROPER SPACE BETWEEN BUTTONS */
    }

    .btn-link {
        padding: 8px 20px;
        border-radius: 50px;
        color: white !important;
        text-decoration: none;
        font-weight: bold;
        font-size: 14px;
        transition: transform 0.2s ease;
    }

    .btn-link:hover {
        transform: scale(1.05);
        color: white;
    }

    .li-btn { background-color: #0077b5; }
    .pf-btn { background-color: #333333; }
    </style>
    """, unsafe_allow_html=True)

# 3. SECURE API INITIALIZATION
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
else:
    st.error("API Key Missing in Secrets.")
    st.stop()

# 4. SIDEBAR - CONTROL PANEL (FIXED)
# This MUST be outside any conditional blocks to always show
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
    st.success("System Ready ✅")

# 5. MAIN CONTENT
st.markdown('<h1 class="hero-title">TestcaseCraft Pro</h1>', unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#1e293b; font-weight:500;'>Enterprise AI Engine for QA Requirement Analysis</p>", unsafe_allow_html=True)

# 6. CACHED GENERATION
@st.cache_data(show_spinner=False, ttl=3600)
def generate_cached_matrix(pdf_text, detail, framework, neg, edge, focus):
    prompt = f"QA Lead: Generate a markdown matrix for this BRD. Style: {framework}. Focus: {focus}. Depth: {detail}. Include Negative: {neg}. Edge: {edge}. Content: {pdf_text[:12000]}"
    try:
        return model.generate_content(prompt)
    except Exception as e:
        return f"ERROR: {str(e)}"

# 7. WORKSPACE
uploaded_file = st.file_uploader("Upload BRD (PDF Format)", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    text = "".join([p.extract_text() for p in reader.pages])

    if st.button("🚀 Analyze and Generate Matrix"):
        with st.status("AI Analysis in Progress...", expanded=True) as status:
            response = generate_cached_matrix(text, detail_level, test_framework, include_neg, include_edge, priority_focus)
            if "ERROR" in str(response):
                st.error("⚠️ System Error. Check API/Quota.")
                st.stop()
            status.update(label="Analysis Complete!", state="complete", expanded=False)

        st.markdown("### 📊 Generated Test Matrix")
        st.markdown(response.text)
        st.download_button("📥 Export Matrix to CSV", response.text, "QA_Matrix.csv", "text/csv")
else:
    st.info("👋 Welcome! Please upload your PDF document to activate the analysis engine.")

# 8. THE ALIGNED FOOTER BAR
st.markdown(
    f"""
    <div class="fixed-footer">
        <div class="footer-text">© 2026 | Subhan Khan Pathan</div>
        <div class="footer-buttons">
            <a href="https://www.linkedin.com/in/pathan-subhan-khan-256547147/" class="btn-link li-btn" target="_blank">LinkedIn</a>
            <a href="https://subhankhanpathan99.github.io/" class="btn-link pf-btn" target="_blank">Portfolio</a>
        </div>
    </div>
    """, 
    unsafe_allow_html=True
)
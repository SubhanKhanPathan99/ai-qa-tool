import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import google.api_core.exceptions
import io

# 1. PAGE CONFIGURATION - RESTORING THE LEFT BAR
st.set_page_config(
    page_title="TestcaseCraft Pro | Enterprise QA",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded" # FORCES SIDEBAR TO SHOW
)

# 2. ADVANCED CSS: #27F5C2 THEME & ALIGNMENT FIXES
st.markdown("""
    <style>
    /* HIDE DEVELOPER TOOLS */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display: none;}
    #MainMenu {visibility: hidden;}
    [data-testid="stStatusWidget"] {display: none !important;}
    
    /* HIDE MANAGE APP BUTTON PERMANENTLY */
    button[data-testid="manage-app-button"] {display: none !important;}
    .st-emotion-cache-zq5wms {display: none !important;}

    /* BACKGROUND COLOR #27F5C2 */
    .stApp {
        background-color: #27F5C2;
    }

    /* REMOVE TOP GAPS */
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

    /* FIXED BOTTOM BAR FOR COPYRIGHT & BUTTONS */
    .bottom-bar {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        padding: 15px 40px;
        display: flex;
        justify-content: space-between; /* Pushes Copyright left, Buttons right */
        align-items: center;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(5px);
        z-index: 9999;
    }

    .copyright-text {
        color: #1e293b;
        font-weight: 600;
        font-size: 0.95rem;
    }

    .social-group {
        display: flex;
        gap: 15px; /* PROPER SPACE BETWEEN BUTTONS */
    }

    .float-btn {
        padding: 10px 22px;
        border-radius: 50px;
        color: white !important;
        text-decoration: none;
        font-weight: bold;
        font-size: 14px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }

    .float-btn:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 15px rgba(0,0,0,0.3);
    }

    .linkedin-btn { background-color: #0077b5; }
    .portfolio-btn { background-color: #24292e; }
    </style>
    """, unsafe_allow_html=True)

# 3. SECURE API INITIALIZATION
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
else:
    st.error("API Key Missing in Secrets Management.")
    st.stop()

# 4. SIDEBAR - CONTROL PANEL (RESTORED SECTION)
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
    st.success("System: Online ✅")

# 5. MAIN CONTENT
st.markdown('<h1 class="hero-title">TestcaseCraft Pro</h1>', unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#1e293b; font-weight:500; font-size:1.1rem;'>Enterprise AI Engine for QA Requirement Analysis</p>", unsafe_allow_html=True)

# 6. CACHED GENERATION (Fixes 429 Error)
@st.cache_data(show_spinner=False, ttl=3600)
def generate_cached_matrix(pdf_text, detail, framework, neg, edge, focus):
    prompt = f"QA Lead: Generate a markdown matrix for this BRD. Style: {framework}. Focus: {focus}. Depth: {detail}. Include Negative: {neg}. Edge: {edge}. Content: {pdf_text[:12000]}"
    try:
        return model.generate_content(prompt)
    except Exception as e:
        return f"ERROR: {str(e)}"

# 7. MAIN WORKSPACE
uploaded_file = st.file_uploader("Upload BRD (PDF Format)", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    text = "".join([p.extract_text() for p in reader.pages])

    if st.button("🚀 Analyze and Generate Matrix"):
        with st.status("AI Analysis in Progress...", expanded=True) as status:
            response = generate_cached_matrix(text, detail_level, test_framework, include_neg, include_edge, priority_focus)
            
            if "ERROR" in str(response):
                st.error(f"⚠️ Quota Reached or System Error. Please wait 60s.")
                st.stop()
            
            status.update(label="Analysis Complete!", state="complete", expanded=False)

        st.markdown("### 📊 Generated Test Matrix")
        st.markdown(response.text)
        st.download_button("📥 Export Matrix to CSV", response.text, "QA_Matrix.csv", "text/csv")
else:
    st.info("👋 Welcome! Please upload your PDF document to activate the analysis engine.")

# 8. ALIGNED BOTTOM BAR (Copyright + Socials)
st.markdown(
    f"""
    <div class="bottom-bar">
        <div class="copyright-text">© 2026 | Subhan Khan Pathan</div>
        <div class="social-group">
            <a href="https://www.linkedin.com/in/pathan-subhan-khan-256547147/" class="float-btn linkedin-btn" target="_blank">LinkedIn</a>
            <a href="https://subhankhanpathan99.github.io/" class="float-btn portfolio-btn" target="_blank">Portfolio</a>
        </div>
    </div>
    """, 
    unsafe_allow_html=True
)
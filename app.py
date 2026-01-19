import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import google.api_core.exceptions
import io

# 1. FORCED PAGE CONFIGURATION
st.set_page_config(
    page_title="TestcaseCraft Pro | Enterprise QA",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded" 
)

# 2. ADVANCED CSS: COLOR #27F5C2 & ALIGNMENT ENGINE
st.markdown("""
    <style>
    /* HIDE DEVELOPER OVERLAYS */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display: none;}
    #MainMenu {visibility: hidden;}
    [data-testid="stStatusWidget"] {display: none !important;}
    button[data-testid="manage-app-button"] {display: none !important;}

    /* THEME COLOR #27F5C2 */
    .stApp { background-color: #27F5C2; }

    /* REMOVE ALL TOP GAPS */
    .block-container {
        padding-top: 0rem !important;
        margin-top: -4rem !important; 
        max-width: 95%;
    }

    /* GLASSMORPHISM MAIN CARDS */
    div[data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 30px;
        border: 1px solid rgba(0, 0, 0, 0.05);
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 900;
        color: #1e293b;
        text-align: center;
        margin-bottom: 0px;
    }

    /* THE FINAL ALIGNED FOOTER (FIXED) */
    .footer-container {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 40px;
        z-index: 9999;
        border-top: 1px solid rgba(0,0,0,0.1);
    }

    .footer-copyright {
        color: #1e293b;
        font-weight: 700;
        font-size: 1rem;
    }

    .footer-socials { display: flex; gap: 15px; }

    .social-link {
        padding: 10px 24px;
        border-radius: 50px;
        color: white !important;
        text-decoration: none;
        font-weight: bold;
        font-size: 14px;
        transition: transform 0.2s ease;
    }

    .social-link:hover { transform: scale(1.05); }
    .li-color { background-color: #0077b5; }
    .pf-color { background-color: #333333; }
    </style>
    """, unsafe_allow_html=True)

# 3. SECURE API INITIALIZATION
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
else:
    st.error("API Key Missing in Streamlit Secrets.")
    st.stop()

# 4. SIDEBAR - CONTROL PANEL (RESTORED)
with st.sidebar:
    st.title("Control Panel")
    st.divider()
    st.success("System: Ready ✅")
    st.info("Choose your analysis settings below or in the main window.")

# 5. MAIN CONTENT
st.markdown('<h1 class="hero-title">TestcaseCraft Pro</h1>', unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#1e293b; font-weight:600; font-size:1.1rem;'>Professional AI Engine for QA Requirement Analysis</p>", unsafe_allow_html=True)

# 6. CACHED GENERATION
@st.cache_data(show_spinner=False, ttl=3600)
def generate_cached_matrix(pdf_text, detail, framework, neg, edge, focus):
    prompt = f"QA Lead: Generate a markdown matrix for this BRD. Style: {framework}. Focus: {focus}. Depth: {detail}. Include Negative: {neg}. Edge: {edge}. Content: {pdf_text[:12000]}"
    try:
        return model.generate_content(prompt)
    except Exception as e:
        return f"ERROR: {str(e)}"

# 7. WORKSPACE
uploaded_file = st.file_uploader("Step 1: Upload BRD (PDF Format)", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    text = "".join([p.extract_text() for p in reader.pages])

    st.markdown("### Step 2: Configure Your Test Strategy")
    col1, col2 = st.columns(2)
    
    with col1:
        priority_focus = st.multiselect("🎯 Priority Focus Areas", 
                                        ["UI/UX", "Security", "API/Backend", "Performance", "Database"], 
                                        default=["UI/UX"])
        test_framework = st.selectbox("📖 Output Format (BDD/Manual)", 
                                      ["Standard Manual", "BDD (Cucumber/Gherkin)", "PyTest Framework"])
        detail_level = st.select_slider("🔍 Analysis Depth", options=["Standard", "Detailed", "Exhaustive"])

    with col2:
        include_neg = st.toggle("🧪 Include Negative Test Cases", value=True)
        include_edge = st.toggle("⚡ Include Edge Case Analysis", value=True)
        st.info("💡 BDD format will generate 'Given-When-Then' scenarios.")

    # FIX: THE PLACEHOLDER THAT REMOVES THE EMPTY BOX
    placeholder = st.empty()
    
    if st.button("🚀 Analyze and Generate Matrix"):
        # We put the status inside the placeholder
        with placeholder.container():
            with st.status("AI Analysis in Progress...") as status:
                response = generate_cached_matrix(text, detail_level, test_framework, include_neg, include_edge, priority_focus)
                if "ERROR" in str(response):
                    st.error("⚠️ System Error or Quota Reached.")
                    st.stop()
                status.update(label="Analysis Complete!", state="complete")
        
        # ONCE DONE, WE CLEAR THE PLACEHOLDER ENTIRELY
        placeholder.empty()

        # NOW SHOW RESULTS
        st.markdown("---")
        st.subheader("📊 Generated Test Matrix")
        st.markdown(response.text)
        st.download_button("📥 Export Matrix to CSV", response.text, "QA_Matrix.csv", "text/csv")
else:
    st.info("👋 Welcome! Please upload your PDF document to activate the analysis engine.")

# 8. THE CORRECTLY ALIGNED FOOTER BAR
st.markdown(
    f"""
    <div class="footer-container">
        <div class="footer-copyright">© 2026 | Subhan Khan Pathan</div>
        <div class="footer-socials">
            <a href="https://www.linkedin.com/in/pathan-subhan-khan-256547147/" class="social-link li-color" target="_blank">LinkedIn</a>
            <a href="https://subhankhanpathan99.github.io/" class="social-link pf-color" target="_blank">Portfolio</a>
        </div>
    </div>
    """, 
    unsafe_allow_html=True
)
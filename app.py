import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import google.api_core.exceptions
import time

# 1. PAGE CONFIG & THEME
st.set_page_config(page_title="TestcaseCraft Pro", page_icon="🧪", layout="wide")

# 2. CSS RESET: Fixes Sidebar Gaps, Blank Spaces, and Adds Animation
st.markdown("""
    <style>
    /* Force Title and Sidebar to the absolute top */
    .block-container { padding-top: 0rem !important; margin-top: -2rem !important; }
    [data-testid="stSidebar"] > div:first-child { padding-top: 0rem !important; }
    
    /* Remove the 'Empty Box' look in Sidebar */
    [data-testid="stSidebarNav"] { display: none; }
    div[data-testid="stVerticalBlock"] > div { margin-top: -1rem; }

    /* Professional Animated Background */
    .stApp {
        background: linear-gradient(-45deg, #f1f5f9, #e2e8f0, #cbd5e1, #94a3b8);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
    }
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Hero Title Style */
    .hero-title { font-size: 3.5rem; font-weight: 900; color: #0f172a; text-align: center; margin: 0; }
    </style>
    """, unsafe_allow_html=True)

# 3. API INITIALIZATION
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
else:
    st.error("API Key Missing in Secrets Management.")
    st.stop()

# 4. SIDEBAR - CONTROL PANEL (Starts immediately to avoid empty boxes)
with st.sidebar:
    st.title("Control Panel")
    st.divider()
    st.subheader("🛠️ Settings")
    detail_level = st.select_slider("Analysis Depth", options=["Standard", "Detailed", "Exhaustive"])
    test_framework = st.selectbox("Framework", ["Standard Manual", "Cucumber/Gherkin", "PyTest"])
    include_neg = st.toggle("Negative Scenarios", value=True)
    st.divider()
    st.success("System: Ready ✅")

# 5. MAIN CONTENT
st.markdown('<h1 class="hero-title">TestcaseCraft Pro</h1>', unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#475569;'>Enterprise AI for QA Requirement Analysis</p>", unsafe_allow_html=True)

# 6. CACHED GENERATION FUNCTION (Saves your Quota)
@st.cache_data(show_spinner=False)
def get_ai_response(pdf_text, detail, framework, neg_toggle):
    prompt = f"Act as a QA Lead. Generate a markdown table matrix for this BRD. Style: {framework}. Depth: {detail}. Include Negative: {neg_toggle}. BRD: {pdf_text[:10000]}"
    return model.generate_content(prompt)

uploaded_file = st.file_uploader("Upload BRD (PDF)", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    text = "".join([p.extract_text() for p in reader.pages])

    if st.button("🚀 Analyze Requirements"):
        try:
            with st.status("AI Analysis in Progress...") as status:
                # Use the cached function to avoid 429 errors on repeat runs
                response = get_ai_response(text, detail_level, test_framework, include_neg)
                
                if not response.candidates:
                    st.error("AI Response Blocked. Try a different file.")
                    st.stop()
                    
                status.update(label="Analysis Complete!", state="complete", expanded=False)

            st.markdown("### 📊 Generated Test Matrix")
            st.markdown(response.text)
            st.download_button("📥 Download CSV", response.text, "QA_Matrix.csv", "text/csv")

        except google.api_core.exceptions.ResourceExhausted:
            st.error("⚠️ AI Quota Exceeded (Error 429).")
            st.info("The Free Tier limit is 15 requests per minute. Please wait 60 seconds and try again.")
        except Exception as e:
            st.error(f"System Error: {e}")
else:
    st.info("👋 Welcome! Please upload your PDF document to begin.")
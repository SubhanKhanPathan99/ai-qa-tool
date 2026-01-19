import streamlit as st
from PyPDF2 import PdfReader
from google import genai
import google.api_core.exceptions
import time

# =========================================================
# 1. PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="TestcaseCraft Pro | Enterprise QA",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# 2. CSS (UNCHANGED)
# =========================================================
st.markdown("""
<style>
header, footer, #MainMenu {visibility: hidden;}
.stApp { background-color: #27F5C2; }
.block-container { margin-top: -4rem; max-width: 95%; }
.hero-title { font-size: 3.5rem; font-weight: 900; text-align: center; }
.footer-container {
    position: fixed; bottom: 0; width: 100%;
    background: rgba(255,255,255,0.9);
    display: flex; justify-content: space-between;
    padding: 12px 40px;
}
.social-link { padding: 10px 24px; color: white; font-weight: bold; }
.li-color { background:#0077b5; }
.pf-color { background:#333; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 3. GEMINI CLIENT (NEW SDK – FIX)
# =========================================================
if "GEMINI_API_KEY" not in st.secrets:
    st.error("❌ GEMINI_API_KEY missing in Streamlit secrets")
    st.stop()

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

MODEL_NAME = "gemini-1.5-flash"  # ✅ WORKING

# =========================================================
# 4. SIDEBAR
# =========================================================
with st.sidebar:
    st.title("Control Panel")
    st.success("Account Status: Tier 1 ✅")

# =========================================================
# 5. HEADER
# =========================================================
st.markdown('<h1 class="hero-title">TestcaseCraft Pro</h1>', unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;font-weight:600;'>Professional AI Engine for QA Requirement Analysis</p>",
    unsafe_allow_html=True
)

# =========================================================
# 6. CACHED GENERATION (NEW CALL STYLE)
# =========================================================
@st.cache_data(show_spinner=False, ttl=3600)
def generate_cached_matrix(pdf_text, detail, framework, neg, edge, focus):

    prompt = f"""
You are a Senior QA Lead.

Generate a professional QA test case matrix in MARKDOWN.

Framework: {framework}
Depth: {detail}
Priority Areas: {', '.join(focus)}
Include Negative Cases: {neg}
Include Edge Cases: {edge}

BRD CONTENT:
{pdf_text[:12000]}
"""

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )
            return response.text

        except google.api_core.exceptions.ResourceExhausted:
            if attempt < 2:
                time.sleep(5)
                continue
            return "QUOTA_EXCEEDED"

        except Exception as e:
            return f"ERROR: {str(e)}"

# =========================================================
# 7. WORKSPACE
# =========================================================
uploaded_file = st.file_uploader("Step 1: Upload BRD (PDF)", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    text = "".join([p.extract_text() or "" for p in reader.pages])

    st.markdown("### Step 2: Configure Your Test Strategy")

    col1, col2 = st.columns(2)

    with col1:
        priority_focus = st.multiselect(
            "🎯 Priority Focus Areas",
            ["UI/UX", "Security", "API/Backend", "Performance"],
            default=["UI/UX"]
        )
        test_framework = st.selectbox(
            "📖 Output Format",
            ["Standard Manual", "BDD (Cucumber/Gherkin)"]
        )
        detail_level = st.select_slider(
            "🔍 Analysis Depth",
            ["Standard", "Detailed", "Exhaustive"]
        )

    with col2:
        include_neg = st.toggle("🧪 Include Negative Cases", True)
        include_edge = st.toggle("⚡ Include Edge Analysis", True)

    if st.button("🚀 Analyze and Generate Matrix"):
        with st.status("AI Analysis in Progress..."):
            response = generate_cached_matrix(
                text, detail_level, test_framework,
                include_neg, include_edge, priority_focus
            )

            if response == "QUOTA_EXCEEDED":
                st.error("⚠️ Quota limit reached. Please wait.")
                st.stop()

            if response.startswith("ERROR"):
                st.error(response)
                st.stop()

        st.markdown("---")
        st.subheader("📊 Generated Test Matrix")
        st.markdown(response)

        st.download_button(
            "📥 Export Matrix",
            response,
            "QA_Matrix.md",
            "text/markdown"
        )
else:
    st.info("👋 Upload a BRD PDF to start.")

# =========================================================
# 8. FOOTER
# =========================================================
st.markdown("""
<div class="footer-container">
    <div>© 2026 | Subhan Khan Pathan</div>
    <div>
        <a class="social-link li-color" href="https://www.linkedin.com/in/pathan-subhan-khan-256547147/">LinkedIn</a>
        <a class="social-link pf-color" href="https://subhankhanpathan99.github.io/">Portfolio</a>
    </div>
</div>
""", unsafe_allow_html=True)

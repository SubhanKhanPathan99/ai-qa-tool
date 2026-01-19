import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
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
# 2. UI STYLING (UNCHANGED)
# =========================================================
st.markdown("""
<style>
header, footer, #MainMenu {visibility: hidden;}
.stApp { background-color: #27F5C2; }
.block-container { margin-top: -4rem; max-width: 95%; }

.hero-title {
    font-size: 3.5rem;
    font-weight: 900;
    text-align: center;
    color: #1e293b;
}

.footer-container {
    position: fixed;
    bottom: 0;
    width: 100%;
    background: rgba(255,255,255,0.9);
    display: flex;
    justify-content: space-between;
    padding: 12px 40px;
}
.social-link {
    padding: 10px 24px;
    color: white;
    font-weight: bold;
    border-radius: 50px;
}
.li-color { background:#0077b5; }
.pf-color { background:#333; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 3. API KEY VALIDATION
# =========================================================
if "GEMINI_API_KEY" not in st.secrets:
    st.error("❌ GEMINI_API_KEY missing in Streamlit secrets")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# =========================================================
# 4. MODEL INITIALIZATION (FUTURE-SAFE)
# =========================================================
def load_model():
    """
    Primary: gemini-flash-latest (stable alias)
    Fallback: gemini-pro (older but reliable)
    """
    try:
        return genai.GenerativeModel("gemini-flash-latest")
    except Exception:
        return genai.GenerativeModel("gemini-pro")

model = load_model()

# =========================================================
# 5. MODEL HEALTH CHECK (PREVENTS SILENT FAILURE)
# =========================================================
try:
    _ = model.generate_content("health check")
except Exception:
    st.error("⚠️ AI service temporarily unavailable. Please try later.")
    st.stop()

# =========================================================
# 6. SIDEBAR
# =========================================================
with st.sidebar:
    st.title("Control Panel")
    st.success("Account Status: Tier 1 ✅")

# =========================================================
# 7. MAIN HEADER
# =========================================================
st.markdown('<h1 class="hero-title">TestcaseCraft Pro</h1>', unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;font-weight:600;'>"
    "Professional AI Engine for QA Requirement Analysis</p>",
    unsafe_allow_html=True
)

# =========================================================
# 8. CORE GENERATION FUNCTION (SAFE + RETRY)
# =========================================================
@st.cache_data(show_spinner=False, ttl=3600)
def generate_test_matrix(pdf_text, detail, framework, neg, edge, focus):

    prompt = f"""
You are a Senior QA Lead.

Generate a PROFESSIONAL QA TEST CASE MATRIX in MARKDOWN format.

Rules:
- Use tables
- Include Test Case ID
- Scenario
- Preconditions
- Steps
- Expected Result

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
            response = model.generate_content(prompt)
            return response.text

        except google.api_core.exceptions.ResourceExhausted:
            time.sleep(10)

        except Exception as e:
            return f"ERROR: {str(e)}"

    return "ERROR: Generation failed after retries."

# =========================================================
# 9. FILE UPLOAD
# =========================================================
uploaded_file = st.file_uploader("📄 Upload BRD PDF", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)

    # SAFE TEXT EXTRACTION
    pdf_text = "".join([page.extract_text() or "" for page in reader.pages])

    st.markdown("### ⚙️ Test Strategy Configuration")

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
        include_edge = st.toggle("⚡ Include Edge Cases", True)

    if st.button("🚀 Analyze and Generate Matrix"):
        with st.status("AI Analysis in Progress..."):
            result = generate_test_matrix(
                pdf_text,
                detail_level,
                test_framework,
                include_neg,
                include_edge,
                priority_focus
            )

        st.markdown("---")
        st.subheader("📊 Generated Test Case Matrix")

        if result.startswith("ERROR"):
            st.error(result)
        else:
            st.markdown(result)
            st.download_button(
                "📥 Download Matrix",
                result,
                "QA_Test_Matrix.md",
                "text/markdown"
            )

else:
    st.info("👋 Upload a BRD PDF to begin.")

# =========================================================
# 10. FOOTER
# =========================================================
st.markdown("""
<div class="footer-container">
  <div>© 2026 | Subhan Khan Pathan</div>
  <div>
    <a class="social-link li-color" href="https://www.linkedin.com/">LinkedIn</a>
    <a class="social-link pf-color" href="https://example.com/">Portfolio</a>
  </div>
</div>
""", unsafe_allow_html=True)

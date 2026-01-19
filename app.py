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
# 2. GLOBAL CSS (HIDE MANAGE BUTTON + ANIMATED BACKGROUND)
# =========================================================
st.markdown("""
<style>

/* -------------------------------
   HIDE STREAMLIT UI ELEMENTS
-------------------------------- */
header {visibility: hidden;}
footer {visibility: hidden;}
#MainMenu {visibility: hidden;}
.stAppDeployButton {display: none !important;}
button[title="Manage app"] {display: none !important;}
div[data-testid="stStatusWidget"] {display: none !important;}

/* Extra safety for floating Cloud UI */
div[style*="position: fixed"][style*="bottom"] {
    opacity: 0 !important;
    pointer-events: none !important;
}

/* -------------------------------
   ANIMATED GRADIENT BACKGROUND
-------------------------------- */
.stApp {
    background: linear-gradient(
        -45deg,
        #27F5C2,
        #4ade80,
        #22d3ee,
        #34d399
    );
    background-size: 400% 400%;
    animation: gradientBG 18s ease infinite;
}

@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* -------------------------------
   LAYOUT TUNING
-------------------------------- */
.block-container {
    padding-top: 0rem !important;
    margin-top: -4rem !important;
    max-width: 95%;
}

/* -------------------------------
   GLASSMORPHIC CONTENT CARDS
-------------------------------- */
div[data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(12px);
    border-radius: 20px;
    padding: 30px;
    border: 1px solid rgba(0, 0, 0, 0.05);
}

/* -------------------------------
   TYPOGRAPHY
-------------------------------- */
.hero-title {
    font-size: 3.5rem;
    font-weight: 900;
    color: #1e293b;
    text-align: center;
    margin-bottom: 0px;
}

/* -------------------------------
   FOOTER
-------------------------------- */
.footer-container {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(10px);
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 40px;
    z-index: 9999;
    border-top: 1px solid rgba(0,0,0,0.1);
}

.footer-socials { display: flex; gap: 15px; }

.social-link {
    padding: 10px 24px;
    border-radius: 50px;
    color: white !important;
    text-decoration: none;
    font-weight: bold;
    font-size: 14px;
}

.li-color { background-color: #0077b5; }
.pf-color { background-color: #333333; }

</style>
""", unsafe_allow_html=True)

# =========================================================
# 3. GEMINI API INITIALIZATION (STABLE)
# =========================================================
if "GEMINI_API_KEY" not in st.secrets:
    st.error("❌ GEMINI_API_KEY missing in Streamlit secrets")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Primary + fallback (future-safe)
def load_model():
    try:
        return genai.GenerativeModel("gemini-flash-latest")
    except Exception:
        return genai.GenerativeModel("gemini-pro")

model = load_model()

# Health check
try:
    _ = model.generate_content("health check")
except Exception:
    st.error("⚠️ AI service temporarily unavailable. Please try later.")
    st.stop()

# =========================================================
# 4. SIDEBAR
# =========================================================
with st.sidebar:
    st.title("Control Panel")
    st.divider()
    st.success("Account Status: Tier 1 ✅")

# =========================================================
# 5. HEADER
# =========================================================
st.markdown('<h1 class="hero-title">TestcaseCraft Pro</h1>', unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center; color:#1e293b; font-weight:600; font-size:1.1rem;'>"
    "Professional AI Engine for QA Requirement Analysis</p>",
    unsafe_allow_html=True
)

# =========================================================
# 6. CORE GENERATION FUNCTION
# =========================================================
@st.cache_data(show_spinner=False, ttl=3600)
def generate_cached_matrix(pdf_text, detail, framework, neg, edge, focus):

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
# 7. WORKSPACE
# =========================================================
uploaded_file = st.file_uploader("📄 Upload BRD (PDF)", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    pdf_text = "".join([p.extract_text() or "" for p in reader.pages])

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
        include_edge = st.toggle("⚡ Include Edge Analysis", True)

    if st.button("🚀 Analyze and Generate Matrix"):
        with st.status("AI Analysis in Progress..."):
            result = generate_cached_matrix(
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
                "📥 Export Matrix",
                result,
                "QA_Test_Matrix.md",
                "text/markdown"
            )

else:
    st.info("👋 Upload a BRD PDF to begin.")

# =========================================================
# 8. FOOTER
# =========================================================
st.markdown("""
<div class="footer-container">
    <div>© 2026 | Subhan Khan Pathan</div>
    <div class="footer-socials">
        <a href="https://www.linkedin.com/in/pathan-subhan-khan-256547147/"
           class="social-link li-color" target="_blank">LinkedIn</a>
        <a href="https://subhankhanpathan99.github.io/"
           class="social-link pf-color" target="_blank">Portfolio</a>
    </div>
</div>
""", unsafe_allow_html=True)

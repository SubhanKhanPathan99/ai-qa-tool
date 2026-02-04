import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import google.api_core.exceptions
import pandas as pd
from io import BytesIO
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
# 2. GLOBAL CSS (FIXED SPACING + ANIMATION + FOOTER)
# =========================================================
st.markdown("""
<style>

/* Hide Streamlit default UI */
header, footer, #MainMenu {visibility: hidden;}
.stAppDeployButton {display: none !important;}

/* Remove empty top spacer blocks */
div[data-testid="stVerticalBlock"]:empty {
    display: none !important;
}
div[data-testid="stAnchor"] {
    display: none !important;
}

/* Animated background */
.stApp {
    background: linear-gradient(-45deg,#27F5C2,#4ade80,#22d3ee,#34d399);
    background-size: 400% 400%;
    animation: gradientBG 18s ease infinite;
}

@keyframes gradientBG {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

/* Layout fix */
.block-container {
    padding-top: 0 !important;
    margin-top: -6rem !important;
    max-width: 95%;
}

/* Glass cards */
div[data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {
    background: rgba(255,255,255,0.95);
    backdrop-filter: blur(12px);
    border-radius: 20px;
    padding: 30px;
}

/* Title */
.hero-title {
    font-size: 3.5rem;
    font-weight: 900;
    color: #1e293b;
    text-align: center;
}

/* Footer */
.footer-container {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    background: rgba(255,255,255,0.85);
    backdrop-filter: blur(10px);
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 40px;
    border-top: 1px solid rgba(0,0,0,0.1);
    z-index: 9999;
}

.footer-socials { display: flex; gap: 15px; }

.social-link {
    padding: 8px 20px;
    border-radius: 30px;
    color: white !important;
    text-decoration: none;
    font-weight: bold;
    font-size: 13px;
}

.li-color { background-color: #0077b5; }
.pf-color { background-color: #333333; }

</style>
""", unsafe_allow_html=True)

# =========================================================
# 3. GEMINI API INITIALIZATION
# =========================================================
if "GEMINI_API_KEY" not in st.secrets:
    st.error("❌ GEMINI_API_KEY missing in Streamlit secrets")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

def load_model():
    try:
        return genai.GenerativeModel("gemini-flash-latest")
    except Exception:
        return genai.GenerativeModel("gemini-pro")

model = load_model()

# Health check
try:
    model.generate_content("health check")
except Exception:
    st.error("⚠️ AI service temporarily unavailable.")
    st.stop()

# =========================================================
# 4. HEADER
# =========================================================
st.markdown('<h1 class="hero-title">TestcaseCraft Pro</h1>', unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;font-weight:600;'>Professional AI Engine for QA Requirement Analysis</p>",
    unsafe_allow_html=True
)

# =========================================================
# 5. CORE GENERATION FUNCTION
# =========================================================
@st.cache_data(show_spinner=False, ttl=3600)
def generate_test_matrix(pdf_text, detail, framework, neg, edge, focus):

    prompt = f"""
You are a Senior QA Lead.

Generate a PROFESSIONAL QA TEST CASE MATRIX in MARKDOWN TABLE format.

Columns:
| Test Case ID | Scenario | Preconditions | Steps | Expected Result |

Framework: {framework}
Depth: {detail}
Priority Areas: {', '.join(focus)}
Include Negative Cases: {neg}
Include Edge Cases: {edge}

BRD CONTENT:
{pdf_text[:12000]}
"""

    for _ in range(3):
        try:
            response = model.generate_content(prompt)
            return response.text
        except google.api_core.exceptions.ResourceExhausted:
            time.sleep(10)

    return "ERROR: Generation failed."

# =========================================================
# 6. MARKDOWN → EXCEL CONVERTER (FIXED)
# =========================================================
def markdown_to_excel(markdown_text):
    lines = [line for line in markdown_text.splitlines() if "|" in line]

    clean_lines = [
        line for line in lines
        if not set(line.replace("|", "").strip()).issubset({"-", ":"})
    ]

    rows = []
    for line in clean_lines:
        rows.append([cell.strip() for cell in line.strip("|").split("|")])

    if len(rows) < 2:
        return None

    df = pd.DataFrame(rows[1:], columns=rows[0])

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="QA Test Matrix")

    output.seek(0)
    return output

# =========================================================
# 7. WORKSPACE
# =========================================================
uploaded_file = st.file_uploader("📄 Upload BRD (PDF)", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    pdf_text = "".join([p.extract_text() or "" for p in reader.pages])

    col1, col2 = st.columns(2)

    with col1:
        priority_focus = st.multiselect(
            "🎯 Priority Focus Areas",
            ["UI/UX", "Security", "API/Backend", "Performance"],
            default=["UI/UX"]
        )
        framework = st.selectbox(
            "📖 Output Format",
            ["Standard Manual", "BDD (Cucumber/Gherkin)"]
        )
        detail = st.select_slider(
            "🔍 Analysis Depth",
            ["Standard", "Detailed", "Exhaustive"]
        )

    with col2:
        neg = st.toggle("🧪 Include Negative Cases", True)
        edge = st.toggle("⚡ Include Edge Cases", True)

    if st.button("🚀 Analyze and Generate Matrix"):
        with st.status("AI Analysis in Progress..."):
            result = generate_test_matrix(
                pdf_text, detail, framework, neg, edge, priority_focus
            )

        st.markdown("---")
        st.subheader("📊 Generated Test Case Matrix")

        if result.startswith("ERROR"):
            st.error(result)
        else:
            st.markdown(result)

            excel_file = markdown_to_excel(result)

            c1, c2 = st.columns(2)
            with c1:
                st.download_button(
                    "📄 Download Markdown",
                    result,
                    "QA_Test_Matrix.md",
                    "text/markdown"
                )
            with c2:
                if excel_file:
                    st.download_button(
                        "📊 Download Excel",
                        excel_file,
                        "QA_Test_Matrix.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.warning("Excel export unavailable.")

else:
    st.info("👋 Upload a BRD PDF to begin.")



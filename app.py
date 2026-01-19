import streamlit as st
from PyPDF2 import PdfReader
from google import genai
import time

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="TestcaseCraft Pro",
    page_icon="🧪",
    layout="wide"
)

# =========================================================
# API KEY
# =========================================================
if "GEMINI_API_KEY" not in st.secrets:
    st.error("❌ GEMINI_API_KEY missing in Streamlit secrets")
    st.stop()

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
MODEL_NAME = "gemini-1.5-flash"

# =========================================================
# UI
# =========================================================
st.title("🧪 TestcaseCraft Pro")
st.caption("AI-powered QA Test Case Generator from BRD PDFs")

# =========================================================
# SAFE GEMINI CALL
# =========================================================
@st.cache_data(show_spinner=False, ttl=3600)
def generate_test_matrix(pdf_text, depth, framework, neg, edge):

    prompt = f"""
You are a Senior QA Lead.

Generate a PROFESSIONAL QA TEST CASE MATRIX in MARKDOWN.

Use a table with columns:
- Test Case ID
- Scenario
- Preconditions
- Steps
- Expected Result

Framework: {framework}
Depth: {depth}
Include Negative Cases: {neg}
Include Edge Cases: {edge}

BRD CONTENT:
{pdf_text[:10000]}
"""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        # 🔐 SAFE EXTRACTION
        if not response.candidates:
            return "❌ Gemini returned no candidates."

        candidate = response.candidates[0]

        if not candidate.content or not candidate.content.parts:
            return "❌ Gemini response had no content parts."

        text = candidate.content.parts[0].text

        if not text or not text.strip():
            return "❌ Gemini returned empty text."

        return text

    except Exception as e:
        return f"❌ Gemini API error: {str(e)}"

# =========================================================
# FILE UPLOAD
# =========================================================
uploaded_file = st.file_uploader("📄 Upload BRD PDF", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    pdf_text = "".join([page.extract_text() or "" for page in reader.pages])

    st.subheader("⚙️ Test Strategy Configuration")

    col1, col2 = st.columns(2)

    with col1:
        framework = st.selectbox(
            "Output Format",
            ["Standard Manual", "BDD (Cucumber/Gherkin)"]
        )
        depth = st.select_slider(
            "Analysis Depth",
            ["Standard", "Detailed", "Exhaustive"]
        )

    with col2:
        neg = st.toggle("Include Negative Test Cases", True)
        edge = st.toggle("Include Edge Cases", True)

    if st.button("🚀 Generate Test Matrix"):
        with st.status("Analyzing BRD with Gemini AI..."):
            result = generate_test_matrix(
                pdf_text, depth, framework, neg, edge
            )

        st.markdown("---")
        st.subheader("📊 Generated Test Case Matrix")

        if result.startswith("❌"):
            st.error(result)
        else:
            st.markdown(result)
            st.download_button(
                "📥 Download Markdown",
                result,
                file_name="QA_Test_Matrix.md",
                mime="text/markdown"
            )

else:
    st.info("👆 Upload a BRD PDF to begin analysis.")

# =========================================================
# FOOTER
# =========================================================
st.markdown(
    "<hr><p style='text-align:center;font-weight:600;'>© 2026 | TestcaseCraft Pro</p>",
    unsafe_allow_html=True
)

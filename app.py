import streamlit as st
from PyPDF2 import PdfReader
from google import genai
import time

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="TestcaseCraft Pro | QA Automation",
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
# GEMINI CALL (FIXED RESPONSE PARSING)
# =========================================================
@st.cache_data(show_spinner=False, ttl=3600)
def generate_test_matrix(pdf_text, depth, framework, neg, edge):

    prompt = f"""
You are a Senior QA Lead.

Generate a PROFESSIONAL QA TEST CASE MATRIX in MARKDOWN format.

Requirements:
- Use tables
- Include Test Case ID
- Preconditions
- Steps
- Expected Result

Configuration:
Framework: {framework}
Depth: {depth}
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

            # ✅ CORRECT WAY TO READ TEXT
            return response.candidates[0].content.parts[0].text

        except Exception as e:
            time.sleep(3)

    return None

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

        if result:
            st.markdown(result)

            st.download_button(
                "📥 Download as Markdown",
                result,
                file_name="QA_Test_Matrix.md",
                mime="text/markdown"
            )
        else:
            st.error("❌ Failed to generate test cases. Please retry.")

else:
    st.info("👆 Upload a BRD PDF to begin analysis.")

# =========================================================
# FOOTER
# =========================================================
st.markdown(
    "<hr><p style='text-align:center;font-weight:600;'>© 2026 | TestcaseCraft Pro</p>",
    unsafe_allow_html=True
)

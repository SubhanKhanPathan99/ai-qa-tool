import streamlit as st
from PyPDF2 import PdfReader
from google import genai
import time

st.set_page_config(
    page_title="TestcaseCraft Pro",
    page_icon="🧪",
    layout="wide"
)

if "GEMINI_API_KEY" not in st.secrets:
    st.error("❌ GEMINI_API_KEY missing in Streamlit secrets")
    st.stop()

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# ✅ ONLY MODEL THAT WORKS EVERYWHERE
MODEL_NAME = "models/gemini-1.0-pro"

st.title("🧪 TestcaseCraft Pro")
st.caption("AI-powered QA Test Case Generator from BRD PDFs")

@st.cache_data(show_spinner=False, ttl=3600)
def generate_test_matrix(pdf_text, depth, framework, neg, edge):

    prompt = f"""
You are a Senior QA Lead.

Generate a PROFESSIONAL QA TEST CASE MATRIX in MARKDOWN format.

Use a table with:
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
{pdf_text[:8000]}
"""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        if not response.candidates:
            return "❌ No response candidates from Gemini."

        parts = response.candidates[0].content.parts
        if not parts:
            return "❌ Empty Gemini response."

        return parts[0].text

    except Exception as e:
        return f"❌ Gemini API error: {str(e)}"

uploaded_file = st.file_uploader("📄 Upload BRD PDF", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    pdf_text = "".join([p.extract_text() or "" for p in reader.pages])

    framework = st.selectbox(
        "Output Format",
        ["Standard Manual", "BDD (Cucumber/Gherkin)"]
    )
    depth = st.select_slider(
        "Analysis Depth",
        ["Standard", "Detailed", "Exhaustive"]
    )

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

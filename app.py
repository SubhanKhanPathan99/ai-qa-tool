import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import pandas as pd
import io

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="TestcaseCraft Pro",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. ADVANCED CSS: ANIMATIONS & WHITESPACE FIX
# This block removes the top padding and adds a smooth animated background
st.markdown("""
    <style>
    /* REMOVE TOP WHITESPACE */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        max-width: 90%;
    }

    /* ANIMATED GRADIENT BACKGROUND */
    .stApp {
        background: linear-gradient(315deg, #f0f4f8 0%, #d9e2ec 25%, #bcccdc 50%, #9fb3c8 75%, #829ab1 100%);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
    }

    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* GLASSMORPHISM CONTENT CARDS */
    div[data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {
        background: rgba(255, 255, 255, 0.4);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 30px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
    }

    /* TITLE STYLING */
    .main-title {
        font-size: 4rem;
        font-weight: 800;
        color: #102a43;
        text-align: center;
        margin-bottom: 0px;
    }
    
    .stButton>button {
        background: linear-gradient(90deg, #1E3A8A 0%, #3B82F6 100%);
        color: white;
        border-radius: 12px;
        border: none;
        height: 3.5rem;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. SECURE API INITIALIZATION
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("Missing GEMINI_API_KEY in Secrets.")
    st.stop()

# 4. FRONT-END BRANDING
st.markdown('<p class="main-title">TestcaseCraft Pro</p>', unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#334e68;'>Enterprise AI Engine for QA Requirement Analysis</p>", unsafe_allow_html=True)

# 5. SIDEBAR CONFIGURATION
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2092/2092215.png", width=70)
    st.title("Control Panel")
    detail_level = st.select_slider("Analysis Depth", options=["Standard", "Detailed", "Exhaustive"])
    include_neg = st.toggle("Negative Path Testing", value=True)
    st.divider()
    st.success("System: Ready ✅")

# 6. MAIN WORKSPACE
tab1, tab2 = st.tabs(["🚀 Matrix Generator", "📖 Help Guide"])

with tab1:
    uploaded_file = st.file_uploader("Upload Business Requirement Document (PDF)", type="pdf")

    if uploaded_file:
        reader = PdfReader(uploaded_file)
        text = "".join([p.extract_text() for p in reader.pages])

        if st.button("🚀 Analyze and Generate Matrix"):
            with st.status("AI Analysis in Progress...", expanded=True) as status:
                st.write("Extracting technical requirements...")
                st.write(f"Generating {detail_level} test scenarios...")
                
                prompt = f"""
                Act as a Senior QA Lead. Generate a professional test case matrix.
                OUTPUT ONLY A MARKDOWN TABLE.
                
                Columns: ID, Type (Positive/Negative), Requirement, Description, Expected Result, Priority.
                Depth: {detail_level}. Negative scenarios: {include_neg}.
                
                BRD: {text[:12000]}
                """
                
                response = model.generate_content(prompt)
                
                if not response.candidates or not response.candidates[0].content.parts:
                    status.update(label="Safety Block", state="error")
                    st.error("Document content triggered AI filters. Try another file.")
                    st.stop()
                
                status.update(label="Analysis Complete!", state="complete", expanded=False)

            # RESULTS TABLE
            st.markdown("### 📊 Generated Test Matrix")
            st.markdown(response.text)
            
            # EXPORT ACTION
            st.download_button(
                label="📥 Export Matrix to CSV",
                data=response.text,
                file_name="QA_Matrix.csv",
                mime="text/csv"
            )

with tab2:
    st.info("Upload your PDF to start. The AI will parse requirements and build a table automatically.")
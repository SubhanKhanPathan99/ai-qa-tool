import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import pandas as pd
import io

# 1. PAGE SETUP
st.set_page_config(
    page_title="TestcaseCraft Pro",
    page_icon="🧪",
    layout="wide"
)

# 2. ADVANCED CSS: ANIMATIONS & LAYOUT OPTIMIZATION
st.markdown("""
    <style>
    /* Reduce top whitespace and tighten container */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        max-width: 95%;
    }

    /* Animated Professional Background */
    .stApp {
        background: linear-gradient(-45deg, #f0f4f8, #d9e2ec, #bcccdc, #9fb3c8);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }

    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Glassmorphism for Main Cards */
    div[data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {
        background: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.4);
        padding: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
    }

    /* Title Styling */
    .main-title {
        font-size: 3.5rem;
        font-weight: 900;
        color: #102a43;
        text-align: center;
        margin-bottom: 0px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. SECURE API INITIALIZATION
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-flash-latest')
else:
    st.error("Missing GEMINI_API_KEY in Secrets.")
    st.stop()

# 4. ADVANCED SIDEBAR (NEW OPTIONS)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2092/2092215.png", width=60)
    st.title("Control Panel")
    st.divider()

    # Section 1: Core Configuration
    st.subheader("🛠️ Core Settings")
    detail_level = st.select_slider("Analysis Depth", options=["Standard", "Detailed", "Exhaustive"])
    
    # Section 2: Advanced User Choices
    st.subheader("🎯 Test Strategy")
    test_framework = st.selectbox("Preferred Framework", ["Standard Manual", "Cucumber/Gherkin", "PyTest/Robot", "Cypress Snippets"])
    priority_focus = st.multiselect("Priority Focus", ["Security", "UI/UX", "API/Backend", "Performance"], default=["UI/UX"])
    
    # Section 3: Scenario Toggles
    st.subheader("🧪 Scenarios")
    include_neg = st.toggle("Negative Scenarios", value=True)
    include_edge = st.toggle("Edge Case Analysis", value=False)
    
    st.divider()
    st.caption("Engine: Gemini 1.5 Flash")
    st.success("System: Ready ✅")

# 5. MAIN INTERFACE
st.markdown('<p class="main-title">TestcaseCraft Pro</p>', unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#334e68;'>Enterprise AI Engine for QA Requirement Analysis</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload Business Requirement Document (PDF)", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    text = "".join([p.extract_text() for p in reader.pages])

    if st.button("🚀 Analyze and Generate Matrix"):
        with st.status("AI Analysis in Progress...", expanded=True) as status:
            st.write("Extracting requirements...")
            
            # The prompt now includes the new sidebar variables
            prompt = f"""
            Act as a Senior QA Lead. Generate a professional test case matrix based on this BRD.
            OUTPUT ONLY A MARKDOWN TABLE.
            
            Formatting: Use {test_framework} style.
            Focus Areas: {', '.join(priority_focus)}.
            Detail: {detail_level}. 
            Include Negative: {include_neg}. 
            Include Edge Cases: {include_edge}.
            
            Columns: ID, Type, Requirement Ref, Description, Expected Result, Priority.
            
            BRD CONTENT:
            {text[:12000]}
            """
            
            response = model.generate_content(prompt)
            
            if not response.candidates or not response.candidates[0].content.parts:
                status.update(label="Safety Block", state="error")
                st.error("Analysis blocked. Try another file.")
                st.stop()
            
            status.update(label="Analysis Complete!", state="complete", expanded=False)

        # ORGANIZED DISPLAY
        st.subheader("📊 Generated Test Matrix")
        st.markdown(response.text)
        
        # EXPORT
        st.download_button(
            label="📥 Export Matrix to CSV",
            data=response.text,
            file_name="QA_Matrix.csv",
            mime="text/csv"
        )
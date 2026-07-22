import sys, os, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
from src.ui import header
from src.resume_tools import extract_text_from_upload, match_resume_to_jd

st.set_page_config(page_title="Resume vs JD Matcher", layout="wide")
header(" Resume vs Job Description Matcher", "Instant keyword/skill match score between your resume and a target job description.")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Resume")
    upload = st.file_uploader("Upload resume", type=["txt", "md", "pdf", "docx"], key="resume_up")
    resume_text = st.text_area("...or paste resume text", height=220, key="resume_txt")
    if upload:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(upload.name)[1]) as tmp:
            tmp.write(upload.getbuffer()); tmp_path = tmp.name
        resume_text = extract_text_from_upload(tmp_path)

with col2:
    st.subheader("Job description")
    jd_text = st.text_area("Paste the job description", height=280, key="jd_txt")

if st.button("Compare", type="primary", disabled=not (resume_text.strip() and jd_text.strip())):
    result = match_resume_to_jd(resume_text, jd_text)
    st.metric("Match score", f"{result['match_pct']}%")
    st.progress(result["match_pct"] / 100)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("✅ Matched keywords")
        st.write(", ".join(result["matched_keywords"]) or "None found")
    with c2:
        st.subheader("⚠️ Missing keywords worth adding")
        st.write(", ".join(result["missing_keywords"]) or "None — great coverage!")

    st.info("Take the missing keywords into **AI Resume Optimizer** or **AI Cover Letter Generator** to weave them in naturally.")
else:
    st.caption("Paste/upload both sides to see your match score.")

import sys, os, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
from src import storage
from src.ui import header, provider_badge
from src.resume_tools import extract_text_from_upload, generate_cover_letter

st.set_page_config(page_title="AI Cover Letter Generator", layout="wide")
header("AI Cover Letter Generator", "Generate a tailored cover letter from your resume and a job description.")

col1, col2 = st.columns(2)
with col1:
    company = st.text_input("Company")
    role = st.text_input("Role")
    tone = st.selectbox("Tone", ["professional", "enthusiastic", "concise", "warm"])
    upload = st.file_uploader("Upload resume", type=["txt", "md", "pdf", "docx"])
    resume_text = st.text_area("...or paste resume text", height=200)
    if upload:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(upload.name)[1]) as tmp:
            tmp.write(upload.getbuffer()); tmp_path = tmp.name
        resume_text = extract_text_from_upload(tmp_path)

with col2:
    jd_text = st.text_area("Job description", height=340)

if st.button("Generate cover letter", type="primary", disabled=not (resume_text.strip() and jd_text.strip())):
    with st.spinner("Writing..."):
        result = generate_cover_letter(resume_text, jd_text, company, role, tone)
    storage.append_record("cover_letters", {"company": company, "role": role, "provider": result["provider"]})

    st.subheader("Your cover letter")
    st.text_area("Result (copy from here)", value=result["text"], height=350)
    provider_badge(result["provider"])
    st.caption(f"Resume/JD keyword match used for tailoring: {result['match']['match_pct']}%")

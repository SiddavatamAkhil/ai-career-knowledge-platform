import sys, os, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
from src import storage
from src.ui import header
from src.resume_tools import extract_text_from_upload
from src.career_tools import recommend_jobs

st.set_page_config(page_title="Job Recommendation System", layout="wide")
header(" Job Recommendation System", "Matched job postings from a curated demo listing, ranked by skill overlap with your resume.")

upload = st.file_uploader("Upload resume", type=["txt", "md", "pdf", "docx"])
pasted = st.text_area("...or paste resume text", height=200)

text = ""
if upload:
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(upload.name)[1]) as tmp:
        tmp.write(upload.getbuffer()); tmp_path = tmp.name
    text = extract_text_from_upload(tmp_path)
elif pasted.strip():
    text = pasted

if st.button("Find matching jobs", type="primary", disabled=not text.strip()):
    jobs = recommend_jobs(text)
    storage.append_record("job_recommendations", {"count": len(jobs)})
    for job in jobs:
        with st.container(border=True):
            st.markdown(f"**{job['title']}** — {job['company']} ({job['location']})")
            st.progress(job["match_pct"] / 100)
            st.caption(f"Match: {job['match_pct']}% · Matched skills: {', '.join(job['matched_skills']) or 'none'}")

st.caption("Note: this is a small curated demo job board (src/knowledge_banks.py), not a live job feed.")

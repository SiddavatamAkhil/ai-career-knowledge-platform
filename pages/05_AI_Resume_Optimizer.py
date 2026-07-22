import sys, os, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
from src import storage
from src.ui import header, provider_badge
from src.resume_tools import extract_text_from_upload, optimize_resume

st.set_page_config(page_title="AI Resume Optimizer", layout="wide")
header("AI Resume Optimizer", "Specific, actionable suggestions to strengthen your resume.")

upload = st.file_uploader("Upload resume", type=["txt", "md", "pdf", "docx"])
pasted = st.text_area("...or paste resume text", height=220)
target_role = st.text_input("Target role (optional, sharpens suggestions)", placeholder="e.g. Backend Engineer")

text = ""
if upload:
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(upload.name)[1]) as tmp:
        tmp.write(upload.getbuffer()); tmp_path = tmp.name
    text = extract_text_from_upload(tmp_path)
elif pasted.strip():
    text = pasted

if st.button("Get optimization suggestions", type="primary", disabled=not text.strip()):
    with st.spinner("Analyzing and generating suggestions..."):
        result = optimize_resume(text, target_role)
    storage.append_record("resume_optimizations", {"target_role": target_role, "provider": result["provider"]})

    st.subheader("Suggestions")
    st.write(result["text"])
    provider_badge(result["provider"])

    with st.expander("Underlying heuristics"):
        st.json(result["heuristics"])

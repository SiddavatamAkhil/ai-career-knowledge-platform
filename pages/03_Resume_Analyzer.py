import sys, os, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
from src import storage
from src.ui import header
from src.resume_tools import extract_text_from_upload, resume_quality_heuristics

st.set_page_config(page_title="Resume Analyzer", layout="wide")
header(" Resume Analyzer", "Get an instant structural + quality analysis of your resume.")

upload = st.file_uploader("Upload your resume (.txt, .pdf, .docx)", type=["txt", "md", "pdf", "docx"])
pasted = st.text_area("...or paste resume text directly", height=200)

text = ""
if upload:
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(upload.name)[1]) as tmp:
        tmp.write(upload.getbuffer())
        tmp_path = tmp.name
    text = extract_text_from_upload(tmp_path)
elif pasted.strip():
    text = pasted

if st.button("Analyze resume", type="primary", disabled=not text.strip()):
    with st.spinner("Analyzing..."):
        result = resume_quality_heuristics(text)
    storage.append_record("resume_analyses", {"word_count": result["word_count"], "score": result["heuristic_score"]})

    c1, c2, c3 = st.columns(3)
    c1.metric("Overall score", f"{result['heuristic_score']}/100")
    c2.metric("Word count", result["word_count"])
    c3.metric("Quantified achievements", result["quantified_achievements"])

    st.subheader("Section coverage")
    cols = st.columns(len(result["sections_detected"]))
    for col, (section, present) in zip(cols, result["sections_detected"].items()):
        col.metric(section.title(), "✅" if present else "❌")

    if result["missing_sections"]:
        st.warning(f"Missing sections detected: {', '.join(result['missing_sections'])}")

    st.subheader("Action-verb usage")
    st.progress(min(1.0, result["action_verb_hits"] / 10))
    st.caption(f"{result['action_verb_hits']} strong action verbs detected (aim for 8+)")

    st.info("Head to **AI Resume Optimizer** for specific rewrite suggestions, or **Resume vs Job Description Matcher** to check fit against a specific role.")
elif not text.strip():
    st.info("Upload or paste a resume to get started.")

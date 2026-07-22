import sys, os, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
from src import storage
from src.ui import header
from src.resume_tools import extract_text_from_upload
from src.knowledge_banks import ROLE_SKILLS
from src.career_tools import skill_gap

st.set_page_config(page_title="Skill Gap Analysis", layout="wide")
header(" Skill Gap Analysis", "See exactly which skills you're missing for a target role.")

upload = st.file_uploader("Upload resume", type=["txt", "md", "pdf", "docx"])
pasted = st.text_area("...or paste resume text", height=200)
target_role = st.selectbox("Target role", list(ROLE_SKILLS.keys()))

text = ""
if upload:
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(upload.name)[1]) as tmp:
        tmp.write(upload.getbuffer()); tmp_path = tmp.name
    text = extract_text_from_upload(tmp_path)
elif pasted.strip():
    text = pasted

if st.button("Analyze gap", type="primary", disabled=not text.strip()):
    result = skill_gap(text, target_role)
    storage.append_record("skill_gap_analyses", {"target_role": target_role, "coverage_pct": result["coverage_pct"]})
    st.session_state.last_skill_gap = result

    st.metric("Skill coverage", f"{result['coverage_pct']}%")
    st.progress(result["coverage_pct"] / 100)
    c1, c2 = st.columns(2)
    c1.subheader("✅ Skills you have")
    c1.write(", ".join(result["have_skills"]) or "None detected")
    c2.subheader("❌ Skills to build")
    c2.write(", ".join(result["missing_skills"]) or "None — full coverage!")

    st.info("Head to **Career Roadmap Generator** to turn these gaps into a staged learning plan.")

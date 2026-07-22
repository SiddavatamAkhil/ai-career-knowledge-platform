import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
from src import storage
from src.ui import header, provider_badge
from src.knowledge_banks import ROLE_SKILLS
from src.career_tools import skill_gap, career_roadmap

st.set_page_config(page_title="Career Roadmap Generator", layout="wide")
header(" Career Roadmap Generator", "A staged plan to go from where you are to your target role.")

current_level = st.selectbox("Current level", ["Student / new grad", "Junior (0-2 yrs)", "Mid-level (2-5 yrs)", "Senior (5+ yrs)"])
target_role = st.selectbox("Target role", list(ROLE_SKILLS.keys()))

gap = st.session_state.get("last_skill_gap")
if not gap or gap.get("target_role") != target_role:
    st.caption("Tip: run **Skill Gap Analysis** first for a resume-informed roadmap, or generate a generic one below.")
    resume_snippet = st.text_area("Optional: paste resume text for a more tailored roadmap", height=120)
    gap = skill_gap(resume_snippet, target_role) if resume_snippet.strip() else {"missing_skills": ROLE_SKILLS[target_role], "target_role": target_role}

if st.button("Generate roadmap", type="primary"):
    with st.spinner("Building your roadmap..."):
        result = career_roadmap(current_level, target_role, gap)
    storage.append_record("career_roadmaps", {"target_role": target_role, "current_level": current_level, "provider": result["provider"]})
    st.write(result["text"])
    provider_badge(result["provider"])

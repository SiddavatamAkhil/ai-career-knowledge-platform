import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
from src import storage
from src.ui import header
from src.knowledge_banks import ROLE_SKILLS

st.set_page_config(page_title="User Profile",  layout="wide")
header(" User Profile", "Used to personalize Job Recommendations, Career Roadmap, and the Dashboard greeting.")

profile = storage.load("profile", {}) or {}

with st.form("profile_form"):
    name = st.text_input("Name", value=profile.get("name", ""))
    target_role = st.selectbox("Target role", list(ROLE_SKILLS.keys()), index=list(ROLE_SKILLS.keys()).index(profile.get("target_role")) if profile.get("target_role") in ROLE_SKILLS else 0)
    experience = st.selectbox("Experience level", ["Student / new grad", "Junior (0-2 yrs)", "Mid-level (2-5 yrs)", "Senior (5+ yrs)"],
                               index=["Student / new grad", "Junior (0-2 yrs)", "Mid-level (2-5 yrs)", "Senior (5+ yrs)"].index(profile.get("experience", "Student / new grad")))
    submitted = st.form_submit_button("Save profile", type="primary")
    if submitted:
        storage.save("profile", {"name": name, "target_role": target_role, "experience": experience})
        st.success("Profile saved.")
        st.rerun()

if profile:
    st.divider()
    st.caption(f"Currently saved: {profile.get('name','—')} · {profile.get('target_role','—')} · {profile.get('experience','—')}")

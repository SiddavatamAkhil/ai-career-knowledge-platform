import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
from src import storage

st.set_page_config(page_title="Admin Panel", layout="wide")
st.title(" Admin Panel")
st.caption("Inspect and manage all locally stored app data (this is a single-instance demo, not a real multi-tenant admin system).")
st.divider()

ALL_COLLECTIONS = [
    "profile", "user_settings", "documents", "chat_history", "resume_analyses",
    "resume_optimizations", "cover_letters", "interview_sessions", "skill_gap_analyses",
    "career_roadmaps", "job_recommendations", "company_prep", "project_analyses",
    "summaries", "notes", "quizzes", "flashcards", "doc_comparisons", "team_notes",
    "feedback", "activity_log",
]

selected = st.selectbox("Inspect a data collection", ALL_COLLECTIONS)
data = storage.load(selected, [] if selected not in ("profile", "user_settings") else {})
st.write(f"**{len(data) if isinstance(data, list) else (1 if data else 0)} record(s)**")
st.json(data)

st.divider()
st.subheader("⚠️ Danger zone")
c1, c2 = st.columns(2)
with c1:
    if st.button(f"Clear '{selected}'"):
        storage.clear(selected) if isinstance(data, list) else storage.save(selected, {})
        st.success(f"Cleared {selected}.")
        st.rerun()
with c2:
    if st.button("Clear ALL app data", type="primary"):
        for c in ALL_COLLECTIONS:
            storage.save(c, [] if c not in ("profile", "user_settings") else {})
        st.success("All local data cleared.")
        st.rerun()

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
import pandas as pd
from src import storage
from src.ui import header

st.set_page_config(page_title="Analytics Dashboard",layout="wide")
header(" Analytics Dashboard", "Usage trends across every feature in the app (from local storage — no external analytics).")

collections = {
    "Chat questions": "chat_history",
    "Resume analyses": "resume_analyses",
    "Resume optimizations": "resume_optimizations",
    "Cover letters": "cover_letters",
    "Interview sessions": "interview_sessions",
    "Skill gap analyses": "skill_gap_analyses",
    "Career roadmaps": "career_roadmaps",
    "Job recommendation runs": "job_recommendations",
    "Company prep briefs": "company_prep",
    "Project analyses": "project_analyses",
    "Summaries": "summaries",
    "Quizzes": "quizzes",
    "Flashcard sets": "flashcards",
    "Notes generated": "notes",
    "Feedback entries": "feedback",
}

counts = {label: len(storage.load(key, [])) for label, key in collections.items()}
df = pd.DataFrame({"feature": list(counts.keys()), "count": list(counts.values())}).sort_values("count", ascending=False)

c1, c2 = st.columns([1, 1])
with c1:
    st.subheader("Usage by feature")
    st.bar_chart(df.set_index("feature"))
with c2:
    st.subheader("Raw counts")
    st.dataframe(df, use_container_width=True, hide_index=True)

st.divider()
st.subheader("LLM provider mix (chat questions)")
chat = storage.load("chat_history", [])
if chat:
    provider_counts = pd.Series([c.get("provider", "unknown") for c in chat]).value_counts()
    st.bar_chart(provider_counts)
else:
    st.caption("No chat activity yet.")

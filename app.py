"""
Dashboard / home page for the AI Career & Knowledge Platform.

Run with:  streamlit run app.py
Every other feature lives under pages/ (Streamlit's native multipage
routing) and shares the RAG core (src/rag_pipeline.py, src/llm.py,
src/embeddings.py) plus the local JSON storage layer (src/storage.py).
"""
import streamlit as st
from src import storage
from src.config import config

st.set_page_config(page_title="AI Career & Knowledge Platform", page_icon="🧠", layout="wide")

st.title("🧠 AI Career & Knowledge Platform")
st.caption(
    "A RAG knowledge assistant, extended with a full suite of AI-powered career-prep tools. "
    "Every feature works with zero API keys (local heuristic fallback) and gets noticeably "
    "better once you add OPENAI_API_KEY or ANTHROPIC_API_KEY to .env."
)

profile = storage.load("profile", {}) or {}
if profile.get("name"):
    st.success(f"Welcome back, {profile['name']} 👋" + (f" — targeting **{profile.get('target_role')}**" if profile.get("target_role") else ""))
else:
    st.info("👤 Set up your profile on the **User Profile** page so tools like Job Matcher and Career Roadmap can personalize results.")

st.divider()

# ---------------- Quick stats ----------------
chat_hist = storage.load("chat_history", [])
resumes = storage.load("resume_analyses", [])
quizzes = storage.load("quizzes", [])
docs = storage.load("documents", [])
feedback = storage.load("feedback", [])

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Chat questions asked", len(chat_hist))
c2.metric("Resumes analyzed", len(resumes))
c3.metric("Quizzes generated", len(quizzes))
c4.metric("Documents managed", len(docs))
c5.metric("Feedback entries", len(feedback))

st.divider()
st.subheader("Feature map")

groups = {
    "📚 Knowledge & Documents": [
        ("Knowledge Base", "Build/manage the RAG vector index over your documents"),
        ("AI Chat Assistant", "Chat with your indexed knowledge base, with memory"),
        ("Document Summarizer", "Summarize any document in short/medium/long form"),
        ("Multi-Document Comparison", "Compare themes and differences across documents"),
        ("Document Management", "Central place to upload/view/delete source files"),
    ],
    "📝 Resume & Applications": [
        ("Resume Analyzer", "Heuristic + AI scoring of a resume's strength"),
        ("Resume vs Job Description Matcher", "Keyword/skill match % against a JD"),
        ("AI Resume Optimizer", "Actionable rewrite suggestions"),
        ("AI Cover Letter Generator", "Tailored cover letter from resume + JD"),
        ("Project Analyzer", "Portfolio/project write-up feedback"),
    ],
    "🎤 Interview Prep": [
        ("AI Interview Simulator", "Mixed mock interview session"),
        ("Technical Interview Practice", "Role-specific technical Q&A practice"),
        ("HR Interview Practice", "Behavioral question practice"),
        ("Company Preparation Assistant", "Company + role prep brief"),
    ],
    "🚀 Career Growth": [
        ("Skill Gap Analysis", "Compare your resume against a target role"),
        ("Career Roadmap Generator", "Staged plan to close the gap"),
        ("Job Recommendation System", "Matched mock job postings"),
    ],
    "🎓 Learning Tools": [
        ("Learning Assistant", "Tutor-style Q&A over your materials"),
        ("AI Notes Generator", "Structured notes from any text/document"),
        ("Quiz Generator", "Auto-generated practice quiz"),
        ("Flashcard Generator", "Auto-generated study flashcards"),
    ],
    "⚙️ Account & Admin": [
        ("Analytics Dashboard", "Usage trends across the whole app"),
        ("Chat History", "Every past AI Chat Assistant conversation"),
        ("Team Workspace", "Shared notes board for a team/study group"),
        ("Settings", "Provider, chunking & retrieval settings"),
        ("User Profile", "Your name, target role & default resume"),
        ("Admin Panel", "Inspect/reset all locally stored app data"),
        ("Feedback & Reports", "Leave feedback, see aggregate ratings"),
        ("About / Help", "What this project is and how it's built"),
    ],
}

for group, items in groups.items():
    with st.expander(group, expanded=False):
        cols = st.columns(2)
        for i, (name, desc) in enumerate(items):
            with cols[i % 2]:
                st.markdown(f"**{name}**")
                st.caption(desc)

st.divider()
st.caption(
    f"LLM provider mode: `{config.LLM_PROVIDER}` · Embedding model: `{config.EMBEDDING_MODEL}` · "
    "Use the sidebar (left) to navigate between all pages."
)

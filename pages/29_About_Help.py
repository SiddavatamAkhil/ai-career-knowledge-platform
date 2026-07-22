import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
from src.ui import header

st.set_page_config(page_title="About / Help", layout="wide")
header("ℹ About / Help", "What this project is and how it's built.")

st.markdown(
    """
### What this is
An **AI Career & Knowledge Platform**: a Retrieval-Augmented Generation (RAG) core
(document ingestion → chunking → hybrid FAISS+BM25 retrieval → grounded LLM answer),
extended with a full suite of AI-powered career-prep and learning tools — resume
analysis, JD matching, cover letters, interview simulators, skill-gap/roadmap
planning, quiz/flashcard/notes generation, and more.

### Design philosophy
Every AI feature follows the same pattern as the original RAG pipeline: try
OpenAI, then Anthropic, then fall back to a **local heuristic** (keyword overlap,
extractive summarization, static question banks) — so the whole app runs and
demos end-to-end with **zero API keys**, and gets more fluent the moment you add
`OPENAI_API_KEY` or `ANTHROPIC_API_KEY` to `.env`.

### How data is stored
There's no external database — everything (chat history, resumes, quizzes,
feedback, profile, team notes) is stored as JSON under `storage/` via
`src/storage.py`. Good enough for a single-instance demo; swap in a real
database by only touching that one file.

### Pages
Use the sidebar to navigate — grouped roughly into Knowledge & Documents,
Resume & Applications, Interview Prep, Career Growth, Learning Tools, and
Account & Admin (see the Dashboard for the full map).

### Limitations (by design, for a demo)
- Job Recommendation System uses a small curated mock job list, not a live feed.
- Team Workspace / Admin Panel are single-instance (no real multi-user auth).
- Heuristic fallbacks are good but not as fluent as a real LLM — add an API key
  for the best experience.
"""
)

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
from src.config import config
from src import storage
from src.ui import header, provider_badge

st.set_page_config(page_title="AI Chat Assistant", layout="wide")
header("AI Chat Assistant", "Ask questions over your indexed knowledge base. Remembers recent turns for follow-up questions.")

if "pipeline" not in st.session_state or not st.session_state.get("indexed"):
    st.warning("No index built yet. Go to **Knowledge Base** first and click 'Build / rebuild index'.")
    st.stop()

if "chat_turns" not in st.session_state:
    st.session_state.chat_turns = []

top_k = st.sidebar.slider("Chunks to retrieve (top-k)", 1, 8, config.TOP_K)
use_memory = st.sidebar.checkbox("Use conversation memory (fold recent turns into the query)", value=True)

question = st.chat_input("Ask a question about the indexed documents...")

if question:
    query = question
    if use_memory and st.session_state.chat_turns:
        recent = st.session_state.chat_turns[-2:]
        context_str = " ".join(f"Previous Q: {t['question']} Previous A: {t['answer'][:200]}" for t in recent)
        query = f"{context_str}\nFollow-up question: {question}"

    with st.spinner("Retrieving context and generating an answer..."):
        result = st.session_state.pipeline.ask(query, top_k=top_k)
    result["question"] = question  # display the original, not the memory-augmented query
    st.session_state.chat_turns.append(result)
    storage.append_record("chat_history", {
        "question": question, "answer": result["answer"], "provider": result["provider"],
    })

for turn in reversed(st.session_state.chat_turns):
    with st.chat_message("user"):
        st.write(turn["question"])
    with st.chat_message("assistant"):
        st.write(turn["answer"])
        provider_badge(turn["provider"])
        with st.expander(f"Show {len(turn['sources'])} retrieved source chunks"):
            for i, src in enumerate(turn["sources"], start=1):
                page = f" (p.{src['page']})" if src.get("page") else ""
                st.markdown(f"**[{i}] {src['source']}{page} — score {src['score']}**")
                st.text(src["text"][:600] + ("..." if len(src["text"]) > 600 else ""))

if st.session_state.chat_turns and st.button("Clear this session's chat"):
    st.session_state.chat_turns = []
    st.rerun()

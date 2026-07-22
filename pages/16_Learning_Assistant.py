import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
from src import storage
from src.ui import header, provider_badge

st.set_page_config(page_title="Learning Assistant",  layout="wide")
header(" Learning Assistant", "A tutor-style chat that explains concepts from your indexed knowledge base simply, with analogies.")

if "pipeline" not in st.session_state or not st.session_state.get("indexed"):
    st.warning("No index built yet. Go to **Knowledge Base** first and click 'Build / rebuild index'.")
    st.stop()

if "learn_turns" not in st.session_state:
    st.session_state.learn_turns = []

q = st.chat_input("Ask me to explain something from your documents...")
if q:
    tutor_q = f"Explain this simply, like a patient tutor, using an example if helpful: {q}"
    with st.spinner("Thinking..."):
        result = st.session_state.pipeline.ask(tutor_q)
    result["question"] = q
    st.session_state.learn_turns.append(result)
    storage.append_record("learning_sessions", {"question": q, "provider": result["provider"]})

for turn in reversed(st.session_state.learn_turns):
    with st.chat_message("user"):
        st.write(turn["question"])
    with st.chat_message("assistant"):
        st.write(turn["answer"])
        provider_badge(turn["provider"])

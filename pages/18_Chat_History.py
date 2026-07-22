import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
from src import storage
from src.ui import header

st.set_page_config(page_title="Chat History", layout="wide")
header(" Chat History", "Every question asked via the AI Chat Assistant, persisted locally.")

history = storage.load("chat_history", [])
if not history:
    st.info("No chat history yet — ask something in the AI Chat Assistant page first.")
else:
    search = st.text_input("Search history")
    filtered = [h for h in history if search.lower() in h["question"].lower()] if search else history
    for h in reversed(filtered):
        with st.container(border=True):
            st.markdown(f"**Q: {h['question']}**  \n*{h.get('created_at', '')} · provider: {h.get('provider','?')}*")
            st.write(h["answer"])

    if st.button("🗑️ Clear all chat history"):
        storage.clear("chat_history")
        st.rerun()

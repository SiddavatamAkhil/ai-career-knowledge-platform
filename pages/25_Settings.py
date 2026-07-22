import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
from src import storage
from src.config import config
from src.ui import header

st.set_page_config(page_title="Settings",  layout="wide")
header(" Settings", "Preferences for retrieval and generation. Saved locally; some values require restarting the app to fully take effect (they're read from .env at process start).")

settings = storage.load("user_settings", {}) or {}

st.subheader("Retrieval")
top_k = st.slider("Default chunks retrieved (top-k)", 1, 10, settings.get("top_k", config.TOP_K))
alpha = st.slider("Hybrid alpha (0 = pure keyword/BM25, 1 = pure semantic)", 0.0, 1.0, settings.get("alpha", config.HYBRID_ALPHA))

st.subheader("Generation")
st.caption(f"Current .env provider mode: `{config.LLM_PROVIDER}`  ·  OpenAI key set: {bool(config.OPENAI_API_KEY)}  ·  Anthropic key set: {bool(config.ANTHROPIC_API_KEY)}")
st.info("To change the provider, edit LLM_PROVIDER in your .env file (auto / openai / anthropic / extractive) and restart the app.")

if st.button("Save settings", type="primary"):
    storage.save("user_settings", {"top_k": top_k, "alpha": alpha})
    st.success("Saved. Knowledge Base / Chat pages read these as defaults on next build.")

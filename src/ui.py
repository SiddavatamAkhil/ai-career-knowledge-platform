import streamlit as st
from . import storage


def header(title: str, subtitle: str = ""):
    st.title(title)
    if subtitle:
        st.caption(subtitle)
    st.divider()


def provider_badge(provider: str):
    color = {"openai": "🟢", "anthropic": "🟣", "heuristic-fallback": "🟡", "extractive-fallback": "🟡"}.get(provider, "⚪")
    st.caption(f"{color} generated via: `{provider}`")


def get_profile() -> dict:
    return storage.load("profile", {}) or {}


def log_activity(kind: str, detail: str):
    storage.append_record("activity_log", {"type": kind, "detail": detail})

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
from src import storage
from src.ui import header, provider_badge
from src.learning_tools import analyze_project

st.set_page_config(page_title="Project Analyzer",  layout="wide")
header(" Project Analyzer", "Paste a project/portfolio description (or README) for feedback and resume-bullet suggestions.")

desc = st.text_area("Project description / README text", height=250)

if st.button("Analyze project", type="primary", disabled=not desc.strip()):
    with st.spinner("Analyzing..."):
        result = analyze_project(desc)
    storage.append_record("project_analyses", {"provider": result["provider"], "length": len(desc)})
    st.write(result["text"])
    provider_badge(result["provider"])

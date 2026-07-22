import sys, os, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
from src import storage
from src.ui import header, provider_badge
from src.resume_tools import extract_text_from_upload
from src.learning_tools import summarize_document

st.set_page_config(page_title="Document Summarizer", layout="wide")
header(" Document Summarizer", "Summarize any document in short, medium, or long form.")

upload = st.file_uploader("Upload document", type=["txt", "md", "pdf", "docx"])
pasted = st.text_area("...or paste text", height=220)
length = st.select_slider("Summary length", ["short", "medium", "long"], value="medium")

text = ""
if upload:
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(upload.name)[1]) as tmp:
        tmp.write(upload.getbuffer()); tmp_path = tmp.name
    text = extract_text_from_upload(tmp_path)
elif pasted.strip():
    text = pasted

if st.button("Summarize", type="primary", disabled=not text.strip()):
    with st.spinner("Summarizing..."):
        result = summarize_document(text, length)
    storage.append_record("summaries", {"length": length, "provider": result["provider"]})
    st.write(result["text"])
    provider_badge(result["provider"])

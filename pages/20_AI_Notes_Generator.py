import sys, os, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
from src import storage
from src.ui import header, provider_badge
from src.resume_tools import extract_text_from_upload
from src.learning_tools import generate_notes

st.set_page_config(page_title="AI Notes Generator",  layout="wide")
header(" AI Notes Generator", "Turn any document or pasted text into structured study notes.")

upload = st.file_uploader("Upload document", type=["txt", "md", "pdf", "docx"])
pasted = st.text_area("...or paste text", height=220)

text = ""
if upload:
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(upload.name)[1]) as tmp:
        tmp.write(upload.getbuffer()); tmp_path = tmp.name
    text = extract_text_from_upload(tmp_path)
elif pasted.strip():
    text = pasted

if st.button("Generate notes", type="primary", disabled=not text.strip()):
    with st.spinner("Generating notes..."):
        result = generate_notes(text)
    storage.append_record("notes", {"provider": result["provider"]})
    st.write(result["text"])
    provider_badge(result["provider"])

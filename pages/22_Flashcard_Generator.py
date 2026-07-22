import sys, os, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
from src import storage
from src.ui import header, provider_badge
from src.resume_tools import extract_text_from_upload
from src.learning_tools import generate_flashcards

st.set_page_config(page_title="Flashcard Generator", layout="wide")
header("Flashcard Generator", "Auto-generate study flashcards from any document or pasted text.")

upload = st.file_uploader("Upload document", type=["txt", "md", "pdf", "docx"])
pasted = st.text_area("...or paste text", height=220)
n = st.slider("Number of flashcards", 3, 15, 8)

text = ""
if upload:
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(upload.name)[1]) as tmp:
        tmp.write(upload.getbuffer()); tmp_path = tmp.name
    text = extract_text_from_upload(tmp_path)
elif pasted.strip():
    text = pasted

if st.button("Generate flashcards", type="primary", disabled=not text.strip()):
    with st.spinner("Generating flashcards..."):
        result = generate_flashcards(text, n)
    storage.append_record("flashcards", {"provider": result["provider"], "n_cards": n})
    st.write(result["text"])
    provider_badge(result["provider"])

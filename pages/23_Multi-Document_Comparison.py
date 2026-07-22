import sys, os, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
from src import storage
from src.ui import header, provider_badge
from src.resume_tools import extract_text_from_upload
from src.learning_tools import compare_documents

st.set_page_config(page_title="Multi-Document Comparison", layout="wide")
header(" Multi-Document Comparison", "Upload 2+ documents to compare their themes and differences.")

uploads = st.file_uploader("Upload 2 or more documents", type=["txt", "md", "pdf", "docx"], accept_multiple_files=True)

docs = {}
if uploads:
    for f in uploads:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(f.name)[1]) as tmp:
            tmp.write(f.getbuffer()); tmp_path = tmp.name
        docs[f.name] = extract_text_from_upload(tmp_path)

if st.button("Compare documents", type="primary", disabled=len(docs) < 2):
    with st.spinner("Comparing..."):
        result = compare_documents(docs)
    storage.append_record("doc_comparisons", {"n_docs": len(docs), "provider": result["provider"]})
    st.write(result["text"])
    provider_badge(result["provider"])
elif uploads and len(docs) < 2:
    st.warning("Upload at least 2 documents to compare.")

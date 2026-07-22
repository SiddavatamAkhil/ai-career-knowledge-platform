import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pathlib import Path
import streamlit as st
from src import storage
from src.ui import header

st.set_page_config(page_title="Document Management", layout="wide")
header(" Document Management", "Central log of documents that have been uploaded/used across the app.")

UPLOAD_DIR = Path("storage/managed_docs")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

uploaded = st.file_uploader("Upload a document to the shared library", type=["txt", "md", "pdf", "docx"], accept_multiple_files=True)
if uploaded:
    for f in uploaded:
        dest = UPLOAD_DIR / f.name
        dest.write_bytes(f.getbuffer())
        docs = storage.load("documents", [])
        if not any(d["name"] == f.name for d in docs):
            storage.append_record("documents", {"name": f.name, "used_in": "Document Management"})
    st.success(f"Uploaded {len(uploaded)} file(s).")

st.divider()
docs = storage.load("documents", [])
if not docs:
    st.info("No documents logged yet.")
else:
    for d in reversed(docs):
        c1, c2, c3 = st.columns([3, 2, 1])
        c1.write(f"📄 {d['name']}")
        c2.caption(f"first used in: {d.get('used_in','?')} · {d.get('created_at','')}")
        if c3.button("Delete record", key=f"del_{d['id']}"):
            remaining = [x for x in docs if x["id"] != d["id"]]
            storage.save("documents", remaining)
            st.rerun()

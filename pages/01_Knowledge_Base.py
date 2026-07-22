import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pathlib import Path
import streamlit as st
from src.rag_pipeline import RAGPipeline
from src.config import config
from src import storage
from src.ui import header

st.set_page_config(page_title="Knowledge Base", page_icon="📚", layout="wide")
header("📚 Knowledge Base", "Build and inspect the RAG vector index that powers the AI Chat Assistant and Learning Assistant.")

if "pipeline" not in st.session_state:
    st.session_state.pipeline = None
if "indexed" not in st.session_state:
    st.session_state.indexed = False

col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("1. Choose document source")
    source_choice = st.radio("Document source", ["Use sample documents", "Upload my own files"], index=0)

    uploaded_files = None
    if source_choice == "Upload my own files":
        uploaded_files = st.file_uploader(
            "Upload .txt, .md, .pdf, or .docx files",
            accept_multiple_files=True,
            type=["txt", "md", "pdf", "docx"],
        )

    if st.button("⚙️ Build / rebuild index", type="primary", use_container_width=True):
        with st.spinner("Loading documents, chunking, and building the vector index..."):
            pipeline = RAGPipeline()
            if source_choice == "Use sample documents":
                pipeline.ingest_directory(config.DOCS_DIR)
                indexed_names = [p.name for p in Path(config.DOCS_DIR).glob("*")]
            elif uploaded_files:
                tmp_dir = Path("storage/uploaded")
                tmp_dir.mkdir(parents=True, exist_ok=True)
                paths = []
                for f in uploaded_files:
                    dest = tmp_dir / f.name
                    dest.write_bytes(f.getbuffer())
                    paths.append(str(dest))
                pipeline.ingest_files(paths)
                indexed_names = [f.name for f in uploaded_files]
            else:
                st.warning("Please upload at least one file first.")
                st.stop()

            st.session_state.pipeline = pipeline
            st.session_state.indexed = True
            st.session_state.history = []
            for name in indexed_names:
                docs = storage.load("documents", [])
                if not any(d["name"] == name for d in docs):
                    storage.append_record("documents", {"name": name, "used_in": "Knowledge Base"})
        st.success("Index built! Head to the AI Chat Assistant or Learning Assistant page to ask questions.")

with col_right:
    st.subheader("2. Index stats")
    if st.session_state.indexed:
        stats = st.session_state.pipeline.stats()
        m1, m2 = st.columns(2)
        m1.metric("Source documents", stats["documents"])
        m2.metric("Chunks indexed", stats["chunks"])
        st.caption(f"Embedding backend: `{stats['embedding_backend']}`")
    else:
        st.info("No index built yet this session.")

    st.subheader("3. Generation settings")
    st.caption(f"LLM provider mode: `{config.LLM_PROVIDER}` (change in Settings page)")
    st.caption(
        "Set OPENAI_API_KEY or ANTHROPIC_API_KEY in a .env file for real LLM answers "
        "everywhere in this app. Without one, every AI feature uses a local heuristic "
        "fallback so nothing ever breaks."
    )

st.divider()
with st.expander("ℹ️ How this pipeline works (architecture)"):
    st.markdown(
        """
1. **Ingestion** — documents (`.txt`, `.md`, `.pdf`, `.docx`) are loaded and normalized to plain text, keeping source/page metadata.
2. **Chunking** — text is split into overlapping windows so retrieval returns precise passages instead of whole documents.
3. **Embedding** — chunks are embedded with `sentence-transformers` (with a TF-IDF fallback for fully offline use).
4. **Indexing** — vectors go into a FAISS index plus a BM25 sparse keyword index.
5. **Hybrid retrieval** — dense + sparse scores are blended (`alpha` weight).
6. **Generation** — top-k chunks are inserted as grounding context for an LLM (OpenAI/Anthropic), with a local extractive fallback.
        """
    )

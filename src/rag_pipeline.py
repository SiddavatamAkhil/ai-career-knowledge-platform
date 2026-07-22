"""
Top-level orchestrator that wires together: load -> chunk -> embed/index ->
retrieve -> generate. This is the class the Streamlit app (or any other
frontend, or a CLI) talks to — it hides all the moving parts behind three
methods: ingest(), ask(), and stats().
"""
import time
from typing import List, Optional

from .config import config
from .document_loader import load_directory, load_document, Document
from .chunking import chunk_documents, Chunk
from .embeddings import get_embedding_backend
from .vector_store import VectorStore
from .llm import generate_answer


class RAGPipeline:
    def __init__(self):
        self.embedding_backend = get_embedding_backend(config.EMBEDDING_MODEL)
        self.store = VectorStore(self.embedding_backend, alpha=config.HYBRID_ALPHA)
        self.num_source_docs = 0
        self.num_chunks = 0

    def ingest_directory(self, directory: str):
        docs = load_directory(directory)
        self._index(docs)

    def ingest_files(self, paths: List[str]):
        docs: List[Document] = []
        for p in paths:
            docs.extend(load_document(p))
        self._index(docs)

    def _index(self, docs: List[Document]):
        chunks = chunk_documents(docs, config.CHUNK_SIZE, config.CHUNK_OVERLAP)
        self.store.build(chunks)
        self.num_source_docs = len({d.metadata.get("source") for d in docs})
        self.num_chunks = len(chunks)

    def ask(self, question: str, top_k: Optional[int] = None) -> dict:
        t0 = time.time()
        k = top_k or config.TOP_K
        retrieved = self.store.search(question, k=k)
        retrieval_ms = (time.time() - t0) * 1000

        chunks_only = [c for c, _ in retrieved]
        t1 = time.time()
        result = generate_answer(question, chunks_only)
        generation_ms = (time.time() - t1) * 1000

        return {
            "question": question,
            "answer": result["answer"],
            "provider": result["provider"],
            "embedding_backend": self.embedding_backend.name,
            "sources": [
                {
                    "text": c.text,
                    "score": round(float(score), 4),
                    "source": c.metadata.get("source"),
                    "page": c.metadata.get("page"),
                }
                for c, score in retrieved
            ],
            "timing_ms": {
                "retrieval": round(retrieval_ms, 1),
                "generation": round(generation_ms, 1),
            },
        }

    def stats(self) -> dict:
        return {
            "documents": self.num_source_docs,
            "chunks": self.num_chunks,
            "embedding_backend": self.embedding_backend.name,
        }

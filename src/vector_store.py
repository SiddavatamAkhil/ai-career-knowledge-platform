"""
Hybrid vector store: dense semantic search (FAISS) combined with sparse
keyword search (BM25). Hybrid retrieval is a genuinely important RAG design
point worth knowing for an interview: dense embeddings are great at "meaning"
matches but can miss exact keywords/IDs/acronyms that BM25 nails. Blending
both scores is a common production pattern (used by e.g. Elastic, Weaviate,
Azure AI Search).
"""
import pickle
from pathlib import Path
from typing import List, Tuple

import numpy as np
import faiss
from rank_bm25 import BM25Okapi

from .chunking import Chunk
from .embeddings import EmbeddingBackend


class VectorStore:
    def __init__(self, embedding_backend: EmbeddingBackend, alpha: float = 0.5):
        self.embedding_backend = embedding_backend
        self.alpha = alpha  # weight for dense score; (1 - alpha) for BM25
        self.chunks: List[Chunk] = []
        self.index: faiss.Index = None
        self.bm25: BM25Okapi = None
        self.dim = None

    def build(self, chunks: List[Chunk]):
        self.chunks = chunks
        texts = [c.text for c in chunks]

        # Dense index
        vectors = self.embedding_backend.embed(texts)
        self.dim = vectors.shape[1]
        self.index = faiss.IndexFlatIP(self.dim)  # inner product == cosine on normalized vecs
        self.index.add(vectors)

        # Sparse index
        tokenized = [t.lower().split() for t in texts]
        self.bm25 = BM25Okapi(tokenized)

    def _dense_scores(self, query: str, k: int) -> List[Tuple[int, float]]:
        qvec = self.embedding_backend.embed([query])
        scores, idxs = self.index.search(qvec, min(k, len(self.chunks)))
        return list(zip(idxs[0].tolist(), scores[0].tolist()))

    def _sparse_scores(self, query: str) -> np.ndarray:
        scores = self.bm25.get_scores(query.lower().split())
        max_s = scores.max() if len(scores) and scores.max() > 0 else 1.0
        return scores / max_s  # normalize to 0..1 so it's comparable to cosine sim

    def search(self, query: str, k: int = 4) -> List[Tuple[Chunk, float]]:
        """Returns top-k (chunk, blended_score) pairs, highest score first."""
        if not self.chunks:
            return []

        dense = self._dense_scores(query, k=max(k * 3, k))
        dense_scores = {idx: score for idx, score in dense if idx != -1}

        sparse = self._sparse_scores(query)

        blended = {}
        all_idxs = set(dense_scores.keys()) | set(range(len(sparse)))
        for idx in all_idxs:
            d = dense_scores.get(idx, 0.0)
            s = sparse[idx] if idx < len(sparse) else 0.0
            blended[idx] = self.alpha * d + (1 - self.alpha) * s

        ranked = sorted(blended.items(), key=lambda x: x[1], reverse=True)[:k]
        return [(self.chunks[idx], score) for idx, score in ranked]

    def save(self, directory: str):
        Path(directory).mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(Path(directory) / "index.faiss"))
        with open(Path(directory) / "meta.pkl", "wb") as f:
            pickle.dump({"chunks": self.chunks, "dim": self.dim}, f)

    def load(self, directory: str):
        self.index = faiss.read_index(str(Path(directory) / "index.faiss"))
        with open(Path(directory) / "meta.pkl", "rb") as f:
            data = pickle.load(f)
        self.chunks = data["chunks"]
        self.dim = data["dim"]
        tokenized = [c.text.lower().split() for c in self.chunks]
        self.bm25 = BM25Okapi(tokenized)

"""
Embedding backend.

Primary path: sentence-transformers (all-MiniLM-L6-v2) — real dense
semantic embeddings, downloaded from HuggingFace on first run.

Fallback path: a dependency-light TF-IDF vectorizer. This exists so the
whole pipeline still runs end-to-end on a machine with no internet access
(e.g. mid-interview Wi-Fi issues) or before the sentence-transformers model
has finished downloading. The rest of the pipeline (vector store, retrieval,
generation) doesn't care which backend produced the vectors — it just wants
fixed-length float arrays it can compare with cosine similarity.
"""
import numpy as np
from typing import List


class EmbeddingBackend:
    def embed(self, texts: List[str]) -> np.ndarray:
        raise NotImplementedError

    @property
    def name(self) -> str:
        raise NotImplementedError


class SentenceTransformerBackend(EmbeddingBackend):
    def __init__(self, model_name: str):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)
        self._name = model_name

    def embed(self, texts: List[str]) -> np.ndarray:
        vecs = self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return np.asarray(vecs, dtype="float32")

    @property
    def name(self) -> str:
        return f"sentence-transformers/{self._name}"


class TfidfBackend(EmbeddingBackend):
    """
    Zero-download fallback. Fits a TF-IDF vocabulary over the corpus at
    index time, then projects queries into the same space. Not as
    semantically rich as a neural embedding, but deterministic, fast,
    and fully local.
    """
    def __init__(self):
        from sklearn.feature_extraction.text import TfidfVectorizer
        self.vectorizer = TfidfVectorizer(stop_words="english", max_features=20000)
        self._fitted = False

    def fit(self, corpus: List[str]):
        self.vectorizer.fit(corpus)
        self._fitted = True

    def embed(self, texts: List[str]) -> np.ndarray:
        if not self._fitted:
            self.fit(texts)
        mat = self.vectorizer.transform(texts)
        # normalize rows for cosine similarity via dot product
        arr = mat.toarray().astype("float32")
        norms = np.linalg.norm(arr, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return arr / norms

    @property
    def name(self) -> str:
        return "tfidf-fallback"


def get_embedding_backend(model_name: str) -> EmbeddingBackend:
    """
    Tries the real neural embedding model first; falls back cleanly if the
    package or model weights aren't available (e.g. no internet access).
    """
    try:
        return SentenceTransformerBackend(model_name)
    except Exception as e:
        print(f"[embeddings] Falling back to TF-IDF backend ({e})")
        return TfidfBackend()

"""
Central configuration for the RAG pipeline.

All knobs the person demoing this project might want to tweak live here,
so the rest of the codebase never hardcodes magic numbers.
"""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    # --- Chunking ---
    CHUNK_SIZE: int = 500          # characters per chunk
    CHUNK_OVERLAP: int = 80        # overlap between consecutive chunks

    # --- Retrieval ---
    TOP_K: int = 4                 # number of chunks retrieved per query
    HYBRID_ALPHA: float = 0.5      # weight between dense (semantic) and sparse (BM25) search

    # --- Embeddings ---
    # Preferred: sentence-transformers model (downloaded from HuggingFace on first run).
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # --- LLM generation ---
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "auto")   # "openai" | "anthropic" | "extractive" | "auto"
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

    # --- Storage ---
    VECTOR_STORE_DIR: str = os.getenv("VECTOR_STORE_DIR", "storage/vector_index")
    DOCS_DIR: str = os.getenv("DOCS_DIR", "data/sample_docs")


config = Config()

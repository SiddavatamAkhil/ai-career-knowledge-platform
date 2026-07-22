"""
Basic sanity tests for the RAG pipeline. Run with: pytest tests/
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.chunking import split_text, chunk_documents
from src.document_loader import Document
from src.rag_pipeline import RAGPipeline


def test_split_text_respects_size():
    text = "Sentence one. " * 100
    chunks = split_text(text, chunk_size=200, overlap=40)
    assert all(len(c) <= 260 for c in chunks)  # allow small overshoot for sentence-boundary snapping
    assert len(chunks) > 1


def test_split_text_short_text_single_chunk():
    text = "Short text."
    chunks = split_text(text, chunk_size=500, overlap=80)
    assert chunks == ["Short text."]


def test_chunk_documents_preserves_metadata():
    docs = [Document(text="A" * 1000, metadata={"source": "test.txt"})]
    chunks = chunk_documents(docs, chunk_size=200, overlap=40)
    assert all(c.metadata["source"] == "test.txt" for c in chunks)
    assert all("chunk_index" in c.metadata for c in chunks)


def test_end_to_end_pipeline_answers_from_sample_docs():
    pipeline = RAGPipeline()
    pipeline.ingest_directory("data/sample_docs")
    assert pipeline.stats()["chunks"] > 0

    result = pipeline.ask("What is the battery life of the AR-200?")
    assert "10 hours" in result["answer"] or "battery" in result["answer"].lower()
    assert len(result["sources"]) > 0
    assert result["sources"][0]["source"] == "product_docs.txt"


def test_retrieval_returns_relevant_source_for_pto_question():
    pipeline = RAGPipeline()
    pipeline.ingest_directory("data/sample_docs")
    result = pipeline.ask("How many PTO days do employees accrue per year?")
    top_sources = [s["source"] for s in result["sources"]]
    assert "company_handbook.txt" in top_sources

"""
Splits long documents into overlapping chunks small enough to embed and
retrieve precisely, while keeping enough overlap that we don't cut an
answer-bearing sentence in half between two chunks.
"""
from dataclasses import dataclass, field
from typing import List
from .document_loader import Document


@dataclass
class Chunk:
    text: str
    metadata: dict = field(default_factory=dict)
    chunk_id: str = ""


def split_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    """
    Simple sliding-window splitter that tries to break on sentence/paragraph
    boundaries when possible, falling back to hard character cuts.
    """
    text = text.strip()
    if len(text) <= chunk_size:
        return [text] if text else []

    # Prefer splitting on paragraph breaks, then sentences, then hard cut.
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        if end < n:
            # try to end on a sentence boundary within the window
            window = text[start:end]
            last_break = max(window.rfind(". "), window.rfind("\n"))
            if last_break > chunk_size * 0.5:
                end = start + last_break + 1
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= n:
            break
        start = max(end - overlap, start + 1)
    return chunks


def chunk_documents(documents: List[Document], chunk_size: int, overlap: int) -> List[Chunk]:
    chunks: List[Chunk] = []
    for doc_idx, doc in enumerate(documents):
        pieces = split_text(doc.text, chunk_size, overlap)
        for i, piece in enumerate(pieces):
            meta = dict(doc.metadata)
            meta["chunk_index"] = i
            chunks.append(
                Chunk(
                    text=piece,
                    metadata=meta,
                    chunk_id=f"{doc_idx}-{i}",
                )
            )
    return chunks

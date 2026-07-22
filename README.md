# AI Career & Knowledge Platform (RAG Pipeline + 28 AI Tools)

Started as a working Retrieval-Augmented Generation system (upload
documents, ask questions in plain English, get answers grounded in those
documents with cited sources) and has grown into a full multi-page
Streamlit platform: the original RAG core, plus resume tools, interview
simulators, career planning, and learning tools — 29 pages in total, all
listed under **Dashboard**.

Every AI feature follows the same reliability pattern as the original
pipeline: try OpenAI → try Anthropic → fall back to a local heuristic
(keyword overlap, extractive summarization, static question banks). That
means the **entire app runs end-to-end with zero API keys**, and gets more
fluent the moment you add `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` to `.env`.

## New pages (on top of the original RAG demo)

- **Knowledge & Documents:** AI Chat Assistant (with conversation memory),
  Document Summarizer, Multi-Document Comparison, Document Management
- **Resume & Applications:** Resume Analyzer, Resume vs JD Matcher, AI
  Resume Optimizer, AI Cover Letter Generator, Project Analyzer
- **Interview Prep:** AI Interview Simulator, Technical Interview Practice,
  HR Interview Practice, Company Preparation Assistant
- **Career Growth:** Skill Gap Analysis, Career Roadmap Generator, Job
  Recommendation System (small curated mock job board)
- **Learning Tools:** Learning Assistant (tutor-style chat), AI Notes
  Generator, Quiz Generator, Flashcard Generator
- **Account & Admin:** Analytics Dashboard, Chat History, Team Workspace,
  Settings, User Profile, Admin Panel, Feedback & Reports, About/Help

All new logic lives in `src/resume_tools.py`, `src/career_tools.py`,
`src/learning_tools.py`, and `src/knowledge_banks.py` (static role/skill/
question data), with local JSON persistence via `src/storage.py` (no
external DB — everything lives under `storage/`, swap that one file for a
real database later if needed).

## Architecture

```
 Documents (.txt/.md/.pdf/.docx)
        │
        ▼
 ┌─────────────┐     ┌───────────┐     ┌───────────────┐
 │  Ingestion  │ --> │ Chunking  │ --> │   Embedding    │
 │(load & clean)│    │(overlap   │     │(sentence-      │
 │             │     │ windows)  │     │ transformers)  │
 └─────────────┘     └───────────┘     └───────┬────────┘
                                                │
                                                ▼
                                   ┌────────────────────────┐
                                   │   Hybrid Vector Store   │
                                   │  FAISS (dense) + BM25   │
                                   │      (sparse)           │
                                   └────────────┬────────────┘
                                                │  top-k chunks
        User question ────────────────────────►│
                                                ▼
                                   ┌────────────────────────┐
                                   │   LLM Generation        │
                                   │ OpenAI / Anthropic /    │
                                   │ local extractive        │
                                   │ fallback                │
                                   └────────────┬────────────┘
                                                ▼
                                        Grounded answer
                                        + cited sources
```

## Why each design choice (for the interview)

- **Chunking with overlap (500 chars / 80 overlap):** prevents an answer
  from being split across two chunks with no shared context, without
  bloating chunk size so much that retrieval gets vague.
- **Hybrid retrieval (dense + BM25):** dense embeddings capture *meaning*
  ("time off" ≈ "PTO"), BM25 catches exact keywords, IDs, model numbers, and
  acronyms that embeddings sometimes blur. Scores are blended with a
  configurable `alpha` weight — this is the same pattern used in production
  systems like Azure AI Search and Weaviate's hybrid search.
- **Provider-agnostic generation layer:** the app tries OpenAI, then
  Anthropic, then falls back to a dependency-free extractive answer built
  directly from retrieved passages. This means the demo **never breaks**
  because of a missing API key or a bad Wi-Fi connection — a deliberate
  reliability decision, not a limitation.
- **Metadata-first design:** every chunk carries its source filename (and
  page number for PDFs) from the moment it's loaded, so every answer can
  cite exactly where it came from — critical for trust in a knowledge
  assistant.
- **Two independent embedding backends:** sentence-transformers
  (`all-MiniLM-L6-v2`) for real semantic search, with an automatic TF-IDF
  fallback if the model can't be downloaded (no internet, blocked network,
  etc.) — the pipeline degrades gracefully instead of crashing.

## Project structure

```
rag-knowledge-assistant/
├── app.py                     # Streamlit UI
├── src/
│   ├── config.py               # all tunable settings in one place
│   ├── document_loader.py      # .txt/.md/.pdf/.docx ingestion
│   ├── chunking.py             # sliding-window text splitter
│   ├── embeddings.py           # sentence-transformers + TF-IDF fallback
│   ├── vector_store.py         # FAISS + BM25 hybrid search
│   ├── llm.py                  # OpenAI / Anthropic / extractive generation
│   └── rag_pipeline.py         # orchestrates the full pipeline
├── data/sample_docs/           # demo documents (fictional robotics company)
├── tests/test_pipeline.py      # pytest suite
├── requirements.txt
└── .env.example
```

## Setup

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # optional — add an API key if you have one
streamlit run app.py
```

The app opens at `http://localhost:8501`. Click **"Build / rebuild index"**
in the sidebar to index the bundled sample documents, then ask questions
like:

- "What is the battery life of the AR-200?"
- "How many days of PTO do employees get?"
- "What safety standard is the robot certified to?"

No API key is required to see it work end-to-end — without one, it uses
the local extractive fallback. Add `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`
to `.env` for fluent, LLM-generated answers instead.

## Running tests

```bash
pip install pytest
pytest tests/ -v
```

## Possible extensions to mention if asked "what would you add next"

- Swap FAISS `IndexFlatIP` for `IndexIVFPQ` for approximate search at scale
  (millions of chunks).
- Add a re-ranking stage (e.g. a cross-encoder) after initial retrieval to
  improve precision on the top-k results.
- Persist the vector index to disk (`store.save()` / `store.load()` are
  already implemented) and add incremental re-indexing instead of full
  rebuilds.
- Add conversation memory so follow-up questions can reference prior turns.
- Add an evaluation harness (e.g. RAGAS) to measure faithfulness and
  answer relevance against a labeled question set.

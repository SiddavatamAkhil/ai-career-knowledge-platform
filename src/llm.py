"""
Generation layer: takes the user question + retrieved chunks and produces
a grounded answer.

Three providers, tried in order of preference unless one is forced via
LLM_PROVIDER in .env:
  1. OpenAI   (if OPENAI_API_KEY is set)
  2. Anthropic (if ANTHROPIC_API_KEY is set)
  3. Extractive fallback (no API key / no internet needed at all) — builds
     an answer directly from the retrieved passages using simple sentence
     ranking. This guarantees the demo never dies because of a missing key
     or a flaky connection.
"""
from typing import List
from .chunking import Chunk
from .config import config


SYSTEM_PROMPT = (
    "You are a knowledgeable assistant answering questions using ONLY the "
    "provided context. If the context does not contain the answer, say so "
    "clearly instead of guessing. Cite sources using the [source] tags given "
    "in the context. Be concise and accurate."
)


def build_context_block(chunks: List[Chunk]) -> str:
    blocks = []
    for c in chunks:
        src = c.metadata.get("source", "unknown")
        page = c.metadata.get("page")
        tag = f"{src}" + (f" p.{page}" if page else "")
        blocks.append(f"[source: {tag}]\n{c.text}")
    return "\n\n---\n\n".join(blocks)


def _generate_openai(question: str, context: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=config.OPENAI_API_KEY)
    resp = client.chat.completions.create(
        model=config.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
        temperature=0.2,
    )
    return resp.choices[0].message.content


def _generate_anthropic(question: str, context: str) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    resp = client.messages.create(
        model=config.ANTHROPIC_MODEL,
        max_tokens=800,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}],
    )
    return resp.content[0].text


def _generate_extractive(question: str, chunks: List[Chunk]) -> str:
    """
    No-API fallback. Ranks sentences across retrieved chunks by lexical
    overlap with the question and stitches the best ones into an answer.
    Not as fluent as an LLM, but fully offline and always available.
    """
    import re
    from collections import Counter

    q_words = set(w.lower() for w in re.findall(r"\w+", question) if len(w) > 2)

    scored_sentences = []
    for c in chunks:
        sentences = re.split(r"(?<=[.!?])\s+", c.text)
        for s in sentences:
            s_clean = s.strip()
            if len(s_clean) < 20:
                continue
            s_words = Counter(w.lower() for w in re.findall(r"\w+", s_clean))
            overlap = sum(s_words[w] for w in q_words if w in s_words)
            if overlap > 0:
                src = c.metadata.get("source", "unknown")
                scored_sentences.append((overlap, s_clean, src))

    scored_sentences.sort(key=lambda x: x[0], reverse=True)
    top = scored_sentences[:4]

    if not top:
        return (
            "I couldn't find a direct answer in the indexed documents. "
            "Try rephrasing the question or adding more source documents."
        )

    answer_lines = [f"- {s} (source: {src})" for _, s, src in top]
    return "Based on the retrieved passages:\n" + "\n".join(answer_lines)


def generate_answer(question: str, chunks: List[Chunk]) -> dict:
    """
    Returns {"answer": str, "provider": str} so the UI can show which
    generation path actually ran.
    """
    context = build_context_block(chunks)
    provider_pref = config.LLM_PROVIDER

    def try_openai():
        if config.OPENAI_API_KEY:
            return _generate_openai(question, context), "openai"
        return None

    def try_anthropic():
        if config.ANTHROPIC_API_KEY:
            return _generate_anthropic(question, context), "anthropic"
        return None

    order = []
    if provider_pref == "openai":
        order = [try_openai]
    elif provider_pref == "anthropic":
        order = [try_anthropic]
    elif provider_pref == "extractive":
        order = []
    else:  # auto
        order = [try_openai, try_anthropic]

    for attempt in order:
        try:
            result = attempt()
            if result:
                answer, provider = result
                return {"answer": answer, "provider": provider}
        except Exception as e:
            print(f"[llm] provider failed, trying next: {e}")
            continue

    return {"answer": _generate_extractive(question, chunks), "provider": "extractive-fallback"}


def _generate_openai_text(system: str, prompt: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=config.OPENAI_API_KEY)
    resp = client.chat.completions.create(
        model=config.OPENAI_MODEL,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
        temperature=0.4,
    )
    return resp.choices[0].message.content


def _generate_anthropic_text(system: str, prompt: str) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    resp = client.messages.create(
        model=config.ANTHROPIC_MODEL,
        max_tokens=1200,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text


def ai_generate(system: str, prompt: str, fallback) -> dict:
    """
    Generic text-generation call reused by every AI feature page (resume
    tools, interview simulators, notes/quiz/flashcard generators, etc).

    Tries OpenAI -> Anthropic (per LLM_PROVIDER / whichever key is set),
    and if neither is available or both fail, calls the supplied
    `fallback()` callable, which must return a plain string. This keeps
    every feature in the app usable with zero API keys configured, same
    philosophy as generate_answer() above.
    """
    provider_pref = config.LLM_PROVIDER

    def try_openai():
        if config.OPENAI_API_KEY:
            return _generate_openai_text(system, prompt), "openai"
        return None

    def try_anthropic():
        if config.ANTHROPIC_API_KEY:
            return _generate_anthropic_text(system, prompt), "anthropic"
        return None

    if provider_pref == "openai":
        order = [try_openai]
    elif provider_pref == "anthropic":
        order = [try_anthropic]
    elif provider_pref == "extractive":
        order = []
    else:
        order = [try_openai, try_anthropic]

    for attempt in order:
        try:
            result = attempt()
            if result:
                text, provider = result
                return {"text": text, "provider": provider}
        except Exception as e:
            print(f"[llm] provider failed, trying next: {e}")
            continue

    return {"text": fallback(), "provider": "heuristic-fallback"}


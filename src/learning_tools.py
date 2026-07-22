"""
Document Summarizer / AI Notes Generator / Quiz Generator / Flashcard
Generator / Multi-Document Comparison / Project Analyzer.

Each has a pure-heuristic fallback (extractive sentence scoring, simple
regex-based term extraction) so the pages work with zero API keys, matching
the existing llm.py extractive-fallback philosophy.
"""
import re
from collections import Counter
from .llm import ai_generate


def _sentences(text: str):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 20]


def _top_sentences(text: str, n: int = 5):
    sents = _sentences(text)
    if not sents:
        return []
    word_freq = Counter(re.findall(r"\w+", text.lower()))
    scored = []
    for s in sents:
        words = re.findall(r"\w+", s.lower())
        score = sum(word_freq[w] for w in words) / max(1, len(words))
        scored.append((score, s))
    scored.sort(key=lambda x: -x[0])
    return [s for _, s in scored[:n]]


def summarize_document(text: str, length: str = "medium") -> dict:
    n = {"short": 3, "medium": 6, "long": 10}.get(length, 6)

    def fallback():
        top = _top_sentences(text, n)
        return "Key points (extractive summary):\n- " + "\n- ".join(top) if top else "Not enough text to summarize."

    system = "You summarize documents clearly and concisely, preserving key facts and figures."
    prompt = f"Summarize the following document in {n} bullet points, then a 1-sentence TL;DR:\n\n{text[:8000]}"
    return ai_generate(system, prompt, fallback)


def generate_notes(text: str) -> dict:
    def fallback():
        top = _top_sentences(text, 8)
        return "Structured notes (extractive):\n" + "\n".join(f"{i+1}. {s}" for i, s in enumerate(top))

    system = "You turn source material into clean, well-organized study notes with headings and bullet points."
    prompt = f"Create structured study notes (with headings) from this content:\n\n{text[:8000]}"
    return ai_generate(system, prompt, fallback)


def generate_quiz(text: str, n_questions: int = 5) -> dict:
    def fallback():
        sents = _top_sentences(text, n_questions)
        questions = []
        for s in sents:
            words = [w for w in re.findall(r"[A-Za-z]{4,}", s)]
            if not words:
                continue
            blank_word = max(words, key=len)
            q_text = re.sub(rf"\b{re.escape(blank_word)}\b", "ـ" * len(blank_word), s, count=1)
            questions.append({"question": f"Fill in the blank: {q_text}", "answer": blank_word})
        return {"format": "fallback-cloze", "questions": questions}

    system = "You write clear multiple-choice quiz questions (4 options, 1 correct) from source material."
    prompt = (
        f"Create {n_questions} multiple-choice questions from this content. "
        "For each: question, 4 options labeled A-D, and the correct letter.\n\n" + text[:8000]
    )

    def text_fallback():
        fb = fallback()
        lines = [f"Q{i+1}. {q['question']} (Answer: {q['answer']})" for i, q in enumerate(fb["questions"])]
        return "\n".join(lines) if lines else "Not enough content to generate a quiz."

    return ai_generate(system, prompt, text_fallback)


def generate_flashcards(text: str, n_cards: int = 8) -> dict:
    def fallback():
        # naive term/definition extraction: capitalized or technical-looking terms + the sentence they appear in
        sents = _sentences(text)
        cards = []
        seen = set()
        for s in sents:
            terms = re.findall(r"\b([A-Z][a-zA-Z]{3,}(?:\s[A-Z][a-zA-Z]{3,})?)\b", s)
            for t in terms:
                if t.lower() in seen:
                    continue
                seen.add(t.lower())
                cards.append({"front": t, "back": s})
                if len(cards) >= n_cards:
                    return cards
        return cards

    def text_fallback():
        cards = fallback()
        if not cards:
            return "Not enough distinct terms found to build flashcards."
        return "\n\n".join(f"Front: {c['front']}\nBack: {c['back']}" for c in cards)

    system = "You create concise term/definition flashcards for studying source material."
    prompt = f"Create {n_cards} flashcards (Front: term/question, Back: concise answer) from this content:\n\n{text[:8000]}"
    return ai_generate(system, prompt, text_fallback)


def compare_documents(docs: dict) -> dict:
    """docs: {filename: text}"""
    def fallback():
        lines = []
        keyword_sets = {}
        for name, text in docs.items():
            kws = Counter(re.findall(r"[a-zA-Z]{4,}", text.lower()))
            keyword_sets[name] = set([w for w, _ in kws.most_common(20)])
        names = list(docs.keys())
        lines.append("Top-keyword overlap (heuristic comparison):")
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                shared = keyword_sets[names[i]] & keyword_sets[names[j]]
                lines.append(f"- {names[i]} vs {names[j]}: shared themes -> {', '.join(sorted(shared)) or 'few overlapping terms'}")
        return "\n".join(lines)

    system = "You compare multiple documents and summarize key similarities and differences."
    joined = "\n\n".join(f"=== {name} ===\n{text[:3000]}" for name, text in docs.items())
    prompt = f"Compare these documents. Summarize shared themes, then key differences, in bullet points:\n\n{joined}"
    return ai_generate(system, prompt, fallback)


def analyze_project(description: str) -> dict:
    def fallback():
        has_metrics = bool(re.search(r"\d+%|\bms\b|\bmillion\b|\busers\b", description.lower()))
        has_stack = bool(re.search(r"python|react|java|node|docker|kubernetes|sql|aws|tensorflow|pytorch", description.lower()))
        tips = []
        if not has_metrics:
            tips.append("Add measurable outcomes (latency reduced, users served, accuracy achieved, cost saved).")
        if not has_stack:
            tips.append("Name your concrete tech stack — reviewers scan for specific tools/frameworks.")
        tips.append("Frame as: Problem -> Approach -> Your specific role -> Measurable result.")
        return "Heuristic project review:\n- " + "\n- ".join(tips)

    system = "You review technical project descriptions and give feedback for making them resume/portfolio-ready."
    prompt = f"Review this project description. Give feedback on clarity, technical depth, and impact, and suggest 2-3 resume bullet points:\n\n{description[:4000]}"
    return ai_generate(system, prompt, fallback)

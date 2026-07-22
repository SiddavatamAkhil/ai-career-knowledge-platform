"""
Resume Analyzer / Resume-vs-JD Matcher / Resume Optimizer / Cover Letter
Generator — all share the same lightweight text-analysis primitives so
none of them require an API key to produce a real result.
"""
import re
from pathlib import Path
from typing import List

from .document_loader import load_document
from .llm import ai_generate

ACTION_VERBS = {
    "led", "built", "designed", "developed", "implemented", "launched",
    "optimized", "reduced", "increased", "improved", "automated", "created",
    "architected", "shipped", "migrated", "scaled", "mentored", "drove",
    "delivered", "streamlined",
}

SECTION_HEADERS = ["experience", "education", "skills", "projects",
                    "certifications", "summary", "objective"]


def extract_text_from_upload(path: str) -> str:
    """Load any supported file (txt/md/pdf/docx) and return its raw text."""
    docs = load_document(path)
    return "\n".join(d.text for d in docs)


def tokenize_keywords(text: str) -> set:
    words = re.findall(r"[a-zA-Z][a-zA-Z+.#]{1,}", text.lower())
    stop = {"the", "and", "for", "with", "that", "this", "from", "have",
            "will", "you", "your", "are", "was", "our", "their", "a", "in",
            "of", "to", "on", "as", "is", "at", "an", "be", "or"}
    return {w for w in words if w not in stop and len(w) > 2}


def detect_sections(text: str) -> dict:
    lower = text.lower()
    return {h: (h in lower) for h in SECTION_HEADERS}


def resume_quality_heuristics(text: str) -> dict:
    words = text.split()
    sentences = re.split(r"(?<=[.!?])\s+", text)
    action_verb_hits = sum(1 for w in words if w.strip(".,").lower() in ACTION_VERBS)
    quantified = len(re.findall(r"\b\d+(\.\d+)?%|\$\d+|\b\d{2,}\b", text))
    sections = detect_sections(text)
    missing_sections = [s for s, present in sections.items() if not present
                         and s in ("experience", "education", "skills")]

    score = 100
    if len(words) < 150:
        score -= 20
    if len(words) > 1200:
        score -= 10
    if action_verb_hits < 3:
        score -= 15
    if quantified < 2:
        score -= 15
    score -= 10 * len(missing_sections)
    score = max(0, min(100, score))

    return {
        "word_count": len(words),
        "sentence_count": len(sentences),
        "action_verb_hits": action_verb_hits,
        "quantified_achievements": quantified,
        "sections_detected": sections,
        "missing_sections": missing_sections,
        "heuristic_score": score,
    }


def match_resume_to_jd(resume_text: str, jd_text: str) -> dict:
    """Keyword-overlap based match — no embeddings model required, so this
    always works instantly regardless of API keys or downloaded models."""
    resume_kw = tokenize_keywords(resume_text)
    jd_kw = tokenize_keywords(jd_text)
    overlap = resume_kw & jd_kw
    missing = jd_kw - resume_kw
    match_pct = round(100 * len(overlap) / max(1, len(jd_kw)), 1)

    # keep only "meaningful" missing keywords (appear >=2 times in JD, likely real requirements)
    jd_word_list = re.findall(r"[a-zA-Z][a-zA-Z+.#]{1,}", jd_text.lower())
    freq = {}
    for w in jd_word_list:
        freq[w] = freq.get(w, 0) + 1
    important_missing = sorted(
        [w for w in missing if freq.get(w, 0) >= 2], key=lambda w: -freq[w]
    )[:20]

    return {
        "match_pct": match_pct,
        "matched_keywords": sorted(overlap)[:40],
        "missing_keywords": important_missing,
    }


def optimize_resume(resume_text: str, target_role: str = "") -> dict:
    heur = resume_quality_heuristics(resume_text)
    suggestions = []
    if heur["action_verb_hits"] < 5:
        suggestions.append(
            "Start more bullet points with strong action verbs (Led, Built, "
            "Reduced, Automated) instead of passive phrasing like 'Responsible for'."
        )
    if heur["quantified_achievements"] < 3:
        suggestions.append(
            "Add measurable impact to your bullets — percentages, dollar amounts, "
            "time saved, or scale (e.g. '...reducing latency by 30%')."
        )
    if heur["missing_sections"]:
        suggestions.append(
            f"Add a clear {', '.join(heur['missing_sections'])} section — "
            "ATS parsers and recruiters both look for standard headers."
        )
    if heur["word_count"] > 1000:
        suggestions.append("Your resume is long — aim for 1 page (~500-700 words) unless you have 10+ years of experience.")
    if heur["word_count"] < 150:
        suggestions.append("Your resume looks very short — add more detail on responsibilities and outcomes per role.")

    def fallback():
        base = "Heuristic review (no LLM key configured):\n- " + "\n- ".join(suggestions or ["Looks solid structurally — no major issues detected."])
        return base

    system = "You are an expert resume coach. Give specific, actionable rewrite suggestions."
    prompt = (
        f"Target role: {target_role or 'not specified'}\n\nResume:\n{resume_text[:6000]}\n\n"
        "Give 5-8 specific, actionable improvement suggestions (bullet points), "
        "focused on stronger action verbs, quantified impact, and clarity. "
        "Then rewrite the 3 weakest-sounding bullet points as examples."
    )
    result = ai_generate(system, prompt, fallback)
    return {"heuristics": heur, "suggestions": suggestions, **result}


def generate_cover_letter(resume_text: str, jd_text: str, company: str, role: str, tone: str = "professional") -> dict:
    match = match_resume_to_jd(resume_text, jd_text)

    def fallback():
        top_matches = ", ".join(match["matched_keywords"][:8]) or "your background"
        return (
            f"Dear Hiring Manager,\n\n"
            f"I'm excited to apply for the {role or 'open role'} position at {company or 'your company'}. "
            f"My background aligns well with what you're looking for, particularly around {top_matches}. "
            f"In my previous work I've focused on delivering measurable results and collaborating closely "
            f"with cross-functional teams, and I'd welcome the chance to bring that same approach to your team.\n\n"
            f"I'd love the opportunity to discuss how my experience matches your needs in more detail.\n\n"
            f"Sincerely,\n[Your Name]\n\n"
            f"(Heuristic template — add an OPENAI_API_KEY or ANTHROPIC_API_KEY in .env for a fully "
            f"personalized, LLM-written letter.)"
        )

    system = f"You write concise, compelling, {tone} cover letters tailored to a specific job description."
    prompt = (
        f"Company: {company or 'N/A'}\nRole: {role or 'N/A'}\n\n"
        f"Resume:\n{resume_text[:4000]}\n\nJob description:\n{jd_text[:4000]}\n\n"
        "Write a 3-4 paragraph cover letter tailored to this job, referencing specific "
        "resume experience that matches the job description. Keep it under 350 words."
    )
    result = ai_generate(system, prompt, fallback)
    return {"match": match, **result}

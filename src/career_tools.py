"""
Skill Gap Analysis / Career Roadmap / Job Recommendation / Company Prep /
Interview simulators (technical + HR). All degrade gracefully without an
API key using the static banks in knowledge_banks.py.
"""
import random
from .knowledge_banks import ROLE_SKILLS, MOCK_JOBS, TECHNICAL_QUESTIONS, HR_QUESTIONS, ROADMAP_STAGES
from .resume_tools import tokenize_keywords
from .llm import ai_generate


def skill_gap(resume_text: str, target_role: str) -> dict:
    required = set(ROLE_SKILLS.get(target_role, []))
    have = tokenize_keywords(resume_text)
    # allow multi-word skills to match via substring against raw lowercased resume text
    resume_lower = resume_text.lower()
    have_skills = {s for s in required if s in resume_lower or s in have}
    missing = sorted(required - have_skills)
    coverage = round(100 * len(have_skills) / max(1, len(required)), 1)
    return {
        "target_role": target_role,
        "required_skills": sorted(required),
        "have_skills": sorted(have_skills),
        "missing_skills": missing,
        "coverage_pct": coverage,
    }


def career_roadmap(current_level: str, target_role: str, gap: dict) -> dict:
    missing = gap.get("missing_skills", [])
    chunks = max(1, len(ROADMAP_STAGES))
    per_stage = [missing[i::chunks] for i in range(chunks)]

    def fallback():
        lines = [f"Roadmap to become a {target_role} (starting level: {current_level}):"]
        for stage, skills in zip(ROADMAP_STAGES, per_stage):
            skill_str = ", ".join(skills) if skills else "reinforce existing strengths, build a portfolio project"
            lines.append(f"- {stage}: focus on {skill_str}")
        return "\n".join(lines)

    system = "You are a career coach who creates concise, realistic skill-building roadmaps."
    prompt = (
        f"Current level: {current_level}\nTarget role: {target_role}\n"
        f"Missing skills: {', '.join(missing) or 'none identified'}\n\n"
        f"Create a {len(ROADMAP_STAGES)}-stage roadmap ({', '.join(ROADMAP_STAGES)}), "
        "with 2-3 concrete actions per stage (courses, projects, or practices), "
        "assuming ~3-6 months per stage."
    )
    result = ai_generate(system, prompt, fallback)
    return {"stages": ROADMAP_STAGES, "skills_by_stage": dict(zip(ROADMAP_STAGES, per_stage)), **result}


def recommend_jobs(resume_text: str, top_n: int = 5) -> list:
    resume_kw = tokenize_keywords(resume_text)
    resume_lower = resume_text.lower()
    scored = []
    for job in MOCK_JOBS:
        job_skills = set(job["skills"])
        hits = {s for s in job_skills if s in resume_lower or s in resume_kw}
        score = round(100 * len(hits) / max(1, len(job_skills)), 1)
        scored.append({**job, "match_pct": score, "matched_skills": sorted(hits)})
    scored.sort(key=lambda j: -j["match_pct"])
    return scored[:top_n]


def company_prep(company: str, role: str) -> dict:
    def fallback():
        return (
            f"General preparation checklist for {company or 'the company'} ({role or 'the role'}):\n"
            "- Research the company's mission, recent news, and main products.\n"
            "- Review the job description line by line and map 2-3 of your experiences to each requirement.\n"
            "- Prepare 3-5 questions to ask the interviewer about team structure and priorities.\n"
            "- Practice a concise 60-second 'tell me about yourself' pitch tailored to this role.\n"
            "- Review common technical/HR questions for this role in the Interview Practice pages.\n"
            "(Add an API key in .env for a company-specific research brief instead of this checklist.)"
        )

    system = "You are a career coach preparing a candidate for a specific company interview."
    prompt = (
        f"Company: {company}\nRole: {role}\n\n"
        "Create a concise interview-preparation brief: likely focus areas, what this "
        "company probably values culturally, and 5 tailored questions the candidate should "
        "be ready to answer, plus 3 smart questions to ask the interviewer."
    )
    return ai_generate(system, prompt, fallback)


def get_technical_questions(role: str, n: int = 5):
    bank = TECHNICAL_QUESTIONS.get(role, [])
    return random.sample(bank, min(n, len(bank))) if bank else []


def get_hr_questions(n: int = 5):
    return random.sample(HR_QUESTIONS, min(n, len(HR_QUESTIONS)))


def evaluate_answer(question: str, answer: str) -> dict:
    def fallback():
        words = len(answer.split())
        tips = []
        if words < 30:
            tips.append("Your answer is quite short — add a specific example (situation, action, result).")
        if "i" not in answer.lower().split():
            tips.append("Make sure you speak about YOUR specific contribution, not just the team's.")
        if not tips:
            tips.append("Solid length and structure — make sure you end with the measurable result.")
        return "Heuristic feedback:\n- " + "\n- ".join(tips)

    system = "You are an interview coach giving direct, constructive feedback on a spoken/written answer."
    prompt = f"Question: {question}\n\nCandidate's answer: {answer}\n\nGive 2-4 bullet points of specific, constructive feedback, and a 1-10 score."
    return ai_generate(system, prompt, fallback)

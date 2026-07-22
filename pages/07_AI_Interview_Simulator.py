import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
from src import storage
from src.ui import header, provider_badge
from src.knowledge_banks import ROLE_SKILLS
from src.career_tools import get_technical_questions, get_hr_questions, evaluate_answer

st.set_page_config(page_title="AI Interview Simulator", layout="wide")
header(" AI Interview Simulator", "A mixed mock interview: technical + behavioral questions, one at a time, with feedback.")

role = st.selectbox("Role", list(ROLE_SKILLS.keys()))

if "sim_questions" not in st.session_state or st.session_state.get("sim_role") != role:
    st.session_state.sim_questions = get_technical_questions(role, 3) + get_hr_questions(2)
    st.session_state.sim_role = role
    st.session_state.sim_idx = 0
    st.session_state.sim_log = []

if st.button("🔄 Start a new session"):
    st.session_state.sim_questions = get_technical_questions(role, 3) + get_hr_questions(2)
    st.session_state.sim_idx = 0
    st.session_state.sim_log = []
    st.rerun()

idx = st.session_state.sim_idx
questions = st.session_state.sim_questions

if idx < len(questions):
    st.progress(idx / len(questions))
    st.subheader(f"Question {idx + 1} of {len(questions)}")
    st.markdown(f"**{questions[idx]}**")
    answer = st.text_area("Your answer", key=f"ans_{idx}", height=150)
    if st.button("Submit answer", type="primary", disabled=not answer.strip()):
        with st.spinner("Evaluating..."):
            fb = evaluate_answer(questions[idx], answer)
        st.session_state.sim_log.append({"question": questions[idx], "answer": answer, "feedback": fb["text"], "provider": fb["provider"]})
        storage.append_record("interview_sessions", {"role": role, "question": questions[idx], "provider": fb["provider"]})
        st.session_state.sim_idx += 1
        st.rerun()
else:
    st.success("Session complete! Review your feedback below.")

if st.session_state.sim_log:
    st.divider()
    st.subheader("Session feedback")
    for i, entry in enumerate(st.session_state.sim_log, start=1):
        with st.container(border=True):
            st.markdown(f"**Q{i}: {entry['question']}**")
            st.caption(f"Your answer: {entry['answer'][:300]}")
            st.write(entry["feedback"])
            provider_badge(entry["provider"])

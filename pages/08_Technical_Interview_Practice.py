import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
from src import storage
from src.ui import header, provider_badge
from src.knowledge_banks import ROLE_SKILLS
from src.career_tools import get_technical_questions, evaluate_answer

st.set_page_config(page_title="Technical Interview Practice", layout="wide")
header(" Technical Interview Practice", "Role-specific technical questions with instant feedback.")

role = st.selectbox("Role", list(ROLE_SKILLS.keys()))
n = st.slider("Number of questions", 1, 5, 3)

if st.button("Generate questions", type="primary"):
    st.session_state.tech_qs = get_technical_questions(role, n)

for i, q in enumerate(st.session_state.get("tech_qs", []), start=1):
    with st.container(border=True):
        st.markdown(f"**Q{i}. {q}**")
        ans = st.text_area("Your answer", key=f"tech_ans_{i}", height=120)
        if st.button("Get feedback", key=f"tech_fb_{i}", disabled=not ans.strip()):
            fb = evaluate_answer(q, ans)
            storage.append_record("interview_sessions", {"role": role, "question": q, "provider": fb["provider"], "mode": "technical"})
            st.write(fb["text"])
            provider_badge(fb["provider"])

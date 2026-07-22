import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
from src import storage
from src.ui import header, provider_badge
from src.career_tools import get_hr_questions, evaluate_answer

st.set_page_config(page_title="HR Interview Practice", layout="wide")
header(" HR Interview Practice", "Practice common behavioral/HR questions with instant feedback.")

n = st.slider("Number of questions", 1, 8, 4)
if st.button("Generate questions", type="primary"):
    st.session_state.hr_qs = get_hr_questions(n)

for i, q in enumerate(st.session_state.get("hr_qs", []), start=1):
    with st.container(border=True):
        st.markdown(f"**Q{i}. {q}**")
        ans = st.text_area("Your answer (try the STAR method: Situation, Task, Action, Result)", key=f"hr_ans_{i}", height=120)
        if st.button("Get feedback", key=f"hr_fb_{i}", disabled=not ans.strip()):
            fb = evaluate_answer(q, ans)
            storage.append_record("interview_sessions", {"question": q, "provider": fb["provider"], "mode": "HR"})
            st.write(fb["text"])
            provider_badge(fb["provider"])

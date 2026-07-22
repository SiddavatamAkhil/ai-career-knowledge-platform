import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
import pandas as pd
from src import storage
from src.ui import header

st.set_page_config(page_title="Feedback & Reports",layout="wide")
header(" Feedback & Reports", "Tell us what to improve, and see aggregate ratings from everyone using this instance.")

with st.form("feedback_form", clear_on_submit=True):
    rating = st.slider("Overall rating", 1, 5, 4)
    feature = st.text_input("Which feature is this about? (optional)")
    comment = st.text_area("Comments")
    submitted = st.form_submit_button("Submit feedback", type="primary")
    if submitted:
        storage.append_record("feedback", {"rating": rating, "feature": feature, "comment": comment})
        st.success("Thanks for the feedback!")

st.divider()
feedback = storage.load("feedback", [])
if feedback:
    df = pd.DataFrame(feedback)
    st.metric("Average rating", round(df["rating"].mean(), 2))
    st.bar_chart(df["rating"].value_counts().sort_index())
    st.subheader("Recent comments")
    for f in reversed(feedback[-10:]):
        st.markdown(f"**{f['rating']}⭐** ({f.get('feature','general')}) — {f.get('comment','')}")
else:
    st.info("No feedback submitted yet.")

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
from src import storage
from src.ui import header

st.set_page_config(page_title="Team Workspace",  layout="wide")
header(" Team Workspace", "A shared notes board for a study group or team preparing together (local demo — everyone using this app instance shares this board).")

with st.form("post_note", clear_on_submit=True):
    name = st.text_input("Your name")
    note = st.text_area("Share a note, resource link, or update with the team")
    submitted = st.form_submit_button("Post")
    if submitted and note.strip():
        storage.append_record("team_notes", {"name": name or "Anonymous", "note": note})
        st.success("Posted!")

st.divider()
notes = storage.load("team_notes", [])
if not notes:
    st.info("No notes yet — be the first to post.")
for n in reversed(notes):
    with st.container(border=True):
        st.markdown(f"**{n['name']}** · {n.get('created_at','')}")
        st.write(n["note"])

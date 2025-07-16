import streamlit as st
from pathlib import Path

homework_pages = []

if "hw_authenticated" not in st.session_state:
    st.session_state.hw_authenticated = False

if not st.session_state.hw_authenticated:
    homework_pages = [st.Page(Path(Path.cwd() / "hw_pages" / "hw_login.py"), title="Upload Homework")]

elif st.session_state.hw_authenticated == "TA":
    homework_pages = [st.Page(Path(Path.cwd() / "hw_pages" / "ta_panel.py"), title="TA Panel")]

elif st.session_state.hw_authenticated and "hw_course" in st.session_state and "user_id" in st.session_state:
    homework_pages = [st.Page(Path(Path.cwd() / "hw_pages" / "stu_panel.py"), title="Student Panel")]

pg = st.navigation(
    {
        "Homework": homework_pages,
     }
)

pg.run()

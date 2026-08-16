"""Entry point and student-facing release navigation."""

import streamlit as st


st.set_page_config(
    page_title="OM & OR Teaching Tools",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

johnson_rule = st.Page(
    "pages/johnson_rule.py",
    title="Johnson's Rule",
    default=True,
)

navigation = st.navigation([johnson_rule], position="sidebar")
navigation.run()

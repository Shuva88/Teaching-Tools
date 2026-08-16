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
consecutive_days_off = st.Page(
    "pages/consecutive_days_off.py",
    title="Consecutive Days Off",
)

navigation = st.navigation(
    [johnson_rule, consecutive_days_off],
    position="sidebar",
)
navigation.run()

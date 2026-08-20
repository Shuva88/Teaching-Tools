"""Entry point and student-facing release navigation."""

import streamlit as st


st.set_page_config(
    page_title="OM & OR Teaching Tools",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

home = st.Page(
    "pages/home.py",
    title="Home",
    default=True,
)
johnson_rule = st.Page(
    "pages/johnson_rule.py",
    title="Johnson's Rule",
    url_path="johnsons_rule",
)
consecutive_days_off = st.Page(
    "pages/consecutive_days_off.py",
    title="Consecutive Days Off",
    url_path="consecutive_days_off",
)
single_processor_sequencing = st.Page(
    "pages/single_processor_sequencing.py",
    title="Single-Processor Sequencing",
    url_path="single_processor_sequencing",
)
clarke_wright = st.Page(
    "pages/clarke_wright.py",
    title="VRP: Clarke-Wright",
    url_path="vrp_clarke_wright",
)

navigation = st.navigation(
    {
        "Operations Management": [
            home,
            johnson_rule,
            consecutive_days_off,
            single_processor_sequencing,
            clarke_wright,
        ]
    },
    position="sidebar",
)
navigation.run()

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
simplex_algorithm = st.Page(
    "pages/simplex_algorithm.py",
    title="Simplex Algorithm - Example 1",
    url_path="simplex_algorithm",
)

operations_research_home = st.Page(
    "pages/operations_research_home.py",
    title="Home",
    url_path="operations_research",
)

operations_management_pages = [
    home,
    johnson_rule,
    consecutive_days_off,
    single_processor_sequencing,
    clarke_wright,
]

operations_research_pages = [
    operations_research_home,
    simplex_algorithm,
]
navigation = st.navigation(
    {
        "Operations Management": operations_management_pages,
        "Operations Research": operations_research_pages,
    },
    position="sidebar",
)
navigation.run()

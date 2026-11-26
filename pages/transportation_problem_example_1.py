"""Interactive transportation demonstration with a fixed shipping example."""

import streamlit as st

from algorithms.transportation import METHODS
from components.transportation import landing_tableau, page_style, playback_html


TITLE = "Transportation Problem - Example 1"
STARTED = "powerco_started"
METHOD = "powerco_selected_method"
SELECTOR = "powerco_method_radio"


def _start():
    st.session_state[METHOD] = st.session_state[SELECTOR]
    st.session_state[STARTED] = True


def _restart():
    st.session_state[STARTED] = False


started = st.session_state.get(STARTED, False)
st.markdown(page_style(started), unsafe_allow_html=True)

if started:
    title_column, controls = st.columns([4, 1], vertical_alignment="center")
    with title_column:
        st.markdown(f"## {TITLE}")
    with controls:
        st.button("Restart", on_click=_restart, key="powerco_restart")
    # The player resizes its host. Give that host a separate lifetime from the landing table.
    with st.container(key="transportation_playback"):
        st.iframe(playback_html(st.session_state[METHOD]), height=460)
else:
    st.title(TITLE)
    st.html(f'<div class="transportation-input-frame">{landing_tableau()}</div>')
    st.markdown(
        "A distributor ships cartons from three warehouses (S1–S3) to four stores (D1–D4). "
        "The table shows shipping costs per carton (in rupees), supply, and demand. "
        "Supply and demand both total **125 cartons**, "
        "so the problem is **balanced**.\n\n"
        "If demand exceeds supply, add a **dummy supply row**. If supply exceeds demand, "
        "add a **dummy demand column**. Use the difference between the totals as the dummy "
        "supply or demand, with a unit cost of **zero** in every dummy cell. "
        "Choose a method to build a shipping plan, then check whether it has the lowest cost."
    )
    st.radio(
        "Method", tuple(METHODS), format_func=METHODS.__getitem__,
        index=tuple(METHODS).index(st.session_state.get(METHOD, "NWCR")), key=SELECTOR,
    )
    st.button("Start Demonstration", type="primary", on_click=_start, key="powerco_start")

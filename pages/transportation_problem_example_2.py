"""VAM and UV iterations for the second transportation example."""

import streamlit as st

from algorithms.transportation import METHODS, VARIANT_COSTS
from components.transportation import landing_tableau, page_style, playback_html


TITLE = "Transportation Problem - Example 2"
STARTED = "transport2_started"


def _set_started(started: bool):
    st.session_state[STARTED] = started


started = st.session_state.get(STARTED, False)
st.markdown(page_style(started), unsafe_allow_html=True)
if started:
    title_column, controls = st.columns([4, 1], vertical_alignment="center")
    with title_column:
        st.markdown(f"## {TITLE}")
    with controls:
        st.button("Restart", on_click=_set_started, args=(False,), key="transport2_restart")
    with st.container(key="transport2_playback"):
        st.iframe(playback_html("VAM", example=2), height=460)
else:
    st.title(TITLE)
    st.html(f'<div class="transportation-input-frame">{landing_tableau(VARIANT_COSTS)}</div>')
    st.markdown(
        "The cost of sending a carton from S2 to D4 has fallen from ₹7 to ₹5. "
        "Supply and demand still total **125 cartons** each, so the problem is **balanced**.\n\n"
        f"Start with **{METHODS['VAM']}**. Then use the **UV method** to test the allocation "
        "and improve it while a negative reduced cost remains."
    )
    st.button("Start Demonstration", type="primary", on_click=_set_started, args=(True,), key="transport2_start")

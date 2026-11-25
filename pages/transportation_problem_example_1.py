"""Interactive transportation demonstration with a fixed shipping example."""

import streamlit as st

from algorithms.transportation import METHODS
from components.transportation import landing_tableau, playback_html


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
st.markdown(
    """
<style>
.block-container {
    max-width: 1250px;
    padding-top: 3.75rem !important;
    padding-bottom: 0.5rem !important;
}
.stMain { overflow: __OVERFLOW__; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] { gap: .4rem; }
[data-testid="stElementContainer"]:has(style) {display: none;}
.block-container h1, .block-container h2 {line-height: 1.15; padding-top: 0; padding-bottom: .25rem;}
.block-container h1 {font-size: 2.15rem;}
.block-container h2 {font-size: 1.65rem;}
.transportation-input-frame {padding-top: 1.125rem;}
.transportation-input {
    width: min(100%, 660px);
    table-layout: fixed;
    border-collapse: collapse;
    font-size: clamp(.82rem, 2.3vw, 1rem);
}
.transportation-input th, .transportation-input td {
    text-align: center !important;
    border: 1px solid #cbd4e2 !important;
    padding: .4rem .15rem !important;
}
.transportation-input th {background: #e8eef8; color: #273a57;}
.transportation-input td {background: #fcfdff; color: #263248;}
.transportation-input tr:nth-child(even) td {background: #f5f7fc;}
.transportation-input tr > :last-child, .transportation-input tfoot th {background: #d9e4f4;}
.st-key-powerco_start button {background: #51447c; border-color: #51447c; color: white;}
.st-key-powerco_start button:hover {background: #413565; border-color: #413565; color: white;}
@media (max-width: 800px) {
    .block-container {padding-top: 4rem !important;}
    .block-container h1 {font-size: 1.55rem;}
    .block-container h2 {font-size: 1.25rem;}
}
</style>
""".replace("__OVERFLOW__", "clip" if started else "auto"),
    unsafe_allow_html=True,
)

if started:
    title_column, controls = st.columns([4, 1], vertical_alignment="center")
    with title_column:
        st.markdown(f"## {TITLE}")
    with controls:
        st.button("Restart", on_click=_restart, key="powerco_restart")
    st.iframe(playback_html(st.session_state[METHOD]), height=460)
else:
    st.title(TITLE)
    st.html(f'<div class="transportation-input-frame">{landing_tableau()}</div>')
    st.markdown(
        "A distributor ships cartons from three warehouses (S1–S3) to four stores (D1–D4). "
        "The table shows the shipping cost per carton in rupees, the supply at each warehouse, "
        "and the demand at each store. Supply and demand both total **125 cartons**. "
        "Choose a method to build a shipping plan, then check whether it has the lowest cost."
    )
    st.radio(
        "Method", tuple(METHODS), format_func=METHODS.__getitem__,
        index=tuple(METHODS).index(st.session_state.get(METHOD, "NWCR")), key=SELECTOR,
    )
    st.button("Start Demonstration", type="primary", on_click=_start, key="powerco_start")

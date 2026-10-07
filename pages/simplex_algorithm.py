"""Fixed worked-example demonstration of the primal simplex algorithm."""

from __future__ import annotations

import streamlit as st

from algorithms.simplex import build_simplex_demonstration
from components.simplex import build_simplex_demonstration_html


DEMONSTRATION = build_simplex_demonstration()
STARTED_KEY = "simplex_fixed_example_started"


def _initialize_state() -> None:
    if STARTED_KEY not in st.session_state:
        st.session_state[STARTED_KEY] = False


def _start() -> None:
    st.session_state[STARTED_KEY] = True


def _restart() -> None:
    st.session_state[STARTED_KEY] = False


def _render_problem_view() -> None:
    st.title("Simplex Algorithm - Example 1")
    st.caption("Maximization problem with less-than-or-equal-to constraints.")

    model_column, _ = st.columns([1.25, 0.75], gap="large")
    with model_column:
        st.latex(
            r"\begin{aligned}"
            r"\max\quad & Z = 5x_1 + 4x_2\\[-2pt]"
            r"\text{s.t.}\quad & 6x_1 + 4x_2 \le 24\\"
            r"& x_1 + 2x_2 \le 6\\"
            r"& -x_1 + x_2 \le 1\\"
            r"& x_2 \le 2\\"
            r"& x_1,x_2 \ge 0"
            r"\end{aligned}"
        )

    st.markdown(
        "1. **Start from an initial basic feasible solution (BFS)**, "
        "i.e., a corner (extreme) point of the feasible region.\n\n"
        "2. **Move to a neighbouring BFS such that $Z$ improves.** "
        "A current nonbasic variable becomes basic (enters the basis), "
        "and a current basic variable becomes nonbasic (leaves the basis).\n\n"
        "3. **Continue until no neighbouring BFS can improve $Z$.** "
        "The current BFS is then optimal."
    )
    st.button(
        "Start Demonstration",
        type="primary",
        on_click=_start,
        width="content",
        key="simplex_start",
    )


def _render_demonstration() -> None:
    title_column, control_column = st.columns([4, 1.15], vertical_alignment="center")
    with title_column:
        st.markdown("## Simplex Algorithm - Example 1")
    with control_column:
        st.button(
            "Restart Demonstration",
            on_click=_restart,
            width="stretch",
            key="simplex_restart",
        )

    st.iframe(
        build_simplex_demonstration_html(DEMONSTRATION),
        height=600,
    )


_initialize_state()

st.markdown(
    """
<style>
.block-container {
    max-width: 1380px;
    padding-top: 3.75rem !important;
    padding-bottom: 0 !important;
}
.stMain {
    overflow: __PAGE_OVERFLOW__;
}
.block-container h2 {
    padding: 0 !important;
    margin-top: 0 !important;
    margin-bottom: 0.25rem !important;
    font-size: 1.65rem !important;
    line-height: 1.15 !important;
}
.block-container h1 {
    font-size: 2.15rem !important;
    line-height: 1.12 !important;
    margin-bottom: 0.35rem !important;
}
[data-testid="stHorizontalBlock"] {
    gap: 0.75rem;
}
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {
    gap: 0.375rem;
}
[data-testid="stElementContainer"]:has(style) {
    display: none;
}
[data-testid="stIFrame"] {
    display: block;
    height: calc(100dvh - 7rem);
    min-height: 0;
}
@media (max-width: 800px) {
    .block-container {padding-top: 4rem !important;}
    .block-container h2 {font-size: 1.25rem !important;}
    .block-container h1 {font-size: 1.55rem !important;}
}
</style>
""".replace(
        "__PAGE_OVERFLOW__",
        "clip" if st.session_state[STARTED_KEY] else "auto",
    ),
    unsafe_allow_html=True,
)

if st.session_state[STARTED_KEY]:
    _render_demonstration()
else:
    _render_problem_view()

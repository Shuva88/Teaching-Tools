"""Click-driven Clarke-Wright savings demonstration for the fixed example."""

from __future__ import annotations

import streamlit as st

from algorithms.clarke_wright import (
    PPT_CAPACITY,
    PPT_DEMANDS,
    PPT_SAVINGS,
    initialize_routes,
    order_final_routes_for_display,
    run_clarke_wright_from_savings,
)
from components.clarke_wright import build_click_demonstration_html


RESULT = run_clarke_wright_from_savings(
    tuple(PPT_DEMANDS),
    PPT_DEMANDS,
    PPT_SAVINGS,
    PPT_CAPACITY,
)
INITIAL_ROUTES = initialize_routes(PPT_DEMANDS)
FINAL_ROUTES = order_final_routes_for_display(RESULT.final_routes)

STARTED_KEY = "clarke_wright_click_v2_started"


def _initialize_state() -> None:
    if STARTED_KEY not in st.session_state:
        st.session_state[STARTED_KEY] = False


def _start() -> None:
    st.session_state[STARTED_KEY] = True


def _restart() -> None:
    st.session_state[STARTED_KEY] = False


def _render_problem_view() -> None:
    st.title("VRP: Clarke-Wright Savings Method")
    st.caption("Fixed classroom example · Depot 0 · 23 customers · Capacity C = 100")
    st.markdown(
        "A third-party logistics (3PL) provider dispatches vehicles from a "
        "central depot to deliver orders to 23 customers. Each vehicle can carry "
        "at most 100 units. Clarke-Wright savings combines separate out-and-back "
        "trips into feasible multi-customer routes."
    )

    data_column, rule_column = st.columns([1.05, 1], gap="large")
    with data_column:
        st.markdown("#### Fixed customer demands")
        demand_rows = []
        for first_customer in range(1, 13):
            second_customer = first_customer + 12
            demand_rows.append(
                {
                    "Customer": first_customer,
                    "Demand": PPT_DEMANDS[str(first_customer)],
                    "Customer ": second_customer if second_customer <= 23 else None,
                    "Demand ": (
                        PPT_DEMANDS[str(second_customer)]
                        if second_customer <= 23
                        else None
                    ),
                }
            )
        st.dataframe(
            demand_rows,
            hide_index=True,
            width="stretch",
            height=390,
        )

    with rule_column:
        st.markdown("#### How the savings method proceeds")
        st.markdown("**1. Calculate the savings for each pair (i, j) of nodes:**")
        st.latex(r"S_{ij}=d_{0i}+d_{0j}-d_{ij}")
        st.caption(
            "In this illustration, the savings values are given. In practice, "
            "they must be computed from travel distances obtained from the "
            "location coordinates of the nodes."
        )
        st.markdown(
            "**2. Obtain the savings list with the node pairs sorted in "
            "descending order.**"
        )
        st.markdown(
            "**3. Proceed down the savings list and accept a candidate link "
            "only when:**"
        )
        st.markdown(
            "1. The two customers are in **different routes**.\n"
            "2. Both customers are at **route ends**.\n"
            "3. Their combined route load is **at most 100**."
        )
        st.button(
            "Start Demonstration",
            type="primary",
            on_click=_start,
            width="stretch",
            key="clarke_wright_start",
        )


def _render_demonstration() -> None:
    title_column, control_column = st.columns([4, 1.15], vertical_alignment="center")
    with title_column:
        st.markdown("## VRP: Clarke-Wright Savings Method")
    with control_column:
        st.button(
            "Restart Demonstration",
            on_click=_restart,
            width="stretch",
            key="clarke_wright_restart",
        )

    st.iframe(
        build_click_demonstration_html(
            RESULT.decisions,
            INITIAL_ROUTES,
            FINAL_ROUTES,
            PPT_DEMANDS,
            PPT_CAPACITY,
        ),
        height=565,
    )


st.markdown(
    """
<style>
.block-container {max-width: 1380px; padding-top: 3.75rem !important; padding-bottom: 0.6rem;}
@media (max-width: 800px) {
    .block-container {padding-top: 4rem !important;}
}
</style>
""",
    unsafe_allow_html=True,
)

_initialize_state()
if st.session_state[STARTED_KEY]:
    _render_demonstration()
else:
    _render_problem_view()

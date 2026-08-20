"""Classroom demonstration for scheduling two consecutive days off."""

from __future__ import annotations

from html import escape

import streamlit as st

from algorithms.consecutive_days_off import (
    DAYS,
    RESTAURANT_REQUIREMENTS,
    DaysOffStep,
    build_employee_schedule,
    calculate_daily_staffing,
    calculate_excess_staffing,
    generate_consecutive_days_off_steps,
)
from components.staffing import make_staffing_chart


STEPS = generate_consecutive_days_off_steps(RESTAURANT_REQUIREMENTS)
SCHEDULE = build_employee_schedule(STEPS)
SCHEDULED_STAFF = calculate_daily_staffing(SCHEDULE)
EXCESS_STAFF = calculate_excess_staffing(
    RESTAURANT_REQUIREMENTS, SCHEDULED_STAFF
)

STARTED_KEY = "days_off_demo_started"
PHASE_KEY = "days_off_demo_phase"
RESULTS_KEY = "days_off_results_view"
TOTAL_PHASES = len(STEPS) * 2


def _initialize_state() -> None:
    if STARTED_KEY not in st.session_state:
        st.session_state[STARTED_KEY] = False
    if PHASE_KEY not in st.session_state:
        st.session_state[PHASE_KEY] = 0
    if RESULTS_KEY not in st.session_state:
        st.session_state[RESULTS_KEY] = False


def _start() -> None:
    st.session_state[STARTED_KEY] = True
    st.session_state[PHASE_KEY] = 0
    st.session_state[RESULTS_KEY] = False


def _previous() -> None:
    st.session_state[PHASE_KEY] = max(0, st.session_state[PHASE_KEY] - 1)
    st.session_state[RESULTS_KEY] = False


def _next() -> None:
    st.session_state[PHASE_KEY] = min(
        TOTAL_PHASES, st.session_state[PHASE_KEY] + 1
    )


def _restart() -> None:
    st.session_state[STARTED_KEY] = False
    st.session_state[PHASE_KEY] = 0
    st.session_state[RESULTS_KEY] = False


def _show_results() -> None:
    st.session_state[RESULTS_KEY] = True


def _return_to_final_step() -> None:
    st.session_state[RESULTS_KEY] = False


def _format_pair(days: tuple[str, str]) -> str:
    return f"{days[0]}–{days[1]}"


def _render_requirement_grid(
    values: tuple[int, ...],
    step: DaysOffStep | None = None,
    phase: str | None = None,
) -> None:
    included_days = set(step.included_days) if step and phase == "identify" else set()
    selected_days = set(step.selected_pair.days) if step else set()
    cells = []
    for day, value in zip(DAYS, values):
        classes = ["days-off-day-card"]
        if day in included_days:
            classes.append("included")
        if phase == "identify" and day in selected_days:
            classes.append("selected-off")
        elif phase == "apply" and day in selected_days:
            classes.append("off-day")
        elif phase == "apply" and step is not None:
            classes.append("work-day")
        if value == 0:
            classes.append("zero")
        cells.append(
            f"<div class='{' '.join(classes)}'>"
            f"<span>{escape(day)}</span><strong>{value}</strong>"
            "</div>"
        )
    st.markdown(
        "<div class='days-off-grid'>" + "".join(cells) + "</div>",
        unsafe_allow_html=True,
    )


def _render_pair_options(step: DaysOffStep) -> None:
    best_days = {option.days for option in step.best_pairs}
    cards = []
    for option in step.eligible_pairs:
        classes = ["days-off-pair-card"]
        if option.days in best_days:
            classes.append("best")
        if option.days == step.selected_pair.days:
            classes.append("chosen")
        label = "chosen" if option.days == step.selected_pair.days else "eligible"
        cards.append(
            f"<div class='{' '.join(classes)}'>"
            f"<strong>{escape(_format_pair(option.days))}</strong>"
            f"<span>pair total = {option.total}</span><small>{label}</small></div>"
        )
    st.markdown(
        "<div class='days-off-pair-grid'>" + "".join(cards) + "</div>",
        unsafe_allow_html=True,
    )


def _render_work_pattern(step: DaysOffStep) -> None:
    off_days = set(step.selected_pair.days)
    cells = []
    for day in DAYS:
        status = "Off" if day in off_days else "Work"
        status_class = "off" if day in off_days else "work"
        cells.append(
            f"<div class='days-off-pattern-cell {status_class}'>"
            f"<span>{escape(day)}</span><strong>{status}</strong></div>"
        )
    st.markdown(
        "<div class='days-off-pattern'>" + "".join(cells) + "</div>",
        unsafe_allow_html=True,
    )


def _render_assignments_so_far(completed_assignments: int) -> None:
    if completed_assignments == 0:
        st.caption("No partner has been assigned yet.")
        return
    chips = [
        f"<span class='days-off-chip'>P{step.employee_number}: "
        f"{escape(_format_pair(step.selected_pair.days))}</span>"
        for step in STEPS[:completed_assignments]
    ]
    st.markdown(
        "<div class='days-off-chips'>" + "".join(chips) + "</div>",
        unsafe_allow_html=True,
    )


def _render_identification(step: DaysOffStep) -> None:
    st.markdown("##### 1. Identify the days-off pair")
    st.markdown(
        "Locate at least two consecutive days among the smallest requirements. "
        f"Move from the smallest requirement upward and highlight all days "
        f"through **{step.threshold}**. The highlighted set now contains at least "
        "one consecutive pair."
    )
    _render_pair_options(step)
    if step.scheduler_tie_assumption:
        alternatives = ", ".join(
            _format_pair(option.days) for option in step.best_pairs
        )
        st.warning(
            f"Lowest pair-total tie: {alternatives}. The demonstration uses the "
            f"earliest pair in Monday-to-Sunday order, so choose "
            f"**{_format_pair(step.selected_pair.days)}**."
        )
    elif len(step.eligible_pairs) > 1:
        st.info(
            f"Choose **{_format_pair(step.selected_pair.days)}** because its "
            f"pair total, **{step.selected_pair.total}**, is the smallest."
        )
    else:
        st.info(
            f"The first available consecutive pair is "
            f"**{_format_pair(step.selected_pair.days)}**."
        )
    st.caption("Click Next Step to assign the five working days and update demand.")


def _render_application(step: DaysOffStep) -> None:
    st.markdown("##### 2. Assign workdays and update requirements")
    st.markdown(
        f"Partner **{step.employee_number}** is off on "
        f"**{_format_pair(step.selected_pair.days)}** and works on the other five days."
    )
    _render_work_pattern(step)
    changes = [
        f"{day}: {before}→{after}"
        for day, before, after in zip(DAYS, step.before, step.after)
        if before != after
    ]
    st.markdown(
        "Subtract 1 from each positive requirement on a working day:  \n"
        f"`{', '.join(changes)}`"
    )
    st.caption(
        "The days-off requirements remain unchanged; zero requirements cannot "
        "fall below zero."
    )


def _render_problem_view() -> None:
    st.title("Scheduling Consecutive Days Off")
    st.caption("Demonstration mode · Restaurant delivery hub")
    st.markdown(
        "A delivery hub needs a different minimum number of partners each day. "
        "Every partner works **five days** and receives **two consecutive days "
        "off**. Find a schedule that covers the demand."
    )

    columns = st.columns([1.05, 1], gap="large")
    with columns[0]:
        st.markdown("#### Minimum partners required")
        _render_requirement_grid(RESTAURANT_REQUIREMENTS)
        st.info(
            "Allowed days-off pairs run from **Mon–Tue** through **Sat–Sun**. "
            "Sun–Mon is not used in this fixed example."
        )
    with columns[1]:
        st.markdown("#### Procedure")
        st.markdown(
            """
1. List the minimum number of employees required for each day of the week.
2. Locate at least two consecutive days having the smallest requirements. Start with the smallest requirement, then the next smallest, and continue until at least two days are consecutive.
3. Highlight those two consecutive days. If several pairs are possible, first choose the pair with the lowest total requirement. If totals still tie, apply the scheduling convention; this demonstration uses the earliest pair in Monday-to-Sunday order.
4. Give the next employee the highlighted days off and assign work on all other days. Subtract 1 from each positive requirement on a day that the employee works.
5. Repeat with the new requirements for the next employee until all requirements become zero.
            """
        )
        st.button(
            "Start Demonstration",
            type="primary",
            on_click=_start,
            width="stretch",
        )


def _render_algorithm_view(
    step: DaysOffStep | None,
    phase: str | None,
    completed_phases: int,
) -> None:
    st.markdown(
        "<h2 class='days-off-workspace-title'>"
        "Scheduling Consecutive Days Off</h2>",
        unsafe_allow_html=True,
    )
    st.caption("Restaurant delivery hub · Build one partner assignment at a time")

    if step is None:
        displayed_requirements = RESTAURANT_REQUIREMENTS
        completed_assignments = 0
    elif phase == "identify":
        displayed_requirements = step.before
        completed_assignments = step.employee_number - 1
    else:
        displayed_requirements = step.after
        completed_assignments = step.employee_number

    columns = st.columns([1.08, 1], gap="large")
    with columns[0]:
        st.markdown("#### Current requirements")
        _render_requirement_grid(displayed_requirements, step, phase)
        st.markdown("##### Completed assignments · days off")
        _render_assignments_so_far(completed_assignments)

    with columns[1]:
        st.progress(
            completed_phases / TOTAL_PHASES,
            text=(
                "Ready to assign Partner 1"
                if step is None
                else f"Partner {step.employee_number} of {len(STEPS)} · "
                + (
                    "select the consecutive days-off pair"
                    if phase == "identify"
                    else "apply the assignment"
                )
            ),
        )
        if step is None:
            st.info(
                "Click **Next Step** to identify the consecutive days-off pair "
                "for Partner 1."
            )
        elif phase == "identify":
            _render_identification(step)
        else:
            _render_application(step)

        controls = st.columns(3)
        with controls[0]:
            st.button(
                "Previous",
                on_click=_previous,
                disabled=completed_phases == 0,
                width="stretch",
            )
        with controls[1]:
            if completed_phases == TOTAL_PHASES:
                st.button(
                    "View Results",
                    type="primary",
                    on_click=_show_results,
                    width="stretch",
                )
            else:
                st.button(
                    "Next Step",
                    type="primary",
                    on_click=_next,
                    width="stretch",
                )
        with controls[2]:
            st.button("Restart", on_click=_restart, width="stretch")


def _render_results() -> None:
    st.title("Scheduling Consecutive Days Off: Results")
    st.caption("Restaurant delivery hub · Completed demonstration")
    st.success(
        "The schedule uses **8 partners**. This is minimum because Friday alone "
        "requires 8 partners; no schedule can use fewer than 8."
    )

    controls = st.columns([1.3, 1.3, 5])
    with controls[0]:
        st.button(
            "Back to final step",
            on_click=_return_to_final_step,
            width="stretch",
        )
    with controls[1]:
        st.button("Restart", on_click=_restart, width="stretch")

    schedule_rows = []
    for assignment in SCHEDULE:
        off_days = set(assignment.days_off)
        schedule_rows.append(
            {
                "Partner": f"Partner {assignment.employee_number}",
                **{day: "Off" if day in off_days else "Work" for day in DAYS},
                "Consecutive days off": _format_pair(assignment.days_off),
            }
        )
    coverage_rows = [
        {
            "Day": day,
            "Required": required,
            "Scheduled": scheduled,
            "Excess": excess,
        }
        for day, required, scheduled, excess in zip(
            DAYS, RESTAURANT_REQUIREMENTS, SCHEDULED_STAFF, EXCESS_STAFF
        )
    ]

    schedule_tab, coverage_tab, calculations_tab = st.tabs(
        ["Final schedule", "Staffing check", "Calculations"]
    )
    with schedule_tab:
        st.dataframe(
            schedule_rows,
            hide_index=True,
            width="stretch",
            column_config={
                "Partner": st.column_config.TextColumn(width="small"),
                "Consecutive days off": st.column_config.TextColumn(width="medium"),
            },
        )
        st.caption("Each partner has exactly five Work days and two consecutive Off days.")

    with coverage_tab:
        chart_column, table_column = st.columns([1.25, 1], gap="large")
        with chart_column:
            st.plotly_chart(
                make_staffing_chart(DAYS, RESTAURANT_REQUIREMENTS, SCHEDULED_STAFF),
                width="stretch",
                config={"displayModeBar": False, "responsive": True},
            )
        with table_column:
            st.dataframe(coverage_rows, hide_index=True, width="stretch")
            st.info(
                "Scheduled staffing meets or exceeds the requirement on every day."
            )

    with calculations_tab:
        st.markdown(
            f"""
**Minimum number of partners**

`largest daily requirement = max(6, 3, 5, 4, 8, 4, 4) = 8`

The constructed schedule uses 8 partners, so it meets this lower bound and is minimum.

**Daily scheduled staffing**

`Mon–Sun = ({', '.join(map(str, SCHEDULED_STAFF))})`

**Daily excess staffing**

`scheduled − required = ({', '.join(map(str, EXCESS_STAFF))})`

**Weekly partner-days**

`8 partners × 5 working days = 40 partner-days`

`total minimum demand = {' + '.join(map(str, RESTAURANT_REQUIREMENTS))} = {sum(RESTAURANT_REQUIREMENTS)} partner-days`

`total excess = 40 − {sum(RESTAURANT_REQUIREMENTS)} = {sum(EXCESS_STAFF)} partner-days`
            """
        )


st.markdown(
    """
<style>
.block-container {max-width: 1240px; padding-top: 3.75rem !important; padding-bottom: 1.5rem;}
.days-off-workspace-title {margin-top: 0; padding-top: 0;}
.days-off-grid {
    display: grid;
    grid-template-columns: repeat(7, minmax(60px, 1fr));
    gap: 0.36rem;
    margin: 0.25rem 0 0.7rem;
}
.days-off-day-card {
    min-height: 78px;
    border: 1px solid rgba(128, 128, 128, 0.35);
    border-radius: 0.5rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: rgba(128, 128, 128, 0.05);
}
.days-off-day-card span {font-size: 0.82rem; font-weight: 600;}
.days-off-day-card strong {font-size: 1.45rem; line-height: 1.35;}
.days-off-day-card.included {background: #FFF4BF; color: #3B2F00;}
.days-off-day-card.selected-off {box-shadow: inset 0 0 0 3px #B45309;}
.days-off-day-card.work-day {background: rgba(0, 114, 178, 0.11);}
.days-off-day-card.off-day {background: rgba(230, 159, 0, 0.20); color: #5A3D00;}
.days-off-day-card.zero {opacity: 0.62;}
.days-off-pair-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(100px, 1fr));
    gap: 0.34rem;
    margin: 0.35rem 0 0.6rem;
}
.days-off-pair-card {
    border: 1px solid rgba(128, 128, 128, 0.32);
    border-radius: 0.45rem;
    padding: 0.34rem 0.42rem;
    display: flex;
    flex-direction: column;
    line-height: 1.25;
}
.days-off-pair-card span {font-size: 0.78rem;}
.days-off-pair-card small {font-size: 0.66rem; opacity: 0.68;}
.days-off-pair-card.best {background: #FFF4BF; color: #3B2F00;}
.days-off-pair-card.chosen {box-shadow: inset 0 0 0 2px #B45309;}
.days-off-pattern {
    display: grid;
    grid-template-columns: repeat(7, minmax(54px, 1fr));
    gap: 0.3rem;
    margin: 0.35rem 0 0.7rem;
}
.days-off-pattern-cell {
    border-radius: 0.4rem;
    padding: 0.35rem 0.2rem;
    text-align: center;
}
.days-off-pattern-cell span {display: block; font-size: 0.72rem;}
.days-off-pattern-cell strong {font-size: 0.86rem;}
.days-off-pattern-cell.work {background: rgba(0, 114, 178, 0.12);}
.days-off-pattern-cell.off {background: rgba(230, 159, 0, 0.23); color: #5A3D00;}
.days-off-chips {display: flex; flex-wrap: wrap; gap: 0.34rem; margin-top: 0.2rem;}
.days-off-chip {
    border: 1px solid rgba(128, 128, 128, 0.30);
    border-radius: 999px;
    padding: 0.2rem 0.48rem;
    font-size: 0.78rem;
    background: rgba(128, 128, 128, 0.07);
}
@media (max-width: 800px) {
    .block-container {padding-top: 4rem !important;}
    .days-off-grid, .days-off-pattern {grid-template-columns: repeat(4, 1fr);}
    .days-off-pair-grid {grid-template-columns: repeat(2, 1fr);}
    .days-off-day-card {min-height: 68px;}
}
</style>
""",
    unsafe_allow_html=True,
)

_initialize_state()
completed_phases = st.session_state[PHASE_KEY]
if completed_phases:
    current_step = STEPS[(completed_phases - 1) // 2]
    current_phase = "identify" if completed_phases % 2 == 1 else "apply"
else:
    current_step = None
    current_phase = None

if not st.session_state[STARTED_KEY]:
    _render_problem_view()
elif st.session_state[RESULTS_KEY]:
    _render_results()
else:
    _render_algorithm_view(current_step, current_phase, completed_phases)

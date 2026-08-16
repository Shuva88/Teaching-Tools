"""Classroom demonstration page for Johnson's Rule."""

from __future__ import annotations

from html import escape

import streamlit as st

from algorithms.johnson import (
    ORIGINAL_SEQUENCE,
    PRINT_SHOP_JOBS,
    DecisionStep,
    Metrics,
    Schedule,
    build_two_resource_schedule,
    calculate_metrics,
    generate_johnson_steps,
)
from components.gantt import make_gantt_chart


STEPS = generate_johnson_steps(PRINT_SHOP_JOBS)
JOHNSON_SEQUENCE = tuple(
    job for job in STEPS[-1].partial_sequence if job is not None
)
JOHNSON_SCHEDULE = build_two_resource_schedule(JOHNSON_SEQUENCE, PRINT_SHOP_JOBS)
ORIGINAL_SCHEDULE = build_two_resource_schedule(ORIGINAL_SEQUENCE, PRINT_SHOP_JOBS)
JOHNSON_METRICS = calculate_metrics(JOHNSON_SCHEDULE, PRINT_SHOP_JOBS)
ORIGINAL_METRICS = calculate_metrics(ORIGINAL_SCHEDULE, PRINT_SHOP_JOBS)

STARTED_KEY = "johnson_demo_started"
PHASE_KEY = "johnson_demo_phase"
RESULTS_KEY = "johnson_results_view"
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


def _resource_short_name(resource: int) -> str:
    return "Printing / Photocopying" if resource == 1 else "Binding / Finishing"


def _render_processing_table(
    current_step: DecisionStep | None, current_phase: str | None
) -> None:
    placed_jobs = set()
    highlighted_cells = set()
    selected_cell = None

    if current_step is not None:
        if current_phase == "place":
            placed_sequence = current_step.partial_sequence
        elif current_step.number > 1:
            placed_sequence = STEPS[current_step.number - 2].partial_sequence
        else:
            placed_sequence = (None,) * len(PRINT_SHOP_JOBS)

        placed_jobs = {job for job in placed_sequence if job is not None}

    if current_step is not None and current_phase == "identify":
        highlighted_cells = {
            (candidate.job, candidate.resource)
            for candidate in current_step.tied_candidates
        }
        selected_cell = (
            current_step.selected_job,
            current_step.selected_resource,
        )

    rows = []
    for job in PRINT_SHOP_JOBS:
        row_class = " class='placed-job'" if job.name in placed_jobs else ""
        cells = []
        for resource, value in ((1, job.resource_1), (2, job.resource_2)):
            classes = []
            if (job.name, resource) in highlighted_cells:
                classes.append("minimum-cell")
            if (job.name, resource) == selected_cell:
                classes.append("selected-cell")
            class_attribute = f" class='{' '.join(classes)}'" if classes else ""
            cells.append(f"<td{class_attribute}>{value}</td>")
        rows.append(
            f"<tr{row_class}><th scope='row'>{escape(job.name)}</th>"
            + "".join(cells)
            + "</tr>"
        )

    table_html = """
    <div class="johnson-table-wrap">
      <table class="johnson-table">
        <thead>
          <tr>
            <th scope="col">Job</th>
            <th scope="col">Printing / Photocopying<br><span>(minutes)</span></th>
            <th scope="col">Binding / Finishing<br><span>(minutes)</span></th>
          </tr>
        </thead>
        <tbody>
    """ + "".join(rows) + """
        </tbody>
      </table>
    </div>
    """
    st.markdown(table_html, unsafe_allow_html=True)


def _render_partial_sequence(partial_sequence: tuple[str | None, ...]) -> None:
    slots = []
    for position, job in enumerate(partial_sequence, start=1):
        value = escape(job) if job is not None else "—"
        filled_class = " filled" if job is not None else ""
        slots.append(
            f"<div class='sequence-slot{filled_class}'>"
            f"<span class='position-label'>Position {position}</span>"
            f"<strong>{value}</strong></div>"
        )
    st.markdown(
        "<div class='sequence-slots'>" + "".join(slots) + "</div>",
        unsafe_allow_html=True,
    )


def _render_identification(step: DecisionStep) -> None:
    if len(step.tied_candidates) > 1:
        tied_descriptions = [
            f"Job {candidate.job} on {_resource_short_name(candidate.resource)}"
            for candidate in step.tied_candidates
        ]
        st.warning(
            f"Tie at {step.minimum_time} minutes: "
            + " and ".join(tied_descriptions)
            + ". Either tied choice preserves Johnson optimality. "
            + f"Using the original table order, select Job {step.selected_job}."
        )
    else:
        st.info(
            f"The smallest remaining processing time is {step.minimum_time} minutes: "
            f"Job {step.selected_job} on "
            f"{_resource_short_name(step.selected_resource)}."
        )

    st.caption(
        "Step 2 is complete. Click Next Step to decide where the selected job "
        "should be placed."
    )


def _render_placement(step: DecisionStep) -> None:

    direction = "beginning" if step.placement == "earliest" else "end"
    st.markdown(
        f"The selected time is on **Resource {step.selected_resource}**, so place "
        f"**Job {step.selected_job}** in the **{step.placement} available position** "
        f"from the {direction}: position **{step.position + 1}**."
    )
    st.caption(
        f"Job {step.selected_job} has now been added to the partial sequence and "
        "greyed out in the processing-time table."
    )


def _format_sequence(sequence: tuple[str, ...]) -> str:
    return " – ".join(sequence)


def _render_sequence_calculations(
    heading: str,
    sequence: tuple[str, ...],
    schedule: Schedule,
    metrics: Metrics,
) -> None:
    job_by_name = {job.name: job for job in PRINT_SHOP_JOBS}
    resource_1_times = [job_by_name[name].resource_1 for name in sequence]
    resource_2_times = [job_by_name[name].resource_2 for name in sequence]
    resource_2_completions = [
        operation.finish
        for operation in schedule.operations
        if operation.resource == 2
    ]
    resource_1_total = sum(resource_1_times)
    resource_2_total = sum(resource_2_times)
    flow_time_total = sum(resource_2_completions)

    st.markdown(f"**{heading}**  \n{_format_sequence(sequence)}")
    st.markdown(
        f"""
- Resource 1 processing time: `{' + '.join(map(str, resource_1_times))} = {resource_1_total} min`
- Resource 2 processing time: `{' + '.join(map(str, resource_2_times))} = {resource_2_total} min`
- Makespan: `last Resource 2 completion = {metrics.makespan} min`
- Resource 1 idle time: `{metrics.makespan} - {resource_1_total} = {metrics.resource_1_idle} min`
- Resource 2 idle time: `{metrics.makespan} - {resource_2_total} = {metrics.resource_2_idle} min`
- Resource 1 utilization: `{resource_1_total} / {metrics.makespan} x 100 = {metrics.resource_1_utilization:.2%}`
- Resource 2 utilization: `{resource_2_total} / {metrics.makespan} x 100 = {metrics.resource_2_utilization:.2%}`
- Average flow time: `({' + '.join(map(str, resource_2_completions))}) / {len(sequence)} = {flow_time_total} / {len(sequence)} = {metrics.average_flow_time:.2f} min`
        """
    )


def _render_results() -> None:
    st.title("Johnson's Rule: Results")
    st.caption("Campus print shop · Completed demonstration")
    st.success(f"Final Johnson sequence: **{_format_sequence(JOHNSON_SEQUENCE)}**")

    result_controls = st.columns([1.3, 1.3, 5])
    with result_controls[0]:
        st.button(
            "Back to final step",
            on_click=_return_to_final_step,
            width="stretch",
        )
    with result_controls[1]:
        st.button("Restart", on_click=_restart, width="stretch")

    comparison_rows = [
        {
            "Measure": "Sequence",
            "Johnson sequence": _format_sequence(JOHNSON_SEQUENCE),
            "Original sequence": _format_sequence(ORIGINAL_SEQUENCE),
        },
        {
            "Measure": "Makespan",
            "Johnson sequence": f"{JOHNSON_METRICS.makespan} min",
            "Original sequence": f"{ORIGINAL_METRICS.makespan} min",
        },
        {
            "Measure": "Resource 1 idle time",
            "Johnson sequence": f"{JOHNSON_METRICS.resource_1_idle} min",
            "Original sequence": f"{ORIGINAL_METRICS.resource_1_idle} min",
        },
        {
            "Measure": "Resource 2 idle time",
            "Johnson sequence": f"{JOHNSON_METRICS.resource_2_idle} min",
            "Original sequence": f"{ORIGINAL_METRICS.resource_2_idle} min",
        },
        {
            "Measure": "Resource 1 utilization",
            "Johnson sequence": f"{JOHNSON_METRICS.resource_1_utilization:.2%}",
            "Original sequence": f"{ORIGINAL_METRICS.resource_1_utilization:.2%}",
        },
        {
            "Measure": "Resource 2 utilization",
            "Johnson sequence": f"{JOHNSON_METRICS.resource_2_utilization:.2%}",
            "Original sequence": f"{ORIGINAL_METRICS.resource_2_utilization:.2%}",
        },
        {
            "Measure": "Average flow time",
            "Johnson sequence": f"{JOHNSON_METRICS.average_flow_time:.2f} min",
            "Original sequence": f"{ORIGINAL_METRICS.average_flow_time:.2f} min",
        },
    ]
    gantt_tab, performance_tab, calculations_tab = st.tabs(
        ["Gantt comparison", "Performance measures", "Calculations"]
    )

    with gantt_tab:
        st.caption(
            "Both schedules use the same time scale. Each bar is labelled with its job."
        )
        shared_axis_maximum = max(
            JOHNSON_METRICS.makespan,
            ORIGINAL_METRICS.makespan,
        )
        chart_columns = st.columns(2, gap="large")
        with chart_columns[0]:
            st.plotly_chart(
                make_gantt_chart(
                    JOHNSON_SCHEDULE,
                    "Johnson sequence",
                    shared_axis_maximum,
                ),
                width="stretch",
                config={"displayModeBar": False, "responsive": True},
            )
        with chart_columns[1]:
            st.plotly_chart(
                make_gantt_chart(
                    ORIGINAL_SCHEDULE,
                    "Original sequence",
                    shared_axis_maximum,
                ),
                width="stretch",
                config={"displayModeBar": False, "responsive": True},
            )

    with performance_tab:
        st.dataframe(
            comparison_rows,
            hide_index=True,
            width="stretch",
            column_config={
                "Measure": st.column_config.TextColumn(width="medium"),
                "Johnson sequence": st.column_config.TextColumn(width="large"),
                "Original sequence": st.column_config.TextColumn(width="large"),
            },
        )
        st.info(
            f"Johnson's Rule reduces the makespan by "
            f"**{ORIGINAL_METRICS.makespan - JOHNSON_METRICS.makespan} minutes** "
            f"and the average flow time by "
            f"**{ORIGINAL_METRICS.average_flow_time - JOHNSON_METRICS.average_flow_time:.2f} minutes**."
        )

    with calculations_tab:
        calculation_columns = st.columns(2)
        with calculation_columns[0]:
            _render_sequence_calculations(
                "Johnson sequence",
                JOHNSON_SEQUENCE,
                JOHNSON_SCHEDULE,
                JOHNSON_METRICS,
            )
        with calculation_columns[1]:
            _render_sequence_calculations(
                "Original sequence",
                ORIGINAL_SEQUENCE,
                ORIGINAL_SCHEDULE,
                ORIGINAL_METRICS,
            )
        st.caption(
            "Average flow time uses the Resource 2 completion times because all jobs "
            "are available at time 0."
        )


def _partial_sequence_for_phase(
    current_step: DecisionStep | None, current_phase: str | None
) -> tuple[str | None, ...]:
    if current_step is None:
        return (None,) * len(PRINT_SHOP_JOBS)
    if current_phase == "place":
        return current_step.partial_sequence
    if current_step.number > 1:
        return STEPS[current_step.number - 2].partial_sequence
    return (None,) * len(PRINT_SHOP_JOBS)


def _render_problem_view() -> None:
    st.title("Johnson's Rule: Two-Resource Flow Shop")
    st.caption("Demonstration mode · Campus print shop")
    st.markdown(
        "Each print job must first go through **Printing / Photocopying** and then "
        "through **Binding / Finishing**. The objective is to find a sequence that "
        "minimizes the total elapsed time."
    )

    problem_columns = st.columns([1.25, 1], gap="large")
    with problem_columns[0]:
        st.markdown("#### Processing times")
        _render_processing_table(None, None)
    with problem_columns[1]:
        st.markdown("#### How Johnson's Rule works")
        st.markdown(
            """
1. List the jobs and their processing times on Resources 1 and 2.
2. Find the job with the shortest processing time on either resource.
3. If this time is on Resource 1, put the job in the first open position. If it is on Resource 2, put the job in the last open position.
4. Repeat Steps 2 and 3 with the remaining jobs, working inward from both ends until all jobs are scheduled.
            """
        )
        st.button(
            "Start Demonstration",
            type="primary",
            on_click=_start,
            width="stretch",
        )


def _render_algorithm_view(
    current_step: DecisionStep | None,
    current_phase: str | None,
    completed_phases: int,
) -> None:
    st.markdown("## Johnson's Rule Demonstration")
    st.caption("Campus print shop · Build the sequence one decision at a time")

    workspace_columns = st.columns([1.15, 1], gap="large")
    with workspace_columns[0]:
        st.markdown("#### Processing times")
        _render_processing_table(current_step, current_phase)

    with workspace_columns[1]:
        st.markdown("#### Current partial sequence")
        _render_partial_sequence(
            _partial_sequence_for_phase(current_step, current_phase)
        )

        st.progress(
            completed_phases / TOTAL_PHASES,
            text=(
                "Ready to begin"
                if current_step is None
                else f"Iteration {current_step.number} of {len(STEPS)} · "
                + (
                    "Step 2: Find the shortest processing time"
                    if current_phase == "identify"
                    else "Step 3: Place the selected job"
                )
            ),
        )

        if current_step is None:
            st.info(
                "Click **Next Step** to find the shortest processing time among "
                "the unscheduled jobs."
            )
        elif current_phase == "identify":
            st.markdown("##### Step 2: Find the shortest processing time")
            _render_identification(current_step)
        else:
            st.markdown("##### Step 3: Place the selected job")
            _render_placement(current_step)

        control_columns = st.columns(3)
        with control_columns[0]:
            st.button(
                "Previous",
                on_click=_previous,
                disabled=completed_phases == 0,
                width="stretch",
            )
        with control_columns[1]:
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
        with control_columns[2]:
            st.button("Restart", on_click=_restart, width="stretch")


st.markdown(
    """
<style>
.block-container {max-width: 1240px; padding-top: 0.9rem; padding-bottom: 1.5rem;}
.johnson-table-wrap {width: 100%; overflow-x: auto; margin: 0.2rem 0 0.5rem;}
.johnson-table {width: 100%; border-collapse: collapse; font-size: 0.95rem;}
.johnson-table th, .johnson-table td {
    border-bottom: 1px solid rgba(128, 128, 128, 0.28);
    padding: 0.43rem 0.55rem;
    text-align: center;
}
.johnson-table thead th {background: rgba(128, 128, 128, 0.10); font-weight: 600;}
.johnson-table thead span {font-size: 0.82rem; font-weight: 400; opacity: 0.75;}
.johnson-table tbody th {font-weight: 600;}
.johnson-table .placed-job > th,
.johnson-table .placed-job > td {background: rgba(128, 128, 128, 0.16); color: #737373;}
.johnson-table .minimum-cell {
    background: #FFF0A8 !important;
    color: #3B2F00 !important;
    font-weight: 700;
}
.johnson-table .selected-cell {box-shadow: inset 0 0 0 3px #B45309;}
.sequence-slots {
    display: grid;
    grid-template-columns: repeat(6, minmax(54px, 1fr));
    gap: 0.35rem;
    margin: 0.25rem 0 0.75rem;
}
.sequence-slot {
    min-height: 58px;
    border: 1px dashed rgba(128, 128, 128, 0.55);
    border-radius: 0.45rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: rgba(128, 128, 128, 0.05);
}
.sequence-slot.filled {border-style: solid; border-color: var(--primary-color);}
.sequence-slot .position-label {font-size: 0.68rem; opacity: 0.70;}
.sequence-slot strong {font-size: 1.2rem; margin-top: 0.05rem;}
@media (max-width: 800px) {
    .block-container {padding-top: 0.6rem;}
    .sequence-slots {grid-template-columns: repeat(3, 1fr);}
    .johnson-table th, .johnson-table td {padding: 0.38rem 0.3rem; font-size: 0.88rem;}
}
</style>
""",
    unsafe_allow_html=True,
)

_initialize_state()
completed_phases = st.session_state[PHASE_KEY]
if completed_phases:
    current_step = STEPS[(completed_phases - 1) // 2]
    current_phase = "identify" if completed_phases % 2 == 1 else "place"
else:
    current_step = None
    current_phase = None

if not st.session_state[STARTED_KEY]:
    _render_problem_view()
elif st.session_state[RESULTS_KEY]:
    _render_results()
else:
    _render_algorithm_view(current_step, current_phase, completed_phases)

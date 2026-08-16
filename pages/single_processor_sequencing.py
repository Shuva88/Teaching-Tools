"""Classroom demonstration comparing three single-processor sequencing rules."""

from __future__ import annotations

from html import escape

import streamlit as st

from algorithms.single_processor import (
    FABRICATION_JOBS,
    SequencingMetrics,
    SingleProcessorSchedule,
    build_single_processor_schedule,
    calculate_sequencing_metrics,
    sequence_edd,
    sequence_fcfs,
    sequence_spt,
)
from components.single_processor_gantt import make_single_processor_gantt


SEQUENCES = {
    "FCFS": sequence_fcfs(FABRICATION_JOBS),
    "SPT": sequence_spt(FABRICATION_JOBS),
    "EDD": sequence_edd(FABRICATION_JOBS),
}
SCHEDULES = {
    rule: build_single_processor_schedule(rule, sequence, FABRICATION_JOBS)
    for rule, sequence in SEQUENCES.items()
}
METRICS = {
    rule: calculate_sequencing_metrics(schedule)
    for rule, schedule in SCHEDULES.items()
}
RULE_ORDER = ("FCFS", "SPT", "EDD")
TOTAL_PROCESSING_TIME = sum(job.processing_time for job in FABRICATION_JOBS)

STARTED_KEY = "single_processor_started"
STAGE_KEY = "single_processor_stage"
RESULTS_STAGE = len(RULE_ORDER)


def _initialize_state() -> None:
    if STARTED_KEY not in st.session_state:
        st.session_state[STARTED_KEY] = False
    if STAGE_KEY not in st.session_state:
        st.session_state[STAGE_KEY] = 0


def _start() -> None:
    st.session_state[STARTED_KEY] = True
    st.session_state[STAGE_KEY] = 0


def _previous() -> None:
    st.session_state[STAGE_KEY] = max(0, st.session_state[STAGE_KEY] - 1)


def _next() -> None:
    st.session_state[STAGE_KEY] = min(
        RESULTS_STAGE, st.session_state[STAGE_KEY] + 1
    )


def _restart() -> None:
    st.session_state[STARTED_KEY] = False
    st.session_state[STAGE_KEY] = 0


def _format_sequence(sequence: tuple[str, ...]) -> str:
    return " – ".join(sequence)


def _rule_description(rule: str) -> str:
    return {
        "FCFS": "First Come, First Served: retain the orders' arrival order.",
        "SPT": "Shortest Processing Time: arrange orders from shortest to longest processing time.",
        "EDD": "Earliest Due Date: arrange orders from earliest to latest due time.",
    }[rule]


def _criterion_label(rule: str) -> str:
    return {
        "FCFS": "Arrival",
        "SPT": "Processing",
        "EDD": "Due",
    }[rule]


def _criterion_value(rule: str, job_name: str) -> str:
    job = next(job for job in FABRICATION_JOBS if job.name == job_name)
    if rule == "FCFS":
        return f"#{job.arrival_order}"
    if rule == "SPT":
        return f"{job.processing_time} h"
    return f"{job.due_time} h"


def _render_sequence(rule: str) -> None:
    cards = []
    for position, job_name in enumerate(SEQUENCES[rule]):
        cards.append(
            "<div class='single-sequence-card'>"
            f"<span>{escape(_criterion_label(rule))}: "
            f"{escape(_criterion_value(rule, job_name))}</span>"
            f"<strong>{escape(job_name)}</strong></div>"
        )
        if position < len(SEQUENCES[rule]) - 1:
            cards.append("<div class='single-sequence-arrow'>→</div>")
    st.markdown(
        "<div class='single-sequence'>" + "".join(cards) + "</div>",
        unsafe_allow_html=True,
    )


def _schedule_rows(schedule: SingleProcessorSchedule) -> list[dict[str, int | str]]:
    return [
        {
            "Order": operation.job,
            "Start": operation.start,
            "Processing": operation.processing_time,
            "Due": operation.due_time,
            "Flow time": operation.flow_time,
            "Lateness": operation.lateness,
            "Tardiness": operation.tardiness,
        }
        for operation in schedule.operations
    ]


def _render_metric_cards(rule: str, metrics: SequencingMetrics) -> None:
    values = (
        ("Average flow time", f"{metrics.average_flow_time:.2f} h", rule == "SPT"),
        ("Average lateness", f"{metrics.average_lateness:.2f} h", False),
        ("Average tardiness", f"{metrics.average_tardiness:.2f} h", rule == "EDD"),
        ("Tardy orders", str(metrics.tardy_jobs), rule == "EDD"),
        ("Maximum tardiness", f"{metrics.maximum_tardiness} h", rule == "EDD"),
    )
    cards = [
        f"<div class='single-metric-card{' best' if highlighted else ''}'>"
        f"<span>{escape(label)}</span><strong>{escape(value)}</strong></div>"
        for label, value, highlighted in values
    ]
    st.markdown(
        "<div class='single-metric-grid'>" + "".join(cards) + "</div>",
        unsafe_allow_html=True,
    )


def _render_controls(stage: int) -> None:
    labels = ("Next: SPT", "Next: EDD", "Compare Rules")
    columns = st.columns(3)
    with columns[0]:
        st.button(
            "Previous",
            on_click=_previous,
            disabled=stage == 0,
            width="stretch",
        )
    with columns[1]:
        st.button(
            labels[stage],
            type="primary",
            on_click=_next,
            width="stretch",
        )
    with columns[2]:
        st.button("Restart", on_click=_restart, width="stretch")


def _render_problem_view() -> None:
    st.title("Single-Processor Sequencing")
    st.caption("Demonstration mode · Precision fabrication shop")
    st.markdown(
        "Six customer orders are waiting for one CNC laser-cutting machine. All "
        "orders are available at time 0, and each order must finish before the "
        "next one starts. Compare how three sequencing rules affect completion "
        "and due-date performance."
    )

    columns = st.columns([1.05, 1], gap="large")
    with columns[0]:
        st.markdown("#### Order data · arrival order")
        st.dataframe(
            [
                {
                    "Order": job.name,
                    "Processing time (h)": job.processing_time,
                    "Due time (h)": job.due_time,
                }
                for job in FABRICATION_JOBS
            ],
            hide_index=True,
            width="stretch",
            height=252,
        )
        st.caption("Time 0 is when the CNC machine becomes available.")
    with columns[1]:
        st.markdown("#### Sequencing rules")
        st.markdown(
            """
- **FCFS — First Come, First Served:** process orders in arrival order.
- **SPT — Shortest Processing Time:** process the shortest order first.
- **EDD — Earliest Due Date:** process the order with the earliest due time first.
            """
        )
        st.markdown(
            "**Measures:** average flow time, average lateness, average "
            "tardiness, number of tardy orders, and maximum tardiness."
        )
        st.button(
            "Start Demonstration",
            type="primary",
            on_click=_start,
            width="stretch",
        )


def _render_rule_view(stage: int) -> None:
    rule = RULE_ORDER[stage]
    schedule = SCHEDULES[rule]
    metrics = METRICS[rule]

    st.markdown("## Single-Processor Sequencing")
    st.caption("Precision fabrication shop · Compare one rule at a time")
    st.progress(
        (stage + 1) / len(RULE_ORDER),
        text=f"Rule {stage + 1} of {len(RULE_ORDER)} · {rule}",
    )

    columns = st.columns([1, 1.08], gap="large")
    with columns[0]:
        st.markdown(f"#### {rule} sequence")
        st.markdown(_rule_description(rule))
        _render_sequence(rule)
        st.plotly_chart(
            make_single_processor_gantt(
                schedule,
                f"{rule} · {_format_sequence(schedule.sequence)}",
                TOTAL_PROCESSING_TIME,
            ),
            width="stretch",
            config={"displayModeBar": False, "responsive": True},
        )
        _render_metric_cards(rule, metrics)

    with columns[1]:
        st.markdown("#### Order-by-order calculations")
        st.dataframe(
            _schedule_rows(schedule),
            hide_index=True,
            width="stretch",
            height=252,
            column_config={
                "Order": st.column_config.TextColumn(width="small"),
                "Processing": st.column_config.NumberColumn("Process"),
            },
        )
        if rule == "FCFS":
            st.info("FCFS requires no reordering: the arrival order is the sequence.")
        elif rule == "SPT":
            st.success(
                f"SPT gives the lowest average flow time in this example: "
                f"**{metrics.average_flow_time:.2f} hours**."
            )
        else:
            st.info(
                "**Lateness = flow time − due time** and may be negative when an "
                "order finishes early. **Tardiness = max(0, lateness)** and can "
                "never be negative."
            )
        _render_controls(stage)


def _comparison_table_html() -> str:
    rows = (
        ("Average flow time (h)", "average_flow_time", "SPT", ".2f"),
        ("Average lateness (h)", "average_lateness", "SPT", ".2f"),
        ("Average tardiness (h)", "average_tardiness", "EDD", ".2f"),
        ("Number of tardy orders", "tardy_jobs", "EDD", "d"),
        ("Maximum tardiness (h)", "maximum_tardiness", "EDD", "d"),
    )
    body = []
    for label, attribute, best_rule, number_format in rows:
        cells = []
        for rule in RULE_ORDER:
            value = getattr(METRICS[rule], attribute)
            displayed = format(value, number_format)
            cell_class = " class='best'" if rule == best_rule else ""
            cells.append(f"<td{cell_class}>{displayed}</td>")
        body.append(f"<tr><th>{escape(label)}</th>{''.join(cells)}</tr>")
    return (
        "<div class='single-comparison-wrap'><table class='single-comparison'>"
        "<thead><tr><th>Performance measure</th><th>FCFS</th><th>SPT</th>"
        "<th>EDD</th></tr></thead><tbody>"
        + "".join(body)
        + "</tbody></table></div>"
    )


def _render_calculations(rule: str) -> None:
    schedule = SCHEDULES[rule]
    metrics = METRICS[rule]
    flow_times = [operation.flow_time for operation in schedule.operations]
    lateness_values = [operation.lateness for operation in schedule.operations]
    tardiness_values = [operation.tardiness for operation in schedule.operations]
    tardy_orders = [
        operation.job for operation in schedule.operations if operation.tardiness > 0
    ]
    st.markdown(f"**{rule} · {_format_sequence(schedule.sequence)}**")
    st.markdown(
        f"""
- Average flow time: `({' + '.join(map(str, flow_times))}) / 6 = {sum(flow_times)} / 6 = {metrics.average_flow_time:.2f} h`
- Average lateness: `({' + '.join(map(str, lateness_values))}) / 6 = {sum(lateness_values)} / 6 = {metrics.average_lateness:.2f} h`
- Average tardiness: `({' + '.join(map(str, tardiness_values))}) / 6 = {sum(tardiness_values)} / 6 = {metrics.average_tardiness:.2f} h`
- Tardy orders: `{', '.join(tardy_orders)} = {metrics.tardy_jobs}`
- Maximum tardiness: `max({', '.join(map(str, tardiness_values))}) = {metrics.maximum_tardiness} h`
        """
    )


def _render_results() -> None:
    st.title("Single-Processor Sequencing: Comparison")
    st.caption("Precision fabrication shop · Completed demonstration")
    st.success(
        "Every rule performs the same **31 hours of processing work**. The "
        "sequence changes order completion and due-date performance, not the "
        "amount of work."
    )

    controls = st.columns([1.3, 1.3, 5])
    with controls[0]:
        st.button("Back to EDD", on_click=_previous, width="stretch")
    with controls[1]:
        st.button("Restart", on_click=_restart, width="stretch")

    performance_tab, gantt_tab, calculations_tab = st.tabs(
        ["Performance comparison", "Gantt comparison", "Calculations"]
    )
    with performance_tab:
        st.markdown(_comparison_table_html(), unsafe_allow_html=True)
        takeaways = st.columns(3, gap="medium")
        with takeaways[0]:
            st.info(
                "**SPT:** strongest on average flow time for this fixed example."
            )
        with takeaways[1]:
            st.info(
                "**EDD:** strongest on tardiness-related measures for this fixed example."
            )
        with takeaways[2]:
            st.info(
                "**FCFS:** preserves arrival order but is not best on these reported criteria."
            )
        st.caption(
            "No rule is universally best; the appropriate rule depends on the "
            "performance criterion that matters."
        )

    with gantt_tab:
        st.caption("All three charts use the same 0–31 hour scale.")
        chart_columns = st.columns(3, gap="medium")
        for column, rule in zip(chart_columns, RULE_ORDER):
            with column:
                st.plotly_chart(
                    make_single_processor_gantt(
                        SCHEDULES[rule],
                        rule,
                        TOTAL_PROCESSING_TIME,
                        height=230,
                    ),
                    width="stretch",
                    config={"displayModeBar": False, "responsive": True},
                )

    with calculations_tab:
        calculation_columns = st.columns(3, gap="large")
        for column, rule in zip(calculation_columns, RULE_ORDER):
            with column:
                _render_calculations(rule)


st.markdown(
    """
<style>
.block-container {max-width: 1240px; padding-top: 0.9rem; padding-bottom: 1.5rem;}
.single-sequence {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    margin: 0.35rem 0 0.55rem;
}
.single-sequence-card {
    min-width: 58px;
    flex: 1;
    border: 1px solid rgba(128, 128, 128, 0.34);
    border-radius: 0.45rem;
    padding: 0.32rem 0.22rem;
    text-align: center;
    background: rgba(0, 114, 178, 0.09);
}
.single-sequence-card span {display: block; font-size: 0.66rem; opacity: 0.75;}
.single-sequence-card strong {font-size: 1.08rem;}
.single-sequence-arrow {font-size: 1rem; opacity: 0.62;}
.single-metric-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.34rem;
    margin-top: 0.25rem;
}
.single-metric-card {
    border: 1px solid rgba(128, 128, 128, 0.28);
    border-radius: 0.45rem;
    padding: 0.38rem 0.45rem;
    background: rgba(128, 128, 128, 0.05);
}
.single-metric-card span {display: block; font-size: 0.70rem; opacity: 0.76;}
.single-metric-card strong {font-size: 1.02rem;}
.single-metric-card.best {
    background: rgba(0, 158, 115, 0.13);
    border-color: rgba(0, 158, 115, 0.55);
}
.single-comparison-wrap {overflow-x: auto; margin: 0.25rem 0 0.8rem;}
.single-comparison {width: 100%; border-collapse: collapse; font-size: 0.96rem;}
.single-comparison th, .single-comparison td {
    border-bottom: 1px solid rgba(128, 128, 128, 0.27);
    padding: 0.52rem 0.62rem;
    text-align: center;
}
.single-comparison th:first-child {text-align: left;}
.single-comparison thead th {background: rgba(128, 128, 128, 0.10);}
.single-comparison td.best {
    background: rgba(0, 158, 115, 0.15);
    color: #006A4E;
    font-weight: 700;
}
@media (max-width: 800px) {
    .block-container {padding-top: 0.6rem;}
    .single-sequence {display: grid; grid-template-columns: repeat(6, 1fr);}
    .single-sequence-arrow {display: none;}
    .single-sequence-card {min-width: 0;}
    .single-metric-grid {grid-template-columns: repeat(2, 1fr);}
}
</style>
""",
    unsafe_allow_html=True,
)

_initialize_state()
if not st.session_state[STARTED_KEY]:
    _render_problem_view()
elif st.session_state[STAGE_KEY] == RESULTS_STAGE:
    _render_results()
else:
    _render_rule_view(st.session_state[STAGE_KEY])

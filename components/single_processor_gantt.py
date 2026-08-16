"""Plotly Gantt component for single-processor sequencing rules."""

from __future__ import annotations

import plotly.graph_objects as go

from algorithms.single_processor import SingleProcessorSchedule


JOB_COLORS = {
    "A": "#0072B2",
    "B": "#D55E00",
    "C": "#009E73",
    "D": "#CC79A7",
    "E": "#E69F00",
    "F": "#56B4E9",
}


def make_single_processor_gantt(
    schedule: SingleProcessorSchedule,
    title: str,
    axis_maximum: int,
    height: int = 220,
) -> go.Figure:
    """Return a directly labelled one-resource Gantt chart."""

    figure = go.Figure()
    for operation in schedule.operations:
        figure.add_trace(
            go.Bar(
                y=["CNC"],
                x=[operation.processing_time],
                base=[operation.start],
                orientation="h",
                width=0.48,
                marker_color=JOB_COLORS[operation.job],
                text=[operation.job],
                textposition="inside",
                insidetextanchor="middle",
                showlegend=False,
                hovertemplate=(
                    f"<b>Order {operation.job}</b><br>"
                    f"Start: {operation.start} h<br>"
                    f"Processing: {operation.processing_time} h<br>"
                    f"Completion: {operation.flow_time} h<br>"
                    f"Due: {operation.due_time} h<br>"
                    f"Lateness: {operation.lateness} h<br>"
                    f"Tardiness: {operation.tardiness} h<extra></extra>"
                ),
            )
        )

    figure.add_vline(
        x=schedule.total_processing_time,
        line_width=2,
        line_dash="dash",
        line_color="#5C677D",
    )
    figure.add_annotation(
        x=schedule.total_processing_time,
        y=1.10,
        xref="x",
        yref="paper",
        text=f"Total = {schedule.total_processing_time} h",
        showarrow=False,
        xanchor="right",
        yanchor="bottom",
        font={"color": "#5C677D", "size": 12},
    )
    figure.update_layout(
        title={"text": title, "x": 0, "font": {"size": 18}},
        barmode="overlay",
        height=height,
        margin={"l": 8, "r": 12, "t": 62, "b": 12},
        xaxis={
            "title": "Elapsed time (hours)",
            "range": [0, axis_maximum * 1.035],
            "dtick": 5,
            "showgrid": True,
            "gridcolor": "rgba(128, 128, 128, 0.20)",
            "zeroline": False,
        },
        yaxis={"title": None, "showgrid": False},
        hoverlabel={"align": "left"},
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font={"size": 13},
    )
    return figure

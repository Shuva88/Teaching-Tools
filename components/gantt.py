"""Plotly Gantt chart component for two-resource schedules."""

from __future__ import annotations

import plotly.graph_objects as go

from algorithms.johnson import Schedule


RESOURCE_LABELS = {
    1: "Resource 1: Printing / Photocopying",
    2: "Resource 2: Binding / Finishing",
}

RESOURCE_AXIS_LABELS = {
    1: "R1: Printing",
    2: "R2: Binding",
}

JOB_COLORS = {
    "A": "#0072B2",
    "B": "#D55E00",
    "C": "#009E73",
    "D": "#CC79A7",
    "E": "#E69F00",
    "F": "#56B4E9",
}


def make_gantt_chart(
    schedule: Schedule,
    title: str,
    shared_axis_maximum: int,
    height: int = 270,
) -> go.Figure:
    """Return a directly labelled two-resource Gantt chart."""

    figure = go.Figure()
    for operation in schedule.operations:
        resource_label = RESOURCE_LABELS[operation.resource]
        resource_axis_label = RESOURCE_AXIS_LABELS[operation.resource]
        figure.add_trace(
            go.Bar(
                y=[resource_axis_label],
                x=[operation.duration],
                base=[operation.start],
                orientation="h",
                width=0.56,
                name=f"Job {operation.job}",
                legendgroup=operation.job,
                showlegend=False,
                marker={"color": JOB_COLORS[operation.job]},
                text=[operation.job],
                textposition="inside",
                insidetextanchor="middle",
                hovertemplate=(
                    f"<b>Job {operation.job}</b><br>"
                    f"{resource_label}<br>"
                    f"Start: {operation.start} min<br>"
                    f"Finish: {operation.finish} min<br>"
                    f"Duration: {operation.duration} min<extra></extra>"
                ),
            )
        )

    makespan = max(
        operation.finish
        for operation in schedule.operations
        if operation.resource == 2
    )
    figure.add_vline(
        x=makespan,
        line_width=2,
        line_dash="dash",
        line_color="#5C677D",
    )
    figure.add_annotation(
        x=makespan,
        y=1.14,
        xref="x",
        yref="paper",
        text=f"Makespan = {makespan} min",
        showarrow=False,
        xanchor="right",
        yanchor="bottom",
        font={"color": "#5C677D", "size": 13},
    )
    figure.update_layout(
        title={"text": title, "x": 0},
        barmode="overlay",
        height=height,
        margin={"l": 12, "r": 16, "t": 78, "b": 16},
        xaxis={
            "title": "Elapsed time (minutes)",
            "range": [0, shared_axis_maximum * 1.04],
            "dtick": 5,
            "showgrid": True,
            "gridcolor": "rgba(128, 128, 128, 0.20)",
            "zeroline": False,
        },
        yaxis={
            "categoryorder": "array",
            "categoryarray": [RESOURCE_AXIS_LABELS[2], RESOURCE_AXIS_LABELS[1]],
            "title": None,
        },
        hoverlabel={"align": "left"},
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font={"size": 14},
    )
    return figure

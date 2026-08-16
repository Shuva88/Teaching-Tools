"""Compact staffing comparison chart for the consecutive-days-off example."""

from __future__ import annotations

import plotly.graph_objects as go


def make_staffing_chart(
    days: tuple[str, ...],
    required: tuple[int, ...],
    scheduled: tuple[int, ...],
    height: int = 300,
) -> go.Figure:
    """Return a directly labelled required-versus-scheduled staffing chart."""

    figure = go.Figure()
    figure.add_trace(
        go.Bar(
            x=days,
            y=required,
            name="Required",
            marker_color="#0072B2",
            text=required,
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{x}<br>Required: %{y}<extra></extra>",
        )
    )
    figure.add_trace(
        go.Bar(
            x=days,
            y=scheduled,
            name="Scheduled",
            marker_color="#E69F00",
            text=scheduled,
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{x}<br>Scheduled: %{y}<extra></extra>",
        )
    )
    figure.update_layout(
        barmode="group",
        height=height,
        margin={"l": 12, "r": 12, "t": 42, "b": 12},
        xaxis={"title": None, "showgrid": False},
        yaxis={
            "title": "Number of partners",
            "range": [0, max(scheduled) + 1.4],
            "dtick": 1,
            "showgrid": True,
            "gridcolor": "rgba(128, 128, 128, 0.20)",
            "zeroline": False,
        },
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.05,
            "xanchor": "right",
            "x": 1,
        },
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font={"size": 14},
    )
    return figure

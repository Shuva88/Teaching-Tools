"""Reusable display components for the teaching demonstrations."""

from .clarke_wright import (
    build_click_demonstration_html,
    build_route_animation_html,
    build_savings_list_html,
    route_edges,
)
from .gantt import make_gantt_chart
from .single_processor_gantt import make_single_processor_gantt
from .staffing import make_staffing_chart

__all__ = [
    "build_click_demonstration_html",
    "build_route_animation_html",
    "build_savings_list_html",
    "route_edges",
    "make_gantt_chart",
    "make_single_processor_gantt",
    "make_staffing_chart",
]

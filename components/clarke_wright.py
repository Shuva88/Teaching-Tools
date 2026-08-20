"""Browser-native SVG components for the Clarke-Wright demonstration."""

from __future__ import annotations

import json
from html import escape
from typing import Iterable

from algorithms.clarke_wright import (
    DEPOT_ID,
    PPT_EXPECTED_FINAL_ROUTES,
    MergeDecision,
    route_load,
)


PPT_POSITIONS: dict[str, tuple[float, float]] = {
    "0": (0.52, 0.48),
    "1": (0.18, 0.10),
    "2": (0.18, 0.30),
    "3": (0.25, 0.18),
    "4": (0.19, 0.42),
    "5": (0.24, 0.40),
    "6": (0.29, 0.34),
    "7": (0.20, 0.57),
    "8": (0.27, 0.57),
    "9": (0.36, 0.24),
    "10": (0.35, 0.40),
    "11": (0.58, 0.12),
    "12": (0.51, 0.25),
    "13": (0.81, 0.36),
    "14": (0.50, 0.62),
    "15": (0.47, 0.78),
    "16": (0.59, 0.78),
    "17": (0.58, 0.29),
    "18": (0.64, 0.26),
    "19": (0.70, 0.26),
    "20": (0.71, 0.59),
    "21": (0.75, 0.30),
    "22": (0.82, 0.12),
    "23": (0.82, 0.25),
}

ROUTE_COLORS = ("#1976D2", "#D95F02", "#009E73", "#A855A1", "#E69F00")
LOAD_BADGE_POSITIONS = (
    (90, 310),
    (340, 300),
    (885, 320),
    (540, 570),
    (555, 32),
)
NEUTRAL_EDGE = "#CBD5E1"
ACCEPT_COLOR = "#16803A"
REJECT_COLOR = "#D32F2F"

Edge = tuple[str, str]


def _edge_key(node_a: str, node_b: str) -> Edge:
    ordered = sorted((node_a, node_b), key=int)
    return ordered[0], ordered[1]


def route_edges(route: Iterable[str]) -> frozenset[Edge]:
    """Return the undirected diagram edges for one depot route."""

    nodes = (DEPOT_ID, *tuple(route), DEPOT_ID)
    return frozenset(
        _edge_key(node_a, node_b)
        for node_a, node_b in zip(nodes, nodes[1:])
    )


def _route_group_index(route: tuple[str, ...]) -> int | None:
    if len(route) == 1:
        return None
    route_customers = set(route)
    return next(
        (
            index
            for index, final_route in enumerate(PPT_EXPECTED_FINAL_ROUTES)
            if route_customers.issubset(set(final_route))
        ),
        None,
    )


def _route_color(route: tuple[str, ...]) -> str:
    group_index = _route_group_index(route)
    return NEUTRAL_EDGE if group_index is None else ROUTE_COLORS[group_index]


def _edge_colors(routes: tuple[tuple[str, ...], ...]) -> dict[Edge, str]:
    colors: dict[Edge, str] = {}
    for route in routes:
        color = _route_color(route)
        for edge in route_edges(route):
            colors[edge] = color
    return colors


def _focused_edges(
    routes: tuple[tuple[str, ...], ...],
    candidate_pair: tuple[str, str] | None,
) -> frozenset[Edge]:
    if candidate_pair is None:
        return frozenset()
    focused: set[Edge] = set()
    for route in routes:
        if candidate_pair[0] in route or candidate_pair[1] in route:
            focused.update(route_edges(route))
    return frozenset(focused)


def _coordinates(customer: str) -> tuple[float, float]:
    x_position, y_position = PPT_POSITIONS[customer]
    x_position = 0.5 + (x_position - 0.5) * 1.32
    return x_position * 1000, y_position * 620


def _load_badge(
    route: tuple[str, ...],
    demands: dict[str, int],
) -> str:
    group_index = _route_group_index(route)
    if group_index is None:
        return ""
    x_position, y_position = LOAD_BADGE_POSITIONS[group_index]
    load = route_load(route, demands)
    color = _route_color(route)
    return (
        f'<g class="load-badge" transform="translate({x_position:.1f} {y_position:.1f})">'
        f'<rect x="-35" y="-13" width="70" height="26" rx="6" '
        f'fill="white" stroke="{color}" stroke-width="2"/>'
        f'<text text-anchor="middle" dominant-baseline="middle" '
        f'fill="#253047">Load {load}</text></g>'
    )


def _load_strip(
    routes: tuple[tuple[str, ...], ...],
    demands: dict[str, int],
) -> str:
    merged_routes = [route for route in routes if len(route) > 1]
    individual_count = sum(len(route) == 1 for route in routes)
    chips = [
        (
            f'<span class="load-chip" style="border-color:{_route_color(route)}">'
            f'{escape("–".join(route))} · L={route_load(route, demands)}</span>'
        )
        for route in merged_routes
    ]
    if individual_count:
        chips.append(
            f'<span class="individual-chip">{individual_count} individual '
            "route"
            f'{"s" if individual_count != 1 else ""} · load = demand</span>'
        )
    return '<div class="load-strip">' + "".join(chips) + "</div>"


def _final_route_table(
    routes: tuple[tuple[str, ...], ...],
    demands: dict[str, int],
) -> str:
    rows = "".join(
        "<tr>"
        f"<td>{route_number}</td>"
        f'<td><span class="route-swatch" style="background:{_route_color(route)}"></span>'
        f'0 – {escape(" – ".join(route))} – 0</td>'
        f"<td>{route_load(route, demands)}</td>"
        "</tr>"
        for route_number, route in enumerate(routes, start=1)
    )
    return (
        '<div class="final-table"><table><thead><tr><th>Route</th>'
        f'<th>Customer sequence</th><th>Load / 100</th></tr></thead><tbody>{rows}'
        "</tbody></table></div>"
    )


def build_route_animation_html(
    previous_routes: tuple[tuple[str, ...], ...],
    current_routes: tuple[tuple[str, ...], ...],
    demands: dict[str, int],
    *,
    candidate_pair: tuple[str, str] | None = None,
    accepted: bool | None = None,
    final_routes: tuple[tuple[str, ...], ...] | None = None,
) -> str:
    """Build an SVG that animates from the previous to current route state."""

    previous_colors = _edge_colors(previous_routes)
    current_colors = _edge_colors(current_routes)
    edges = sorted(
        set(previous_colors) | set(current_colors),
        key=lambda edge: (int(edge[0]), int(edge[1])),
    )
    focused = _focused_edges(previous_routes, candidate_pair)
    edge_markup: list[str] = []
    for edge in edges:
        node_a, node_b = edge
        x1, y1 = _coordinates(node_a)
        x2, y2 = _coordinates(node_b)
        previous_visible = edge in previous_colors
        current_visible = edge in current_colors
        previous_color = (
            previous_colors[edge]
            if edge in previous_colors
            else current_colors[edge]
        )
        current_color = (
            current_colors[edge]
            if edge in current_colors
            else previous_color
        )
        classes = "route-edge"
        if edge in focused:
            classes += " route-focus"
        if not previous_visible and current_visible:
            classes += " entering-edge"
        if previous_visible and not current_visible:
            classes += " leaving-edge"
        edge_markup.append(
            f'<line class="{classes}" data-edge="{node_a}-{node_b}" '
            f'x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'pathLength="1" stroke="{previous_color}" '
            f'data-current-color="{current_color}" '
            f'data-current-visible="{1 if current_visible else 0}" '
            f'style="opacity:{1 if previous_visible else 0};'
            f'stroke-dashoffset:{1 if not previous_visible else 0}"/>'
        )

    candidate_markup = ""
    if candidate_pair is not None:
        i, j = candidate_pair
        x1, y1 = _coordinates(i)
        x2, y2 = _coordinates(j)
        candidate_class = "candidate-accepted" if accepted else "candidate-rejected"
        candidate_markup = (
            f'<line class="candidate-line {candidate_class}" x1="{x1:.1f}" '
            f'y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>'
        )

    node_markup: list[str] = []
    for customer in (DEPOT_ID, *tuple(str(number) for number in range(1, 24))):
        x_position, y_position = _coordinates(customer)
        is_candidate = candidate_pair is not None and customer in candidate_pair
        candidate_class = ""
        if is_candidate:
            candidate_class = (
                " candidate-node accepted-node"
                if accepted
                else " candidate-node rejected-node"
            )
        if customer == DEPOT_ID:
            node_markup.append(
                f'<g class="node depot-node" transform="translate({x_position:.1f} {y_position:.1f})">'
                '<circle r="24"/><text text-anchor="middle" dominant-baseline="middle">0</text>'
                '<text class="depot-label" x="0" y="40" text-anchor="middle">Depot</text></g>'
            )
        else:
            demand = demands[customer]
            node_markup.append(
                f'<g class="node customer-node{candidate_class}" '
                f'transform="translate({x_position:.1f} {y_position:.1f})">'
                '<circle r="18"/><text text-anchor="middle" dominant-baseline="middle">'
                f"{customer}</text><text class=\"demand-label\" x=\"24\" y=\"-17\">"
                f"d={demand}</text></g>"
            )

    badges = "".join(
        _load_badge(route, demands) for route in current_routes if len(route) > 1
    )
    final_table = (
        _final_route_table(final_routes, demands) if final_routes is not None else ""
    )
    diagram_height = 350 if final_routes is not None else 405

    return f"""<!doctype html>
<html><head><meta charset="utf-8"><style>
* {{ box-sizing: border-box; }}
body {{ margin: 0; font-family: Inter, Arial, sans-serif; color: #253047; background: transparent; }}
.panel {{ height: 100%; border: 1px solid #D9DEE8; border-radius: 12px; background: #FFF; overflow: hidden; }}
.load-strip {{ min-height: 42px; padding: 7px 10px 3px; display: flex; gap: 6px; flex-wrap: wrap; align-items: center; border-bottom: 1px solid #EEF1F5; }}
.load-chip, .individual-chip {{ display: inline-block; padding: 3px 7px; border: 1.5px solid #AAB4C4; border-radius: 999px; font-size: 11px; background: #FFF; white-space: nowrap; }}
.individual-chip {{ color: #667085; border-color: #D4DAE3; background: #F7F8FA; }}
svg {{ width: 100%; height: {diagram_height}px; display: block; }}
.route-edge {{ stroke-width: 4; stroke-linecap: round; transition: stroke 600ms ease, opacity 520ms ease, stroke-dashoffset 650ms ease, stroke-width 450ms ease; }}
.entering-edge {{ stroke-dasharray: 1; }}
.route-focus {{ animation: routeFocus 680ms ease; }}
.candidate-line {{ fill: none; stroke-width: 6; stroke-linecap: round; pointer-events: none; }}
.candidate-accepted {{ stroke: #16803A; opacity: 0; animation: acceptGlow 700ms ease; }}
.candidate-rejected {{ stroke: #D32F2F; stroke-dasharray: 10 8; opacity: 0; animation: rejectFlash 700ms ease; }}
.customer-node circle {{ fill: #FFF; stroke: #D58A00; stroke-width: 3; }}
.customer-node > text {{ fill: #1D4ED8; font-size: 14px; font-weight: 700; }}
.customer-node .demand-label {{ fill: #15803D; font-size: 13px; font-weight: 700; }}
.depot-node circle {{ fill: #172033; stroke: #FFF; stroke-width: 3; }}
.depot-node > text {{ fill: #FFF; font-size: 16px; font-weight: 800; }}
.depot-node .depot-label {{ fill: #172033; font-size: 13px; font-weight: 700; }}
.candidate-node circle {{ transform-box: fill-box; transform-origin: center; }}
.accepted-node circle {{ animation: nodePulseGreen 700ms ease; }}
.rejected-node circle {{ animation: nodePulseRed 700ms ease; }}
.load-badge text {{ font-size: 12px; font-weight: 700; }}
.final-table {{ padding: 0 10px 8px; }}
.final-table table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
.final-table th {{ text-align: left; color: #596579; background: #F5F7FA; }}
.final-table th, .final-table td {{ padding: 4px 7px; border-bottom: 1px solid #E7EAF0; }}
.final-table th:first-child, .final-table td:first-child {{ width: 48px; text-align: center; }}
.final-table th:last-child, .final-table td:last-child {{ width: 82px; text-align: center; }}
.route-swatch {{ display: inline-block; width: 13px; height: 4px; margin-right: 6px; vertical-align: middle; border-radius: 2px; }}
@keyframes routeFocus {{ 0%,100% {{ stroke-width:4; filter:none; }} 45% {{ stroke-width:8; filter:drop-shadow(0 0 5px #60A5FA); }} }}
@keyframes acceptGlow {{ 0% {{ opacity:0; }} 35% {{ opacity:.95; }} 100% {{ opacity:0; }} }}
@keyframes rejectFlash {{ 0% {{ opacity:0; }} 30%,65% {{ opacity:.95; }} 100% {{ opacity:.12; }} }}
@keyframes nodePulseGreen {{ 0%,100% {{ transform:scale(1); stroke:#D58A00; }} 45% {{ transform:scale(1.5); stroke:#16803A; stroke-width:6; }} }}
@keyframes nodePulseRed {{ 0%,100% {{ transform:scale(1); stroke:#D58A00; }} 45% {{ transform:scale(1.5); stroke:#D32F2F; stroke-width:6; }} }}
</style></head><body>
<div class="panel">{_load_strip(current_routes, demands)}
<svg viewBox="0 0 1000 620" role="img" aria-label="Current Clarke-Wright route network">
<g id="route-edges">{"".join(edge_markup)}</g>
<g id="candidate-link">{candidate_markup}</g>
<g id="nodes">{"".join(node_markup)}</g>
<g id="route-loads">{badges}</g>
</svg>{final_table}</div>
<script>
requestAnimationFrame(() => requestAnimationFrame(() => {{
  document.querySelectorAll('.route-edge').forEach((edge) => {{
    edge.style.stroke = edge.dataset.currentColor;
    edge.style.opacity = edge.dataset.currentVisible;
    if (edge.classList.contains('entering-edge')) edge.style.strokeDashoffset = '0';
  }});
}}));
</script></body></html>"""


def build_savings_list_html(
    decisions: tuple[MergeDecision, ...],
    processed_count: int,
) -> str:
    """Build the fully stateful, auto-scrolling 27-row savings panel."""

    rows: list[str] = []
    for index, decision in enumerate(decisions):
        processed = index < processed_count
        current = processed_count > 0 and index == processed_count - 1
        state_class = "future"
        status = "—"
        if processed:
            state_class = "accepted" if decision.accepted else "rejected"
            status = "✓ Accepted" if decision.accepted else "✕ Rejected"
        if current:
            state_class += " current"
        current_id = ' id="current-row"' if current else ""
        rows.append(
            f'<tr class="{state_class}"{current_id}>'
            f"<td>{decision.number}</td><td>{decision.saving}</td>"
            f'<td class="pair">({decision.i}, {decision.j})</td>'
            f'<td class="status">{status}</td></tr>'
        )

    return f"""<!doctype html>
<html><head><meta charset="utf-8"><style>
* {{ box-sizing: border-box; }}
body {{ margin: 0; font-family: Inter, Arial, sans-serif; color: #253047; background: transparent; }}
.panel {{ height: 478px; border: 1px solid #D9DEE8; border-radius: 12px; overflow: hidden; background: #FFF; }}
.title {{ height: 38px; display:flex; align-items:center; padding:0 11px; font-weight:700; border-bottom:1px solid #E4E8EF; background:#F7F8FA; }}
.scroll {{ height: 439px; overflow-y: auto; scroll-behavior: smooth; }}
table {{ width: 100%; border-collapse: separate; border-spacing: 0; font-size: 12px; }}
thead th {{ position: sticky; top: 0; z-index: 2; background: #EEF2F7; color:#4B5565; text-align:center; padding:7px 5px; border-bottom:1px solid #D7DCE5; }}
tbody td {{ padding: 6px 5px; text-align:center; border-bottom:1px solid #EEF1F5; transition: background-color 450ms ease, color 450ms ease; }}
tbody tr.future {{ color:#7C8799; background:#FFF; }}
tbody tr.accepted {{ color:#14532D; background:#E9F8EE; }}
tbody tr.rejected {{ color:#9F1D1D; background:#FDECEC; }}
tbody tr.rejected .pair {{ text-decoration: line-through; }}
tbody tr.current td {{ border-top:2px solid #2563EB; border-bottom:2px solid #2563EB; font-weight:800; animation:rowPulse 700ms ease; }}
tbody tr.current td:first-child {{ border-left:4px solid #2563EB; }}
tbody tr.current td:last-child {{ border-right:2px solid #2563EB; }}
.status {{ min-width:77px; font-weight:700; }}
@keyframes rowPulse {{ 0% {{ filter:brightness(1); }} 45% {{ filter:brightness(.88); }} 100% {{ filter:brightness(1); }} }}
</style></head><body><div class="panel"><div class="title">Savings list · descending order</div>
<div class="scroll"><table><thead><tr><th>S. No.</th><th>Saving</th><th>Pair</th><th>Decision</th></tr></thead>
<tbody>{"".join(rows)}</tbody></table></div></div>
<script>const row=document.getElementById('current-row'); if(row) setTimeout(() => row.scrollIntoView({{block:'center'}}), 80);</script>
</body></html>"""


def build_click_demonstration_html(
    decisions: tuple[MergeDecision, ...],
    initial_routes: tuple[tuple[str, ...], ...],
    final_routes: tuple[tuple[str, ...], ...],
    demands: dict[str, int],
    capacity: int,
) -> str:
    """Build a click-driven browser animation with no per-step Streamlit reruns."""

    def edge_state(
        routes: tuple[tuple[str, ...], ...],
        *,
        include_depot: bool = False,
    ) -> dict[str, str]:
        colors: dict[str, str] = {}
        for route in routes:
            edges = (
                route_edges(route)
                if include_depot
                else {
                    _edge_key(node_a, node_b)
                    for node_a, node_b in zip(route, route[1:])
                }
            )
            for edge in edges:
                colors[f"{edge[0]}-{edge[1]}"] = _route_color(route)
        return colors

    def load_state(routes: tuple[tuple[str, ...], ...]) -> dict[str, object]:
        merged = [
            {
                "chain": "–".join(route),
                "load": route_load(route, demands),
                "color": _route_color(route),
            }
            for route in routes
            if len(route) > 1
        ]
        return {
            "merged": merged,
            "individualCount": sum(len(route) == 1 for route in routes),
        }

    frames: list[dict[str, object]] = []
    all_edge_ids: set[str] = set()
    for decision in decisions:
        current_edges = edge_state(decision.routes_after)
        all_edge_ids.update(current_edges)
        merged_route = None
        if decision.accepted:
            merged_route = next(
                route
                for route in decision.routes_after
                if decision.i in route and decision.j in route
            )
        frames.append(
            {
                "step": decision.number,
                "saving": decision.saving,
                "i": decision.i,
                "j": decision.j,
                "accepted": decision.accepted,
                "reason": decision.rejection_reason,
                "mergedRoute": (
                    " – ".join(merged_route)
                    if merged_route is not None
                    else None
                ),
                "mergedLoad": decision.resulting_route_load,
                "edges": current_edges,
                "focusEdges": [
                    f"{edge[0]}-{edge[1]}"
                    for edge in sorted(
                        {
                            _edge_key(node_a, node_b)
                            for route in decision.routes_before
                            if decision.i in route or decision.j in route
                            for node_a, node_b in zip(route, route[1:])
                        },
                        key=lambda edge: (int(edge[0]), int(edge[1])),
                    )
                ],
                "loads": load_state(decision.routes_after),
            }
        )

    initial_edges = edge_state(initial_routes)
    final_edges = edge_state(final_routes, include_depot=True)
    all_edge_ids.update(final_edges)
    edge_markup: list[str] = []
    for edge_id in sorted(
        all_edge_ids,
        key=lambda edge: tuple(int(node) for node in edge.split("-")),
    ):
        node_a, node_b = edge_id.split("-")
        x1, y1 = _coordinates(node_a)
        x2, y2 = _coordinates(node_b)
        initial_color = initial_edges.get(edge_id, NEUTRAL_EDGE)
        initially_visible = edge_id in initial_edges
        edge_markup.append(
            f'<line id="edge-{edge_id}" class="route-edge" data-edge="{edge_id}" '
            f'x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'pathLength="1" stroke="{initial_color}" '
            f'style="opacity:{1 if initially_visible else 0};'
            f'stroke-dashoffset:{0 if initially_visible else 1}"/>'
        )

    node_markup: list[str] = []
    for customer in (DEPOT_ID, *tuple(str(number) for number in range(1, 24))):
        x_position, y_position = _coordinates(customer)
        if customer == DEPOT_ID:
            node_markup.append(
                f'<g id="node-0" class="node depot-node" '
                f'transform="translate({x_position:.1f} {y_position:.1f})">'
                '<circle r="24"/><text text-anchor="middle" dominant-baseline="middle">0</text>'
                '<text class="depot-label" x="0" y="40" text-anchor="middle">Depot</text></g>'
            )
        else:
            node_markup.append(
                f'<g id="node-{customer}" class="node customer-node" '
                f'transform="translate({x_position:.1f} {y_position:.1f})">'
                '<circle r="25"/><text class="customer-number" x="0" y="-5" '
                f'text-anchor="middle">{customer}</text>'
                '<text class="demand-label" x="0" y="12" text-anchor="middle">'
                f'({demands[customer]})</text></g>'
            )

    savings_rows = "".join(
        f'<tr id="saving-{decision.number}" class="future">'
        f"<td>{decision.number}</td><td>{decision.saving}</td>"
        f'<td class="pair">({decision.i}, {decision.j})</td>'
        '<td class="decision">—</td></tr>'
        for decision in decisions
    )
    final_table = _final_route_table(final_routes, demands)
    frames_json = json.dumps(frames, ensure_ascii=False)
    initial_edges_json = json.dumps(initial_edges, ensure_ascii=False)
    final_edges_json = json.dumps(final_edges, ensure_ascii=False)
    initial_loads_json = json.dumps(load_state(initial_routes), ensure_ascii=False)

    return f"""<!doctype html>
<html><head><meta charset="utf-8"><style>
* {{ box-sizing: border-box; }}
body {{ margin:0; font-family:Inter,Arial,sans-serif; color:#253047; background:transparent; }}
.app {{ height:557px; display:flex; flex-direction:column; gap:8px; }}
.topbar {{ min-height:62px; display:grid; grid-template-columns:minmax(330px,1fr) 285px 190px; gap:10px; align-items:center; }}
.status {{ min-height:58px; display:flex; align-items:center; padding:9px 13px; border:1px solid #D9DEE8; border-radius:10px; background:#F7F9FC; font-size:13px; line-height:1.35; transition:background-color 300ms ease,border-color 300ms ease; }}
.status.considering {{ background:#EEF5FF; border-color:#77A7EF; }}
.status.accepted {{ background:#EAF8EE; border-color:#63B67A; color:#14532D; }}
.status.rejected {{ background:#FDECEC; border-color:#E88B8B; color:#8F1D1D; }}
.status.complete {{ background:#E7F7EC; border-color:#46A566; color:#14532D; font-weight:700; }}
.progress-card {{ padding:8px 10px; border:1px solid #D9DEE8; border-radius:10px; background:#FFF; }}
.progress-label {{ display:flex; justify-content:space-between; font-size:11px; color:#596579; margin-bottom:6px; }}
.progress-track {{ height:9px; background:#E8ECF2; border-radius:999px; overflow:hidden; }}
.progress-bar {{ width:0; height:100%; background:#2563EB; border-radius:999px; transition:width 600ms ease; }}
.controls {{ display:grid; grid-template-columns:1fr 1.25fr; gap:7px; }}
.controls button {{ min-height:42px; padding:7px 9px; border:1px solid #C9D1DC; border-radius:9px; background:#FFF; color:#253047; font-size:12px; font-weight:700; cursor:pointer; transition:background-color 180ms ease,border-color 180ms ease,transform 120ms ease; }}
.controls button:hover:not(:disabled) {{ background:#F2F6FC; border-color:#8CA6CB; }}
.controls button:active:not(:disabled) {{ transform:translateY(1px); }}
.controls button.primary {{ color:#FFF; background:#2563EB; border-color:#2563EB; }}
.controls button.primary:hover:not(:disabled) {{ background:#1D4ED8; }}
.controls button:disabled {{ color:#9AA3B2; background:#F1F3F6; cursor:not-allowed; }}
.workspace {{ min-height:0; flex:1; display:grid; grid-template-columns:36% 64%; gap:10px; }}
.panel {{ border:1px solid #D9DEE8; border-radius:12px; background:#FFF; overflow:hidden; min-width:0; }}
.savings-panel {{ display:flex; flex-direction:column; min-height:0; }}
.panel-title {{ height:36px; display:flex; align-items:center; padding:0 10px; font-size:13px; font-weight:700; background:#F7F8FA; border-bottom:1px solid #E4E8EF; }}
.savings-scroll {{ min-height:0; flex:1; overflow-y:auto; scroll-behavior:smooth; }}
table {{ width:100%; border-collapse:separate; border-spacing:0; font-size:11px; }}
thead th {{ position:sticky; top:0; z-index:2; padding:6px 4px; background:#EEF2F7; color:#4B5565; border-bottom:1px solid #D7DCE5; text-align:center; }}
tbody td {{ padding:5px 4px; text-align:center; border-bottom:1px solid #EEF1F5; transition:background-color 400ms ease,color 400ms ease; }}
tbody tr.future {{ color:#7C8799; background:#FFF; }}
tbody tr.considering td {{ color:#1D4ED8; background:#E8F1FF; font-weight:800; border-top:2px solid #2563EB; border-bottom:2px solid #2563EB; }}
tbody tr.accepted {{ color:#14532D; background:#E9F8EE; }}
tbody tr.rejected {{ color:#9F1D1D; background:#FDECEC; }}
tbody tr.rejected .pair {{ text-decoration:line-through; }}
tbody tr.current td {{ border-top:2px solid #2563EB; border-bottom:2px solid #2563EB; font-weight:800; }}
.decision {{ min-width:68px; font-weight:700; }}
.route-panel {{ position:relative; display:flex; flex-direction:column; }}
.load-strip {{ min-height:40px; padding:6px 9px 3px; display:flex; gap:5px; flex-wrap:wrap; align-items:center; border-bottom:1px solid #EEF1F5; transition:opacity 250ms ease; }}
.load-chip,.individual-chip {{ display:inline-block; padding:3px 6px; border:1.5px solid #AAB4C4; border-radius:999px; font-size:10px; background:#FFF; white-space:nowrap; }}
.individual-chip {{ color:#667085; border-color:#D4DAE3; background:#F7F8FA; }}
.visual-note {{ min-height:27px; display:flex; align-items:center; padding:4px 10px; color:#596579; background:#FFF8E7; border-bottom:1px solid #F0DFC0; font-size:10px; line-height:1.25; }}
svg {{ width:100%; min-height:0; flex:1; display:block; }}
.route-edge {{ stroke-width:4; stroke-linecap:round; stroke-dasharray:1; transition:stroke 1100ms ease,opacity 1000ms ease,stroke-dashoffset 1150ms ease,stroke-width 800ms ease; }}
.route-edge.focus {{ animation:routeFocus 850ms ease; }}
.candidate-line {{ fill:none; stroke-width:6; stroke-linecap:round; opacity:0; pointer-events:none; }}
.candidate-line.preview {{ stroke:#2563EB; stroke-dasharray:9 7; animation:previewFlash 850ms ease forwards; }}
.candidate-line.accepted {{ stroke:#16803A; animation:acceptGlow 1100ms ease; }}
.candidate-line.rejected {{ stroke:#D32F2F; stroke-dasharray:10 8; animation:rejectFlash 1100ms ease forwards; }}
.customer-node circle {{ fill:#FFF; stroke:#D58A00; stroke-width:3; transform-box:fill-box; transform-origin:center; }}
.customer-node .customer-number {{ fill:#1D4ED8; font-size:14px; font-weight:800; }}
.customer-node .demand-label {{ fill:#15803D; font-size:11px; font-weight:700; }}
.depot-node circle {{ fill:#172033; stroke:#FFF; stroke-width:3; }}
.depot-node > text {{ fill:#FFF; font-size:16px; font-weight:800; }}
.depot-node .depot-label {{ fill:#172033; font-size:13px; font-weight:700; }}
.depot-node.connecting circle {{ animation:depotPulse 1200ms ease; }}
.customer-node.preview circle {{ animation:nodePreview 850ms ease; }}
.customer-node.accepted circle {{ animation:nodePulseGreen 1100ms ease; }}
.customer-node.rejected circle {{ animation:nodePulseRed 1100ms ease; }}
.final-table {{ flex:none; max-height:0; opacity:0; overflow:hidden; margin:0 7px; padding:0 8px; border:0 solid #D9DEE8; border-radius:8px; background:#FFF; transition:max-height 600ms ease,opacity 500ms ease,padding 500ms ease,border-width 500ms ease; }}
.final-table.show {{ max-height:145px; opacity:1; padding:5px 8px; border-width:1px; }}
.final-table table {{ font-size:10px; }}
.final-table th {{ text-align:left; color:#596579; background:#F5F7FA; }}
.final-table th,.final-table td {{ padding:3px 5px; border-bottom:1px solid #E7EAF0; }}
.final-table th:first-child,.final-table td:first-child {{ width:42px; text-align:center; }}
.final-table th:last-child,.final-table td:last-child {{ width:70px; text-align:center; }}
.route-swatch {{ display:inline-block; width:13px; height:4px; margin-right:5px; vertical-align:middle; border-radius:2px; }}
@keyframes routeFocus {{ 0%,100% {{ stroke-width:4;filter:none; }} 50% {{ stroke-width:8;filter:drop-shadow(0 0 5px #60A5FA); }} }}
@keyframes previewFlash {{ 0% {{ opacity:0; }} 45%,100% {{ opacity:.8; }} }}
@keyframes acceptGlow {{ 0% {{ opacity:.8; }} 50% {{ opacity:1; }} 100% {{ opacity:0; }} }}
@keyframes rejectFlash {{ 0% {{ opacity:.8; }} 35%,70% {{ opacity:1; }} 100% {{ opacity:.15; }} }}
@keyframes nodePreview {{ 0%,100% {{ transform:scale(1);stroke:#D58A00; }} 50% {{ transform:scale(1.35);stroke:#2563EB;stroke-width:5; }} }}
@keyframes nodePulseGreen {{ 0%,100% {{ transform:scale(1);stroke:#D58A00; }} 45% {{ transform:scale(1.5);stroke:#16803A;stroke-width:6; }} }}
@keyframes nodePulseRed {{ 0%,100% {{ transform:scale(1);stroke:#D58A00; }} 45% {{ transform:scale(1.5);stroke:#D32F2F;stroke-width:6; }} }}
@keyframes depotPulse {{ 0%,100% {{ transform:scale(1); }} 45% {{ transform:scale(1.35);filter:drop-shadow(0 0 7px #2563EB); }} }}
@media (max-width:900px) {{ .topbar {{ grid-template-columns:1fr 270px; }} .progress-card {{ grid-column:1 / -1; }} }}
@media (max-width:760px) {{ .app {{ height:auto; }} .topbar {{ grid-template-columns:1fr; }} .progress-card {{ grid-column:auto; }} .workspace {{ grid-template-columns:1fr; }} .savings-scroll {{ height:310px; flex:none; }} svg {{ height:390px; flex:none; }} }}
</style></head><body>
<div class="app">
  <div class="topbar">
    <div id="status" class="status">Initial state: no savings links selected. Click Next Savings Pair to consider S. No. 1.</div>
    <div class="controls"><button id="previous-button" type="button" disabled>Previous</button><button id="next-button" class="primary" type="button">Next Savings Pair</button></div>
    <div class="progress-card"><div class="progress-label"><span>Savings pairs</span><span id="progress-text">0 / {len(decisions)}</span></div><div class="progress-track"><div id="progress-bar" class="progress-bar"></div></div></div>
  </div>
  <div class="workspace">
    <div class="panel savings-panel"><div class="panel-title">Savings list · descending order</div><div class="savings-scroll"><table><thead><tr><th>S. No.</th><th>Saving</th><th>Pair</th><th>Decision</th></tr></thead><tbody>{savings_rows}</tbody></table></div></div>
    <div class="panel route-panel"><div id="load-strip" class="load-strip"></div><div class="visual-note"><strong>Visual note:</strong>&nbsp;Direct depot links are hidden while customer sub-paths are formed. They are added after the savings list is exhausted.</div>
      <svg viewBox="0 25 1000 525" role="img" aria-label="Animated Clarke-Wright route network">
        <g id="route-edges">{"".join(edge_markup)}</g>
        <line id="candidate-line" class="candidate-line"/>
        <g id="nodes">{"".join(node_markup)}</g>
      </svg>{final_table}
    </div>
  </div>
</div>
<script>
const frames={frames_json};
const initialEdges={initial_edges_json};
const finalEdges={final_edges_json};
const initialLoads={initial_loads_json};
const sleep=(ms)=>new Promise(resolve=>setTimeout(resolve,ms));
const statusBox=document.getElementById('status');
const candidate=document.getElementById('candidate-line');
const progressBar=document.getElementById('progress-bar');
const progressText=document.getElementById('progress-text');
const loadStrip=document.getElementById('load-strip');
const previousButton=document.getElementById('previous-button');
const nextButton=document.getElementById('next-button');
const finalTable=document.querySelector('.final-table');
let currentIndex=0;
let busy=false;
let depotConnected=false;

function renderLoads(loads) {{
  const chips=loads.merged.map(item=>`<span class="load-chip" style="border-color:${{item.color}}">${{item.chain}} · L=${{item.load}}</span>`);
  if(loads.individualCount) chips.push(`<span class="individual-chip">${{loads.individualCount}} individual route${{loads.individualCount===1?'':'s'}} · load = demand</span>`);
  loadStrip.style.opacity='0.35';
  setTimeout(()=>{{ loadStrip.innerHTML=chips.join(''); loadStrip.style.opacity='1'; }},180);
}}

function applyEdges(edgeState) {{
  document.querySelectorAll('.route-edge').forEach(edge=>{{
    const color=edgeState[edge.dataset.edge];
    const visible=Boolean(color);
    if(visible && Number(edge.style.opacity)===0) edge.style.strokeDashoffset='1';
    requestAnimationFrame(()=>{{
      if(color) edge.style.stroke=color;
      edge.style.opacity=visible?'1':'0';
      edge.style.strokeDashoffset=visible?'0':'1';
    }});
  }});
}}

function positionCandidate(frame) {{
  const first=document.getElementById(`node-${{frame.i}}`);
  const second=document.getElementById(`node-${{frame.j}}`);
  const firstTransform=first.getAttribute('transform').match(/[-\d.]+/g).map(Number);
  const secondTransform=second.getAttribute('transform').match(/[-\d.]+/g).map(Number);
  candidate.setAttribute('x1',firstTransform[0]); candidate.setAttribute('y1',firstTransform[1]);
  candidate.setAttribute('x2',secondTransform[0]); candidate.setAttribute('y2',secondTransform[1]);
}}

function clearTransientClasses() {{
  document.querySelectorAll('.customer-node').forEach(node=>node.classList.remove('preview','accepted','rejected'));
  document.querySelectorAll('.route-edge').forEach(edge=>edge.classList.remove('focus'));
  candidate.className.baseVal='candidate-line';
}}

function stateEdges(index) {{
  return index===0 ? initialEdges : frames[index-1].edges;
}}

function stateLoads(index) {{
  return index===0 ? initialLoads : frames[index-1].loads;
}}

function renderRows(processedCount) {{
  frames.forEach((frame,index)=>{{
    const row=document.getElementById(`saving-${{frame.step}}`);
    const decision=row.querySelector('.decision');
    row.className='future';
    decision.textContent='—';
    if(index<processedCount) {{
      row.className=frame.accepted?'accepted':'rejected';
      decision.textContent=frame.accepted?'✓ Accepted':'✕ Rejected';
    }}
  }});
  if(processedCount>0) document.getElementById(`saving-${{processedCount}}`).classList.add('current');
}}

function updateProgress() {{
  progressBar.style.width=`${{100*currentIndex/frames.length}}%`;
  progressText.textContent=`${{currentIndex}} / ${{frames.length}}`;
}}

function updateControls() {{
  previousButton.disabled=busy || (currentIndex===0 && !depotConnected);
  nextButton.disabled=busy || depotConnected;
  nextButton.textContent=currentIndex<frames.length
    ? 'Next Savings Pair'
    : depotConnected ? 'Demonstration Complete' : 'Connect Routes to Depot';
}}

function showRestoredStatus() {{
  finalTable.classList.toggle('show',depotConnected);
  if(depotConnected) {{
    statusBox.className='status complete';
    statusBox.textContent='Complete — the five customer sub-paths are connected to Depot 0; route loads are 95, 90, 90, 90, and 95.';
    return;
  }}
  if(currentIndex===0) {{
    statusBox.className='status';
    statusBox.textContent='Initial state: no savings links selected. Click Next Savings Pair to consider S. No. 1.';
    return;
  }}
  if(currentIndex===frames.length) {{
    statusBox.className='status considering';
    statusBox.textContent='The savings list is exhausted. Click Connect Routes to Depot to join each customer sub-path’s two end nodes to Depot 0.';
    return;
  }}
  const frame=frames[currentIndex-1];
  statusBox.className=frame.accepted?'status accepted':'status rejected';
  statusBox.textContent=frame.accepted
    ? `State after S. No. ${{frame.step}} — accepted (${{frame.i}}, ${{frame.j}}); sub-path load ${{frame.mergedLoad}} / {capacity}.`
    : `State after S. No. ${{frame.step}} — rejected because ${{frame.reason}}. Customer sub-paths are unchanged.`;
}}

async function nextSavingsPair() {{
  if(busy || depotConnected) return;
  if(currentIndex===frames.length) {{
    await connectRoutesToDepot();
    return;
  }}
  busy=true;
  updateControls();
  finalTable.classList.remove('show');
  const frame=frames[currentIndex];
  renderRows(currentIndex);
  const row=document.getElementById(`saving-${{frame.step}}`);
  row.className='considering current';
  row.scrollIntoView({{block:'center',behavior:'smooth'}});
  statusBox.className='status considering';
  statusBox.textContent=`Considering S. No. ${{frame.step}}: saving ${{frame.saving}} for pair (${{frame.i}}, ${{frame.j}})`;
  positionCandidate(frame);
  candidate.className.baseVal='candidate-line preview';
  document.getElementById(`node-${{frame.i}}`).classList.add('preview');
  document.getElementById(`node-${{frame.j}}`).classList.add('preview');
  frame.focusEdges.forEach(id=>{{ const edge=document.getElementById(`edge-${{id}}`); if(edge) edge.classList.add('focus'); }});
  await sleep(900);

  document.getElementById(`node-${{frame.i}}`).classList.remove('preview');
  document.getElementById(`node-${{frame.j}}`).classList.remove('preview');
  if(frame.accepted) {{
    row.className='accepted current';
    row.querySelector('.decision').textContent='✓ Accepted';
    statusBox.className='status accepted';
    statusBox.textContent=`Accepted — customer sub-path ${{frame.mergedRoute}} · load ${{frame.mergedLoad}} / {capacity}`;
    candidate.className.baseVal='candidate-line accepted';
    document.getElementById(`node-${{frame.i}}`).classList.add('accepted');
    document.getElementById(`node-${{frame.j}}`).classList.add('accepted');
    applyEdges(frame.edges);
    renderLoads(frame.loads);
  }} else {{
    row.className='rejected current';
    row.querySelector('.decision').textContent='✕ Rejected';
    statusBox.className='status rejected';
    statusBox.textContent=`Rejected — ${{frame.reason}}. Customer sub-paths are unchanged.`;
    candidate.className.baseVal='candidate-line rejected';
    document.getElementById(`node-${{frame.i}}`).classList.add('rejected');
    document.getElementById(`node-${{frame.j}}`).classList.add('rejected');
  }}
  currentIndex+=1;
  updateProgress();
  await sleep(1200);
  clearTransientClasses();
  renderRows(currentIndex);
  if(currentIndex===frames.length) showRestoredStatus();
  busy=false;
  updateControls();
}}

async function previousSavingsPair() {{
  if(busy || (currentIndex===0 && !depotConnected)) return;
  busy=true;
  updateControls();
  clearTransientClasses();
  if(depotConnected) {{
    depotConnected=false;
    finalTable.classList.remove('show');
    applyEdges(stateEdges(currentIndex));
    renderLoads(stateLoads(currentIndex));
    showRestoredStatus();
    await sleep(1200);
    busy=false;
    updateControls();
    return;
  }}
  currentIndex-=1;
  finalTable.classList.remove('show');
  applyEdges(stateEdges(currentIndex));
  renderLoads(stateLoads(currentIndex));
  renderRows(currentIndex);
  updateProgress();
  showRestoredStatus();
  const target=document.getElementById(`saving-${{Math.max(1,currentIndex)}}`);
  if(target) target.scrollIntoView({{block:'center',behavior:'smooth'}});
  await sleep(1200);
  busy=false;
  updateControls();
}}

async function connectRoutesToDepot() {{
  if(busy || depotConnected || currentIndex!==frames.length) return;
  busy=true;
  updateControls();
  statusBox.className='status considering';
  statusBox.textContent='No more savings pairs remain. Connecting the two end nodes of each customer sub-path to Depot 0...';
  document.getElementById('node-0').classList.add('connecting');
  applyEdges(finalEdges);
  await sleep(1200);
  document.getElementById('node-0').classList.remove('connecting');
  depotConnected=true;
  showRestoredStatus();
  busy=false;
  updateControls();
}}

nextButton.addEventListener('click',nextSavingsPair);
previousButton.addEventListener('click',previousSavingsPair);
renderLoads(initialLoads);
renderRows(0);
updateProgress();
updateControls();
</script></body></html>"""

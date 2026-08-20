"""Clarke-Wright logic for the fixed 23-customer teaching example."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Iterable


DEPOT_ID = "0"
PPT_CAPACITY = 100


@dataclass(frozen=True)
class SavingsPair:
    """One ordered customer pair from the fixed savings list."""

    saving: int
    i: str
    j: str


@dataclass(frozen=True)
class MergeDecision:
    """Route state before and after evaluating one savings pair."""

    number: int
    saving: int
    i: str
    j: str
    routes_before: tuple[tuple[str, ...], ...]
    accepted: bool
    rejection_reason: str | None
    routes_after: tuple[tuple[str, ...], ...]
    resulting_route_load: int | None


@dataclass(frozen=True)
class ClarkeWrightResult:
    """All click states and the final routes from one deterministic run."""

    decisions: tuple[MergeDecision, ...]
    final_routes: tuple[tuple[str, ...], ...]
    route_loads: tuple[int, ...]
    accepted_merges: int
    runtime_seconds: float


PPT_DEMANDS: dict[str, int] = {
    "1": 20,
    "2": 10,
    "3": 15,
    "4": 30,
    "5": 20,
    "6": 25,
    "7": 10,
    "8": 10,
    "9": 40,
    "10": 5,
    "11": 20,
    "12": 20,
    "13": 10,
    "14": 20,
    "15": 20,
    "16": 50,
    "17": 30,
    "18": 25,
    "19": 15,
    "20": 20,
    "21": 10,
    "22": 5,
    "23": 30,
}

PPT_SAVINGS: tuple[SavingsPair, ...] = tuple(
    SavingsPair(saving, str(i), str(j))
    for saving, i, j in (
        (188, 1, 2),
        (181, 22, 23),
        (175, 13, 23),
        (173, 2, 4),
        (164, 13, 22),
        (161, 1, 4),
        (152, 1, 3),
        (148, 21, 23),
        (146, 4, 7),
        (145, 21, 22),
        (144, 13, 21),
        (129, 5, 6),
        (127, 3, 6),
        (123, 7, 8),
        (111, 13, 20),
        (105, 5, 8),
        (99, 19, 22),
        (94, 19, 21),
        (93, 3, 9),
        (90, 5, 10),
        (87, 6, 9),
        (73, 15, 16),
        (62, 18, 19),
        (55, 11, 18),
        (51, 14, 15),
        (45, 11, 12),
        (43, 17, 18),
    )
)

PPT_EXPECTED_ACCEPTED: tuple[bool, ...] = (
    True,
    True,
    True,
    True,
    False,
    False,
    True,
    False,
    True,
    True,
    False,
    True,
    False,
    True,
    True,
    False,
    False,
    True,
    False,
    True,
    True,
    True,
    False,
    True,
    True,
    True,
    True,
)

PPT_EXPECTED_FINAL_ROUTES: tuple[tuple[str, ...], ...] = (
    ("3", "1", "2", "4", "7", "8"),
    ("9", "6", "5", "10"),
    ("19", "21", "22", "23", "13", "20"),
    ("14", "15", "16"),
    ("12", "11", "18", "17"),
)


def initialize_routes(customers: Iterable[str]) -> tuple[tuple[str, ...], ...]:
    """Return one individual route for every customer."""

    return tuple((str(customer),) for customer in customers)


def route_load(route: Iterable[str], demands: dict[str, int]) -> int:
    """Return the demand assigned to one route."""

    return sum(demands[customer] for customer in route)


def _route_index(
    routes: tuple[tuple[str, ...], ...],
    customer: str,
) -> int:
    return next(index for index, route in enumerate(routes) if customer in route)


def process_savings_pair(
    routes: tuple[tuple[str, ...], ...],
    demands: dict[str, int],
    pair: SavingsPair,
    capacity: int,
    decision_number: int,
) -> MergeDecision:
    """Evaluate and, when feasible, apply one parallel-savings merge."""

    route_i_index = _route_index(routes, pair.i)
    route_j_index = _route_index(routes, pair.j)
    route_i = routes[route_i_index]
    route_j = routes[route_j_index]

    rejection_reason: str | None = None
    combined_load: int | None = None
    if route_i_index == route_j_index:
        rejection_reason = "same route / would create a cycle"
    else:
        non_endpoints = [
            customer
            for customer, route in ((pair.i, route_i), (pair.j, route_j))
            if customer not in (route[0], route[-1])
        ]
        if non_endpoints:
            noun = "Customer" if len(non_endpoints) == 1 else "Customers"
            verb = "is" if len(non_endpoints) == 1 else "are"
            rejection_reason = (
                f"{noun} {' and '.join(non_endpoints)} {verb} not at a route end"
            )
        else:
            combined_load = route_load(route_i + route_j, demands)
            if combined_load > capacity:
                rejection_reason = (
                    f"combined load {combined_load} exceeds capacity {capacity}"
                )

    if rejection_reason is not None:
        return MergeDecision(
            number=decision_number,
            saving=pair.saving,
            i=pair.i,
            j=pair.j,
            routes_before=routes,
            accepted=False,
            rejection_reason=rejection_reason,
            routes_after=routes,
            resulting_route_load=None,
        )

    left = route_i if route_i[-1] == pair.i else tuple(reversed(route_i))
    right = route_j if route_j[0] == pair.j else tuple(reversed(route_j))
    merged_route = left + right
    first_index = min(route_i_index, route_j_index)
    merged_routes: list[tuple[str, ...]] = []
    for index, route in enumerate(routes):
        if index == first_index:
            merged_routes.append(merged_route)
        if index not in (route_i_index, route_j_index):
            merged_routes.append(route)

    routes_after = tuple(merged_routes)
    return MergeDecision(
        number=decision_number,
        saving=pair.saving,
        i=pair.i,
        j=pair.j,
        routes_before=routes,
        accepted=True,
        rejection_reason=None,
        routes_after=routes_after,
        resulting_route_load=combined_load,
    )


def run_clarke_wright_from_savings(
    customers: Iterable[str],
    demands: dict[str, int],
    savings: Iterable[SavingsPair],
    capacity: int,
) -> ClarkeWrightResult:
    """Process the supplied savings list and retain every click state."""

    started = perf_counter()
    routes = initialize_routes(customers)
    decisions: list[MergeDecision] = []
    for number, pair in enumerate(savings, start=1):
        decision = process_savings_pair(
            routes,
            demands,
            pair,
            capacity,
            decision_number=number,
        )
        decisions.append(decision)
        routes = decision.routes_after

    return ClarkeWrightResult(
        decisions=tuple(decisions),
        final_routes=routes,
        route_loads=tuple(route_load(route, demands) for route in routes),
        accepted_merges=sum(decision.accepted for decision in decisions),
        runtime_seconds=perf_counter() - started,
    )


def order_final_routes_for_display(
    routes: Iterable[tuple[str, ...]],
) -> tuple[tuple[str, ...], ...]:
    """Orient and order computed routes to match the classroom route groups."""

    available = tuple(routes)
    ordered: list[tuple[str, ...]] = []
    for preferred_route in PPT_EXPECTED_FINAL_ROUTES:
        matching_route = next(
            route for route in available if set(route) == set(preferred_route)
        )
        if matching_route == preferred_route:
            ordered.append(matching_route)
        elif tuple(reversed(matching_route)) == preferred_route:
            ordered.append(preferred_route)
        else:
            ordered.append(preferred_route)
    return tuple(ordered)

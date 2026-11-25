"""Exact arithmetic for the balanced Powerco classroom example."""

from dataclasses import dataclass


COSTS = ((8, 6, 10, 9), (9, 12, 13, 7), (14, 9, 16, 5))
SUPPLY = (35, 50, 40)
DEMAND = (45, 20, 30, 30)
METHODS = {
    "NWCR": "Northwest Corner Rule (NWCR)",
    "LCM": "Least Cost Method (LCM)",
    "VAM": "Vogel’s Approximation Method (VAM)",
}

Cell = tuple[int, int]
Matrix = tuple[tuple[int, ...], ...]


@dataclass(frozen=True)
class Penalty:
    axis: str
    index: int
    low: int
    second: int
    cheapest: tuple[Cell, ...]

    @property
    def difference(self) -> int:
        return self.second - self.low


@dataclass(frozen=True)
class Allocation:
    cell: Cell
    amount: int
    supply_before: tuple[int, ...]
    demand_before: tuple[int, ...]
    candidates: tuple[Cell, ...]
    penalties: tuple[Penalty, ...] = ()
    tied_lines: tuple[Penalty, ...] = ()
    line: Penalty | None = None
    forced: bool = False


@dataclass(frozen=True)
class Potential:
    axis: str
    index: int
    value: int
    cell: Cell
    known: int


def _most_units(cells, supply, demand) -> Cell:
    return min(cells, key=lambda cell: (-min(supply[cell[0]], demand[cell[1]]), cell))


def choose_cell(method, costs, supply, demand) -> Allocation:
    """Describe the next choice, including the candidates present before allocation."""
    rows = [i for i, remaining in enumerate(supply) if remaining > 0]
    cols = [j for j, remaining in enumerate(demand) if remaining > 0]
    active = tuple((i, j) for i in rows for j in cols)
    penalties = ()
    tied_lines = ()
    line = None
    forced = method == "VAM" and (len(rows) == 1 or len(cols) == 1)
    if method == "NWCR" or forced:
        candidates = (active[0],)
    elif method == "LCM":
        minimum = min(costs[i][j] for i, j in active)
        candidates = tuple((i, j) for i, j in active if costs[i][j] == minimum)
    elif method == "VAM":
        lines = [("row", i, tuple((i, j) for j in cols)) for i in rows]
        lines += [("column", j, tuple((i, j) for i in rows)) for j in cols]
        penalties = tuple(_penalty(axis, index, cells, costs) for axis, index, cells in lines)
        maximum = max(p.difference for p in penalties)
        tied_lines = tuple(p for p in penalties if p.difference == maximum)
        line = min(tied_lines, key=lambda p: p.low)
        candidates = line.cheapest
    else:
        raise ValueError(f"Unknown transportation method: {method}")
    i, j = _most_units(candidates, supply, demand)
    return Allocation(
        (i, j), min(supply[i], demand[j]), tuple(supply), tuple(demand),
        candidates, penalties, tied_lines, line, forced,
    )


def _penalty(axis, index, cells, costs) -> Penalty:
    low, second = sorted(costs[i][j] for i, j in cells)[:2]
    return Penalty(axis, index, low, second, tuple((i, j) for i, j in cells if costs[i][j] == low))


def initial_solution(method: str) -> tuple[tuple[Allocation, ...], Matrix]:
    """Build a starting solution for the fixed balanced, nondegenerate example."""
    supply, demand = list(SUPPLY), list(DEMAND)
    allocations = [[0 for _ in DEMAND] for _ in SUPPLY]
    decisions = []
    while any(supply):
        decision = choose_cell(method, COSTS, supply, demand)
        i, j = decision.cell
        allocations[i][j] = decision.amount
        supply[i] -= decision.amount
        demand[j] -= decision.amount
        decisions.append(decision)
    return tuple(decisions), tuple(tuple(row) for row in allocations)


def basis_cells(allocations: Matrix) -> tuple[Cell, ...]:
    return tuple((i, j) for i, row in enumerate(allocations) for j, amount in enumerate(row) if amount)


def solve_potentials(
    costs: Matrix, basis: tuple[Cell, ...], anchor: int = 0,
) -> tuple[tuple[int, ...], tuple[int, ...], tuple[Potential, ...]]:
    """Solve a connected transportation basis, using u1 = anchor."""
    m, n = len(costs), len(costs[0])
    if len(basis) != m + n - 1:
        raise ValueError("Expected a transportation basis with m + n − 1 cells.")
    u = [anchor] + [None] * (m - 1)
    v = [None] * n
    steps = []
    while None in u or None in v:
        for i, j in sorted(basis):
            if u[i] is None and v[j] is not None:
                u[i] = costs[i][j] - v[j]
                steps.append(Potential("u", i, u[i], (i, j), v[j]))
                break
            if v[j] is None and u[i] is not None:
                v[j] = costs[i][j] - u[i]
                steps.append(Potential("v", j, v[j], (i, j), u[i]))
                break
        else:
            raise ValueError("The transportation basis must be connected.")
    return tuple(u), tuple(v), tuple(steps)


def reduced_costs(costs: Matrix, basis: tuple[Cell, ...], u, v) -> dict[Cell, int]:
    basic = set(basis)
    return {
        (i, j): cost - (u[i] + v[j])
        for i, row in enumerate(costs) for j, cost in enumerate(row)
        if (i, j) not in basic
    }

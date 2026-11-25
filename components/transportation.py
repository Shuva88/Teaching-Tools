"""Classroom narrative and browser-side transportation tableau playback."""

from functools import lru_cache
from html import escape
from json import dumps
from pathlib import Path

from algorithms.transportation import (
    COSTS, DEMAND, METHODS, SUPPLY, basis_cells, initial_solution, reduced_costs,
    solve_potentials,
)


def _number(value):
    return f"({value})".replace("-", "−") if value < 0 else str(value)


def _var(symbol, *indices):
    return f"{symbol}<sub>{''.join(str(i + 1) for i in indices)}</sub>"


def _cell_label(cell):
    i, j = cell
    return f"S{i + 1}–D{j + 1}"


def _row_or_column(penalty):
    label = "row S" if penalty.axis == "row" else "column D"
    return f"{label}{penalty.index + 1}"


def _forced_prompt(decision, show_other_case):
    if sum(value > 0 for value in decision.demand_before) == 1:
        prompt = ("Since only one destination column remains, work down the column from top "
                  "to bottom, skipping any rows already crossed out.")
        other = (" If only one supply row remained, we would work across the row from left "
                 "to right, skipping any columns already crossed out.")
    else:
        prompt = ("Since only one supply row remains, work across the row from left to right, "
                  "skipping any columns already crossed out.")
        other = (" If only one destination column remained, we would work down the column from "
                 "top to bottom, skipping any rows already crossed out.")
    return prompt + other if show_other_case else prompt


def _choice_explanation(method, decision):
    cell = _cell_label(decision.cell)
    i, j = decision.cell
    if method == "NWCR":
        return f"Cell {cell} is the top-left (north-west) cell with supply and demand left."
    if decision.forced:
        return (
            f"Only one row or column is left, so the supply and demand left determine how many "
            f"cartons go in cell {cell}."
        )
    details = []
    if method == "LCM":
        details.append(f"The lowest available unit cost is {COSTS[i][j]}.")
    else:
        largest = decision.line
        label = _row_or_column(largest)
        name = label[0].upper() + label[1:]
        details.append(
            f"{name} has a largest penalty of {largest.second} − {largest.low} = {largest.difference}. "
            f"The lowest unit cost there is {largest.low}."
        )
        if len(decision.tied_lines) > 1:
            candidates = ", ".join(f"{_row_or_column(p)} (lowest cost {p.low})" for p in decision.tied_lines)
            reason = ("Choose the row or column with the lowest available cost." if
                      sum(p.low == largest.low for p in decision.tied_lines) == 1 else
                      "If the lowest costs also tie, check rows from top to bottom, then columns from left to right.")
            details.append(f"Rows or columns with equal penalties: {candidates}. {reason}")
    if len(decision.candidates) > 1:
        amounts = {cell: min(decision.supply_before[cell[0]], decision.demand_before[cell[1]])
                   for cell in decision.candidates}
        sizes = ", ".join(f"{_cell_label(cell)} ({amount} cartons)" for cell, amount in amounts.items())
        reason = ("Choose the cell where we can allocate more cartons." if
                  sum(amount == decision.amount for amount in amounts.values()) == 1 else
                  "If the amounts also tie, scan each row from left to right, starting at the top.")
        details.append(f"Equal-cost cells: {sizes}. {reason}")
    details.append(f"Select cell {cell}.")
    if len(decision.candidates) > 1 or len(decision.tied_lines) > 1:
        details.append("Picking a different tied cell can give a different starting allocation.")
    return " ".join(details)


def _penalties(decision):
    return [
        dict(axis=p.axis, index=p.index, low=p.low, second=p.second, value=p.difference)
        for p in decision.penalties
    ]


@lru_cache(maxsize=len(METHODS))
def build_states(method: str) -> tuple[dict, ...]:
    decisions, final = initial_solution(method)
    states = []
    grid = [[0 for _ in DEMAND] for _ in SUPPLY]
    supply, demand = list(SUPPLY), list(DEMAND)
    u, v = [None] * len(SUPPLY), [None] * len(DEMAND)
    rc = [[None for _ in DEMAND] for _ in SUPPLY]
    equations = ()
    phase = "Build the shipping plan"

    def add(title, body, **marks):
        states.append(dict(
            title=title, body=body, phase=phase, grid=[row[:] for row in grid],
            supply=supply[:], demand=demand[:], u=u[:], v=v[:], rc=[row[:] for row in rc],
            equations=equations, **marks,
        ))

    prompts = {
        "NWCR": "Find the top-left (north-west) cell where the warehouse still has cartons "
                "and the destination still has demand to fill.",
        "LCM": "Which cell has the lowest unit cost among those with supply and demand left?",
        "VAM": "Which row or column has the greatest penalty, and which cell in it is cheapest?",
    }
    openings = {
        "NWCR": "In this method, we start at the top-left (north-west) cell.",
        "LCM": "In this method, we start with the cheapest cell.",
    }
    if method == "VAM":
        example = decisions[0].penalties[0]
        add(
            "What does a penalty tell us?",
            "In this method, we use penalties to decide which row or column to work on first. "
            "The penalty is the difference between its two lowest available unit costs. "
            f"In S1, that is {example.second} − {example.low} = {example.difference}. "
            f"If the cheapest cell in S1 becomes unavailable, the next cheapest costs "
            f"₹{example.difference} more per carton.",
            penalties=_penalties(decisions[0]),
        )
    first_forced = True
    for index, decision in enumerate(decisions, 1):
        i, j = decision.cell
        cell = _cell_label(decision.cell)
        penalties = _penalties(decision)
        prompt = prompts[method]
        title = f"Allocation {index} · Which cell comes next?"
        if decision.forced:
            prompt = _forced_prompt(decision, show_other_case=first_forced)
            first_forced = False
        elif index == 1 and method in openings:
            title = f"Allocation {index} · How do we start?"
            prompt = f"{openings[method]} Which cell is that?"
        add(title, prompt, penalties=penalties)
        add(
            f"How much can we allocate to cell {cell}?",
            f"{_choice_explanation(method, decision)} "
            f"<strong>How many cartons can we ship with {supply[i]} available and {demand[j]} needed?</strong>",
            penalties=penalties, selected=decision.cell, candidates=decision.candidates,
            lines=[(p.axis, p.index) for p in decision.tied_lines],
            selected_line=(decision.line.axis, decision.line.index) if decision.line else None,
        )
        calculation = f"The smaller of {supply[i]} and {demand[j]} is {decision.amount}"
        grid[i][j] = decision.amount
        supply[i] -= decision.amount
        demand[j] -= decision.amount
        retired = []
        if supply[i] == 0:
            retired.append(f"row S{i + 1}")
        if demand[j] == 0:
            retired.append(f"column D{j + 1}")
        note = ("<strong>Observe that</strong> we did not use the unit costs to choose the cell."
                if method == "NWCR" and index == 1 else "")
        add(
            f"Allocate {decision.amount} cartons to cell {cell}",
            f"<strong>{calculation}.</strong> The remaining supply at S{i + 1} is {supply[i]} "
            f"and the remaining demand at D{j + 1} is {demand[j]}. "
            f"Cross out {' and '.join(retired)}.",
            selected=decision.cell, note=note,
        )

    basis = basis_cells(final)
    total = sum(COSTS[i][j] * final[i][j] for i, j in basis)
    products = " + ".join(f"{COSTS[i][j]} × {final[i][j]}" for i, j in basis)
    phase = "Optimality test"
    add(
        "Can we lower the total cost?",
        f"All supply and demand are met. Total cost = {products} = <strong>{total:,}</strong>. "
        "We now check whether this plan is optimal.",
    )
    equations = tuple((i, j, COSTS[i][j]) for i, j in basis)
    add(
        "Write an equation for each basic cell",
        "In a transportation problem, each basic cell gives one equation, "
        "<strong>u<sub>i</sub> + v<sub>j</sub> = c<sub>ij</sub></strong>. "
        "In words, the row and column dual variables add up to the unit cost of that cell. "
        "Six independent equations leave one "
        "of the seven values free. We can fix it to find one of infinitely many solutions.",
    )
    u[0] = 0
    add(
        "Let us set u₁ = 0",
        "Any of the seven variables can be set to zero. A useful shortcut is to pick one "
        "that appears most often, so more equations can be solved right away. Here we start "
        "with u<sub>1</sub> for consistency across the three methods.",
        highlighted_duals=[("u", 0)],
    )
    solved_u, solved_v, moves = solve_potentials(COSTS, basis)
    for move in moves:
        i, j = move.cell
        target = _var(move.axis, move.index)
        known = _var("v", j) if move.axis == "u" else _var("u", i)
        margin = u if move.axis == "u" else v
        margin[move.index] = move.value
        equation_number = basis.index(move.cell) + 1
        add(
            f"Find {target} from cell {_cell_label(move.cell)}",
            f"Using {known} = {_number(move.known)} in equation {equation_number}, "
            f"we get <strong>{target} = {_number(move.value)}</strong>.",
            selected=move.cell, equation=move.cell, highlighted_duals=[("u", i), ("v", j)],
        )

    costs = reduced_costs(COSTS, basis, solved_u, solved_v)
    add(
        "How do we find the reduced cost of a cell with no allocation?",
        "In a transportation problem, the reduced cost of a non-basic variable is the cell’s unit cost "
        "minus the sum of its row and column dual variables. In symbols, "
        "<strong>RC<sub>ij</sub> = c<sub>ij</sub> − (u<sub>i</sub> + v<sub>j</sub>)</strong>.",
    )
    last_cell = next(reversed(costs))
    for cell, value in costs.items():
        i, j = cell
        rc[i][j] = value
        add(
            f"Compute the reduced cost for cell {_cell_label(cell)}",
            f"<strong>{_var('RC', i, j)} = {COSTS[i][j]} − "
            f"({_number(u[i])} + {_number(v[j])}) = {_number(value)}</strong>. "
            f"Allocating one carton to this cell and adjusting the other allocations would "
            f"{'lower' if value < 0 else 'raise'} total cost by ₹{abs(value)}."
            if value else f"{_var('RC', i, j)} = 0. The corresponding adjustment leaves total cost unchanged.",
            selected=cell, highlighted_duals=[("u", i), ("v", j)],
            note=(
                "<strong>Note.</strong> Setting a different dual variable to zero initially would give "
                "different values for u<sub>i</sub> and v<sub>j</sub>. However, for the same allocation, "
                "their sum in each cell stays the same, so every reduced cost computed stays the same too."
                if cell == last_cell else ""
            ),
        )
    phase = "Result"
    if any(value < 0 for value in costs.values()):
        add(
            "The current allocation is not optimal",
            f"The presence of a negative reduced cost tells us that we can lower the current total cost "
            f"of <strong>₹{total:,}</strong>. We can do this by allocating cartons to a cell with a "
            "negative reduced cost and adjusting the other allocations so that supply and demand are still met.",
        )
    else:
        add(
            "The VAM solution is optimal for this example",
            f"None of the reduced costs is negative, so the current plan has the lowest possible cost "
            f"of <strong>₹{total:,}</strong>.",
        )
    return tuple(states)


def landing_tableau() -> str:
    headers = "".join(f'<th scope="col">D{j + 1}</th>' for j in range(len(DEMAND)))
    rows = []
    for i, costs in enumerate(COSTS):
        cells = "".join(f'<td>{cost}</td>' for cost in costs)
        rows.append(f'<tr><th scope="row">S{i + 1}</th>{cells}<th>{SUPPLY[i]}</th></tr>')
    demands = "".join(f"<th>{amount}</th>" for amount in DEMAND)
    return (
        '<table class="transportation-input" aria-label="Shipping costs, supply and demand">'
        f'<thead><tr><th scope="col">Source</th>{headers}<th scope="col">Supply</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody>'
        f'<tfoot><tr><th scope="row">Demand</th>{demands}<th>{sum(DEMAND)}</th></tr></tfoot></table>'
    )


def playback_html(method: str) -> str:
    template = Path(__file__).with_name("transportation_player.html").read_text(encoding="utf-8")
    data = dumps(
        dict(method=method, costs=COSTS, supply=SUPPLY, demand=DEMAND, states=build_states(method)),
        ensure_ascii=False,
    ).replace("<", "\\u003c")
    return template.replace("__METHOD__", escape(METHODS[method])).replace("__DATA__", data)

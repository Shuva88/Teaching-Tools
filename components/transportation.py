"""Classroom narrative and browser-side transportation tableau playback."""

from functools import lru_cache
from html import escape
from json import dumps
from pathlib import Path

from algorithms.transportation import (
    COSTS, DEMAND, METHODS, SUPPLY, VARIANT_COSTS, basis_cells, improving_pivot,
    initial_solution, reduced_costs, solve_potentials,
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


def _choice_explanation(method, decision, unit_cost):
    cell = _cell_label(decision.cell)
    if method == "NWCR":
        return f"Cell {cell} is the top-left (north-west) cell with supply and demand left."
    if decision.forced:
        return (
            f"Only one row or column is left, so the supply and demand left determine how many "
            f"cartons go in cell {cell}."
        )
    details = []
    if method == "LCM":
        details.append(f"The lowest available unit cost is {unit_cost}.")
    else:
        largest = decision.line
        label = _row_or_column(largest)
        name = label[0].upper() + label[1:]
        details.append(
            f"{name} has a largest penalty of {largest.second} − {largest.low} = {largest.difference}. "
            f"The lowest unit cost there is {largest.low}."
        )
        if len(decision.tied_lines) > 1:
            labels = [_row_or_column(p) for p in decision.tied_lines]
            names = f"{', '.join(labels[:-1])} and {labels[-1]}"
            costs = [f"₹{p.low}" for p in decision.tied_lines]
            described_costs = f"{', '.join(costs[:-1])} and {costs[-1]}, respectively"
            if len(set(costs)) == 1:
                described_costs = f"{costs[0]} in each case"
            details = [
                f"{names[0].upper() + names[1:]} tie for the largest penalty of {largest.difference}. "
                f"Their lowest unit costs are {described_costs}."
            ]
            if len(decision.candidates) == 1:
                details.append(f"Choose {label} because it has the lowest available cost.")
    if len(decision.candidates) > 1:
        amounts = {
            candidate: min(decision.supply_before[candidate[0]], decision.demand_before[candidate[1]])
            for candidate in decision.candidates
        }
        leaders = [candidate for candidate, amount in amounts.items() if amount == decision.amount]
        if method == "VAM":
            prefix = "At that cost," if len(decision.tied_lines) > 1 else "At the same lowest unit cost,"
            if len(leaders) == len(amounts) == 2:
                first, second = map(_cell_label, amounts)
                details.append(f"{prefix} {first} and {second} can each take {decision.amount} cartons.")
            else:
                sizes = [f"{_cell_label(candidate)} can take {amount} cartons" for candidate, amount in amounts.items()]
                details.append(f"{prefix} {', '.join(sizes[:-1])} and {sizes[-1]}.")
            if len(leaders) == 1:
                details.append(f"Choose {cell} because it permits the largest allocation.")
            else:
                position = "leftmost" if all(i == decision.cell[0] for i, _ in leaders) else "topmost"
                details.append(
                    f"Choose {cell}, the {position} candidate, as per our tie breaking convention."
                )
            return " ".join(details)
        sizes = ", ".join(f"{_cell_label(cell)} ({amount} cartons)" for cell, amount in amounts.items())
        if len(leaders) == 1:
            reason = "Choose the cell where we can allocate the most cartons."
        else:
            reason = "If the amounts also tie, scan each row from left to right, starting at the top."
        details.append(f"Possible allocations for equal-cost cells are {sizes}. {reason}")
    details.append(f"Select cell {cell}.")
    if len(decision.candidates) > 1:
        details.append("Picking a different tied cell can give a different starting allocation.")
    return " ".join(details)


def _penalties(decision):
    return [
        dict(axis=p.axis, index=p.index, low=p.low, second=p.second, value=p.difference)
        for p in decision.penalties
    ]


@lru_cache(maxsize=len(METHODS) + 1)
def build_states(method: str, example: int = 1) -> tuple[dict, ...]:
    cost_matrix = COSTS if example == 1 else VARIANT_COSTS
    decisions, final = initial_solution(method, cost_matrix)
    states = []
    grid = [[0 for _ in DEMAND] for _ in SUPPLY]
    supply, demand = list(SUPPLY), list(DEMAND)
    phase = "Build the shipping plan"

    def add(title, body, **marks):
        states.append(dict(
            title=title, body=body, phase=phase, grid=[row[:] for row in grid],
            supply=supply[:], demand=demand[:], u=[None] * len(SUPPLY), v=[None] * len(DEMAND),
            rc=[[None for _ in DEMAND] for _ in SUPPLY], equations=(),
        ) | marks)

    prompts = {
        "NWCR": "Find the top-left (north-west) cell where the warehouse still has cartons "
                "and the destination still has demand to fill.",
        "LCM": "Which cell has the lowest unit cost among those with supply and demand left?",
        "VAM": "Which row or column has the greatest penalty, and which cell in it is cheapest?",
    }
    openings = {
        "NWCR": "In NWCR, we start at the top-left (north-west) cell.",
        "LCM": "In LCM, we start with the cheapest cell.",
    }
    if method == "VAM":
        penalty_example = decisions[0].penalties[0]
        add(
            "What does a penalty tell us?",
            "In VAM, we use penalties to decide which row or column to work on first. "
            "The penalty is the difference between its two lowest available unit costs. "
            f"In S1, that is {penalty_example.second} − {penalty_example.low} = {penalty_example.difference}. "
            f"If the cheapest cell in S1 becomes unavailable, the next cheapest costs "
            f"₹{penalty_example.difference} more per carton.",
            penalties=_penalties(decisions[0]),
        )
        if example == 2:
            add(
                "How do we break a VAM tie?",
                "<strong>Penalty tie:</strong> Among the tied rows or columns, identify the cell(s) "
                "with the lowest available transportation cost."
                "<br><strong>Cost tie:</strong> If multiple candidate cells have the same lowest cost, "
                "choose the one that permits the largest allocation. This applies both across tied "
                "rows or columns and within a selected row or column."
                "<br><strong>Allocation tie:</strong> If the possible allocations also tie, choose the "
                "topmost candidate and then the leftmost if needed.",
                penalties=_penalties(decisions[0]),
                note="These are tie-breaking conventions. Different choices may lead to different "
                     "initial basic feasible solutions and transportation costs.",
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
        compare_amounts = method == "VAM" and len(decision.candidates) > 1
        question = (
            "" if compare_amounts else
            f" <strong>How many cartons can we ship with {supply[i]} available and {demand[j]} needed?</strong>"
        )
        add(
            f"Why choose cell {cell}?" if compare_amounts else f"How much can we allocate to cell {cell}?",
            _choice_explanation(method, decision, cost_matrix[i][j]) + question,
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

    phase = "Optimality test"
    products, total = _cost_calculation(cost_matrix, final)
    add(
        "Can we lower the total cost?",
        f"All supply and demand are met. Total cost = {products} = <strong>{total:,}</strong>. "
        "We now check whether this plan is optimal.",
    )
    iteration = 0
    while True:
        costs = _add_optimality(add, cost_matrix, final, example, first_test=iteration == 0)
        panel = {key: states[-1][key] for key in ("equations", "u", "v", "rc")}
        pivot = improving_pivot(final, costs) if example == 2 else None
        if pivot is None:
            break

        iteration += 1
        phase = f"Iteration {iteration}"
        total = _add_uv_steps(add, cost_matrix, final, costs, pivot, total, panel, iteration)
        final = pivot.updated
        grid = final
        phase = f"Optimality test after iteration {iteration}"

    phase = "Result"
    if any(value < 0 for value in costs.values()):
        add(
            "The current allocation is not optimal",
            f"The presence of a negative reduced cost tells us that we can lower the current total cost "
            f"of <strong>₹{total:,}</strong>. We can do this by allocating cartons to a cell with a "
            "negative reduced cost and adjusting the other allocations so that supply and demand are still met.",
            **panel,
        )
    else:
        title = ("The VAM solution is optimal for this example" if example == 1
                 else f"The solution is optimal after {iteration} UV iterations")
        zero_cell = next((cell for cell, value in costs.items() if value == 0), None)
        note = ""
        if example == 2 and zero_cell is not None:
            variable = _var("x", *zero_cell)
            note = (
                f"<strong>Note.</strong> The non-basic variable {variable} in cell "
                f"{_cell_label(zero_cell)} has zero reduced cost. "
                f"Allocating one carton to this cell and adjusting the other allocations leaves the total cost unchanged. "
                f"Another UV iteration with {variable} entering the basis would thus give an alternate optimal solution."
            )
        add(
            title,
            f"None of the reduced costs is negative, so the current plan has the lowest possible cost "
            f"of <strong>₹{total:,}</strong>.",
            note=note, **panel,
        )
    return tuple(states)


def _add_optimality(add, cost_matrix, allocations, example, *, first_test):
    basis = basis_cells(allocations)
    equations = tuple((i, j, cost_matrix[i][j]) for i, j in basis)
    u, v = [None] * len(SUPPLY), [None] * len(DEMAND)
    rc = [[None for _ in DEMAND] for _ in SUPPLY]

    def show(title, body, **marks):
        add(title, body, u=u[:], v=v[:], rc=[row[:] for row in rc], equations=equations, **marks)

    show(
        "Write an equation for each basic cell",
        "In a transportation problem, each basic cell gives one equation, "
        "<strong>u<sub>i</sub> + v<sub>j</sub> = c<sub>ij</sub></strong>. "
        "In words, the row and column dual variables add up to the unit cost of that cell. "
        "Six independent equations leave one "
        "of the seven values free. So, we can fix one of the values (to say 0) "
        "to find one of infinitely many solutions.",
    )
    u[0] = 0
    show(
        "Let us set u₁ = 0",
        "Any of the seven variables can be set to zero. A useful shortcut is to pick one "
        "that appears most often, so more equations can be solved right away. Here we start "
        + ("with u<sub>1</sub> for consistency across the three methods." if example == 1
           else "with u<sub>1</sub> again." if not first_test else "with u<sub>1</sub>, as in Example 1."),
        highlighted_duals=[("u", 0)],
    )
    solved_u, solved_v, moves = solve_potentials(cost_matrix, basis)
    for move in moves:
        i, j = move.cell
        target = _var(move.axis, move.index)
        known = _var("v", j) if move.axis == "u" else _var("u", i)
        margin = u if move.axis == "u" else v
        margin[move.index] = move.value
        equation_number = basis.index(move.cell) + 1
        show(
            f"Find {target} from cell {_cell_label(move.cell)}",
            f"Using {known} = {_number(move.known)} in equation {equation_number}, "
            f"we get <strong>{target} = {_number(move.value)}</strong>.",
            selected=move.cell, equation=move.cell, highlighted_duals=[("u", i), ("v", j)],
        )

    costs = reduced_costs(cost_matrix, basis, solved_u, solved_v)
    show(
        "How do we find the reduced cost of a cell with no allocation?",
        "In a transportation problem, the reduced cost of a non-basic variable is the cell’s unit cost "
        "minus the sum of its row and column dual variables. In symbols, "
        "<strong>RC<sub>ij</sub> = c<sub>ij</sub> − (u<sub>i</sub> + v<sub>j</sub>)</strong>.",
    )
    last_cell = next(reversed(costs))
    for cell, value in costs.items():
        i, j = cell
        rc[i][j] = value
        show(
            f"Compute the reduced cost for cell {_cell_label(cell)}",
            f"<strong>{_var('RC', i, j)} = {cost_matrix[i][j]} − "
            f"({_number(u[i])} + {_number(v[j])}) = {_number(value)}</strong>. "
            f"Allocating one carton to this cell and adjusting the other allocations would "
            f"{'lower' if value < 0 else 'raise'} total cost by ₹{abs(value)}."
            if value else
            f"<strong>{_var('RC', i, j)} = {cost_matrix[i][j]} − "
            f"({_number(u[i])} + {_number(v[j])}) = 0</strong>. "
            f"The non-basic variable {_var('x', i, j)} has zero reduced cost. "
            "Allocating one carton to this cell and adjusting the other allocations leaves total cost unchanged.",
            selected=cell, highlighted_duals=[("u", i), ("v", j)],
            note=(
                "<strong>Note.</strong> Setting a different dual variable to zero initially would give "
                "different values for u<sub>i</sub> and v<sub>j</sub>. However, for the same allocation, "
                "their sum in each cell stays the same, so every reduced cost computed stays the same too."
                if first_test and cell == last_cell else ""
            ),
        )
    return costs


def _cost_calculation(cost_matrix, allocations):
    basis = basis_cells(allocations)
    terms = " + ".join(f"{cost_matrix[i][j]} × {allocations[i][j]}" for i, j in basis)
    total = sum(cost_matrix[i][j] * allocations[i][j] for i, j in basis)
    return terms, total


def _add_uv_steps(add, cost_matrix, allocations, costs, pivot, total, panel, iteration):
    cycle = pivot.cycle
    entering = cycle[0]
    label = _cell_label(entering)
    entering_var = _var("x", *entering)
    leaving_var = _var("x", *pivot.leaving)
    rc = costs[entering]
    add(
        "Which non-basic variable should enter?",
        "A negative reduced cost tells us that the current allocation can be improved. "
        "Which cell gives the greatest drop in total cost per additional carton?",
        **panel,
    )
    add(
        f"{entering_var} enters the basis",
        f"Cell {label} corresponds to {entering_var}. Its reduced cost of "
        f"<strong>{_number(rc)}</strong> is the most negative. "
        "Let δ be the number of cartons added to this cell. Which other allocations must change "
        "so that each row still matches its supply and each column still matches its demand?",
        selected=entering, **panel,
    )
    moves = [_loop_move(previous, current, index)
             for index, (previous, current) in enumerate(zip(cycle, cycle[1:]), 1)]
    add(
        "Start the loop and mark the first two turns",
        f"Start at {label} with (+), meaning its allocation will increase by δ cartons.<br>{moves[0]}",
        note=moves[1], cycle=cycle[:3], cycle_closed=False, **panel,
    )
    add(
        "Continue alternating directions and signs",
        moves[2], note=moves[3], cycle=cycle[:5], cycle_closed=False, **panel,
    )
    add(
        "Close the loop",
        f"{moves[4]} Move {_loop_direction(cycle[-1], entering)} along row S{entering[0] + 1} "
        f"to return to {label}.",
        note="Each affected row and column gains and loses δ cartons, so its total stays the same. "
             "Tracing these cells in the opposite direction gives the same loop and the same signs.",
        cycle=cycle, **panel,
    )
    i, j = next(cell for cell in basis_cells(allocations) if cell not in cycle)
    junction = min((cell for cell in cycle if cell[0] == i), key=lambda cell: abs(cell[1] - j))
    add(
        "Why is this the only loop?",
        f"Suppose we move {_loop_direction(junction, (i, j))} from {_cell_label(junction)} to "
        f"{_cell_label((i, j))}, as shown by the red dashed line. "
        f"We would then have to turn vertically in column D{j + 1}, "
        "but that column has no other allocated cell. This path gets stuck.",
        note=f"<strong>Note.</strong> This is the only loop for {label}. It starts at a non-basic "
             "cell and turns only at basic cells, which are the cells with allocations in this example.",
        trial=(junction, (i, j)), cycle=cycle, **panel,
    )
    add(
        "How large can δ be?",
        "Each donor cell loses δ cartons. None can drop below zero, so the smallest of the "
        "donor allocations limits the increase in the entering cell.",
        cycle=pivot.cycle, **panel,
    )
    donors = ", ".join(str(allocations[i][j]) for i, j in cycle[1::2])
    leaving_cell = _cell_label(pivot.leaving)
    add(
        f"Set δ = {pivot.delta}",
        f"The donor cells hold {donors} cartons. The smallest amount is <strong>{pivot.delta}</strong>. "
        f"That amount is in the highlighted cell {leaving_cell}.<br>"
        f"As the allocation in cell {label} ({entering_var}) increases by {pivot.delta} cartons, "
        f"the allocation in donor cell {leaving_cell} ({leaving_var}) falls to zero. "
        f"Thus, {leaving_var} leaves the basis.",
        selected=pivot.leaving, cycle=pivot.cycle, **panel,
    )
    decrease = -rc * pivot.delta
    terms, new_total = _cost_calculation(cost_matrix, pivot.updated)
    add(
        f"Update the allocations by δ = {pivot.delta}",
        f"Add {pivot.delta} at every (+) and subtract {pivot.delta} at every (−). "
        f"The cost falls by <strong>₹{decrease:,}</strong> because each of the {pivot.delta} "
        f"cartons added to {label} lowers cost by ₹{-rc}. "
        f"New total = ₹{total:,} − ({pivot.delta} × ₹{-rc}) = <strong>₹{new_total:,}</strong>."
        + (" We now have a new basic feasible solution." if iteration == 1 else ""),
        grid=pivot.updated, cycle=pivot.cycle,
    )
    next_test = (
        "That completes the first iteration. We now check whether this plan is optimal. "
        "Let’s begin the second by finding the dual "
        "variables for the updated allocation and checking its reduced costs."
        if iteration == 1
        else "Let’s find the new dual variables and check the reduced costs again. "
             "Is this allocation optimal?"
    )
    add(
        "Verify the new total cost",
        f"Multiply each unit cost by its new allocation. {terms} = <strong>₹{new_total:,}</strong>.",
        note=next_test,
        grid=pivot.updated,
    )
    return new_total


def _loop_direction(previous, current):
    if previous[0] == current[0]:
        return "left" if current[1] < previous[1] else "right"
    return "up" if current[0] < previous[0] else "down"


def _loop_move(previous, current, index):
    i, j = current
    if previous[0] == i:
        line = f"row S{i + 1}"
        balance = f"S{i + 1} must still ship {SUPPLY[i]} cartons"
    else:
        line = f"column D{j + 1}"
        balance = f"D{j + 1} must still receive {DEMAND[j]} cartons"
    subtracting = index % 2
    adjustment = "subtract" if subtracting else "add"
    sign = "−" if subtracting else "+"
    return (
        f"{balance}, so we need to {adjustment} δ cartons at another allocated cell in {line}. "
        f"Move {_loop_direction(previous, current)} to {_cell_label(current)} and mark ({sign})."
    )


def page_style(started: bool) -> str:
    css = Path(__file__).with_name("transportation_page.css").read_text(encoding="utf-8")
    return f"<style>{css.replace('__OVERFLOW__', 'clip' if started else 'auto')}</style>"


def landing_tableau(cost_matrix=COSTS) -> str:
    headers = "".join(f'<th scope="col">D{j + 1}</th>' for j in range(len(DEMAND)))
    rows = []
    for i, costs in enumerate(cost_matrix):
        cells = "".join(f'<td>{cost}</td>' for cost in costs)
        rows.append(f'<tr><th scope="row">S{i + 1}</th>{cells}<th>{SUPPLY[i]}</th></tr>')
    demands = "".join(f"<th>{amount}</th>" for amount in DEMAND)
    return (
        '<table class="transportation-input" aria-label="Shipping costs, supply and demand">'
        f'<thead><tr><th scope="col">Source</th>{headers}<th scope="col">Supply</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody>'
        f'<tfoot><tr><th scope="row">Demand</th>{demands}<th>{sum(DEMAND)}</th></tr></tfoot></table>'
    )


def playback_html(method: str, example: int = 1) -> str:
    template = Path(__file__).with_name("transportation_player.html").read_text(encoding="utf-8")
    data = dumps(
        dict(
            method=method, example=example, costs=COSTS if example == 1 else VARIANT_COSTS,
            supply=SUPPLY, demand=DEMAND, states=build_states(method, example),
        ),
        ensure_ascii=False,
    ).replace("<", "\\u003c")
    return template.replace("__METHOD__", escape(METHODS[method])).replace("__DATA__", data)

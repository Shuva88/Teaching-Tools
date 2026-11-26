"""Verify the worked slide results and the teaching order."""

from pathlib import Path
from unittest import TestCase

from streamlit.testing.v1 import AppTest

from algorithms.transportation import (
    COSTS, DEMAND, SUPPLY, VARIANT_COSTS, basis_cells, choose_cell, improving_pivot,
    initial_solution, reduced_costs, solve_potentials,
)
from components.transportation import build_states


# Source and destination indices below follow the slide labels, starting at one.
EXPECTED = {
    "NWCR": (
        ((1, 1, 35), (2, 1, 10), (2, 2, 20), (2, 3, 20), (3, 3, 10), (3, 4, 30)),
        1180, (0, 1, 4), (8, 11, 12, 1), (-5, -2, 8, 5, 2, -6),
    ),
    "LCM": (
        ((3, 4, 30), (1, 2, 20), (1, 1, 15), (2, 1, 30), (2, 3, 20), (3, 3, 10)),
        1080, (0, 1, 4), (8, 6, 12, 1), (-2, 8, 5, 5, 2, -1),
    ),
    "VAM": (
        ((3, 4, 30), (3, 2, 10), (1, 2, 10), (2, 1, 45), (1, 3, 25), (2, 3, 5)),
        1020, (0, 3, 3), (6, 6, 10, 2), (2, 7, 3, 2, 5, 3),
    ),
}


class PowercoTests(TestCase):
    def test_variant_vam_and_uv_match_worked_solution(self):
        decisions, grid = initial_solution("VAM", VARIANT_COSTS)
        self.assertEqual(tuple((step.cell, step.amount) for step in decisions), (
            ((1, 3), 30), ((2, 1), 20), ((1, 0), 20), ((0, 0), 25), ((0, 2), 10), ((2, 2), 20),
        ))
        self.assertEqual([(p.axis, p.index, p.low) for p in decisions[0].tied_lines],
                         [("row", 1, 5), ("row", 2, 5)])
        self.assertEqual([(p.axis, p.index, p.low) for p in decisions[3].tied_lines],
                         [("column", 0, 8), ("column", 2, 10)])

        checks = (
            (((2, 3), (1, 3), (1, 0), (0, 0), (0, 2), (2, 2)), 20, (2, 2), 1130, 1030),
            (((0, 1), (2, 1), (2, 3), (1, 3), (1, 0), (0, 0)), 5, (0, 0), 1030, 1020),
        )
        def total(allocations):
            return sum(VARIANT_COSTS[i][j] * value
                       for i, row in enumerate(allocations) for j, value in enumerate(row))

        for cycle, delta, leaving, old_total, new_total in checks:
            basis = basis_cells(grid)
            u, v, _ = solve_potentials(VARIANT_COSTS, basis)
            rc = reduced_costs(VARIANT_COSTS, basis, u, v)
            pivot = improving_pivot(grid, rc)
            self.assertEqual((pivot.cycle, pivot.delta, pivot.leaving), (cycle, delta, leaving))
            self.assertEqual(total(grid), old_total)
            self.assertEqual(total(pivot.updated), new_total)
            self.assertEqual(new_total - old_total, delta * rc[cycle[0]])
            grid = pivot.updated
            self.assertEqual(tuple(map(sum, grid)), SUPPLY)
            self.assertEqual(tuple(map(sum, zip(*grid))), DEMAND)
            self.assertTrue(all(value >= 0 for row in grid for value in row))
        self.assertEqual(grid, ((0, 5, 30, 0), (45, 0, 0, 5), (0, 15, 0, 25)))
        basis = basis_cells(grid)
        u, v, _ = solve_potentials(VARIANT_COSTS, basis)
        rc = reduced_costs(VARIANT_COSTS, basis, u, v)
        self.assertTrue(all(value >= 0 for value in rc.values()))
        self.assertEqual(rc[(1, 2)], 0)
        self.assertIsNone(improving_pivot(grid, rc))

        states = build_states("VAM", example=2)
        self.assertIn("topmost candidate and then the leftmost if needed", states[1]["body"])
        self.assertIn("as per our tie breaking convention", states[3]["body"])
        self.assertIn("₹8 and ₹10, respectively", states[12]["body"])
        loops = [state for state in states if state["title"] == "Close the loop"]
        self.assertEqual([state["cycle"] for state in loops], [check[0] for check in checks])
        self.assertTrue(all("opposite direction" in state["note"] for state in loops))
        partial = [state["cycle"] for state in states if state.get("cycle_closed") is False]
        self.assertEqual(partial, [check[0][:size] for check in checks for size in (3, 5)])
        explanations = [state for state in states if state["title"] == "Why is this the only loop?"]
        self.assertIn("column D2", explanations[0]["body"])
        self.assertIn("column D3", explanations[1]["body"])
        self.assertTrue(all("red dashed line" in state["body"] for state in explanations))
        self.assertEqual([state["trial"] for state in explanations],
                         [((2, 2), (2, 1)), ((0, 1), (0, 2))])
        verified = [state["body"] for state in states if state["title"] == "Verify the new total cost"]
        self.assertCountEqual([next(cost for cost in ("₹1,030", "₹1,020") if cost in body) for body in verified],
                              ["₹1,030", "₹1,020"])
        first_update = next(state for state in states if state["title"] == "Verify the new total cost")
        self.assertIn("begin the second", first_update["note"])
        first_limit = next(state for state in states if state["title"] == "Set δ = 20")
        self.assertTrue(first_limit["body"].startswith("The donor cells hold 30, 25, 20 cartons."))
        self.assertIn("highlighted cell S3–D3", first_limit["body"])
        self.assertIn("S3–D4 (x<sub>34</sub>)", first_limit["body"])
        self.assertIn("S3–D3 (x<sub>33</sub>)", first_limit["body"])
        second_limit = next(state for state in states if state["title"] == "Set δ = 5")
        self.assertTrue(second_limit["body"].startswith("The donor cells hold 20, 10, 5 cartons."))
        self.assertIn("highlighted cell S1–D1", second_limit["body"])
        self.assertIn("S1–D2 (x<sub>12</sub>)", second_limit["body"])
        self.assertIn("S1–D1 (x<sub>11</sub>)", second_limit["body"])
        self.assertIn("Allocating one carton", states[34]["body"])
        self.assertIn("Allocating one carton", states[83]["body"])
        self.assertEqual(states[-1]["phase"], "Result")
        self.assertIn("₹1,020", states[-1]["body"])
        self.assertTrue(states[-1]["note"].startswith("<strong>Note.</strong>"))
        self.assertIn("x<sub>23</sub> entering the basis", states[-1]["note"])
        self.assertIn("alternate optimal solution", states[-1]["note"])

    def test_allocations_and_optimality_certificates(self):
        for method, (order, total, expected_u, expected_v, expected_rc) in EXPECTED.items():
            with self.subTest(method=method):
                steps, allocations = initial_solution(method)
                self.assertEqual(
                    tuple((i + 1, j + 1, step.amount) for step in steps for i, j in [step.cell]),
                    order,
                )
                supply, demand = list(SUPPLY), list(DEMAND)
                for step in steps:
                    i, j = step.cell
                    self.assertEqual(step.supply_before, tuple(supply))
                    self.assertEqual(step.demand_before, tuple(demand))
                    self.assertEqual(step.amount, min(supply[i], demand[j]))
                    supply[i] -= step.amount
                    demand[j] -= step.amount
                self.assertFalse(any(supply) or any(demand))
                self.assertEqual(tuple(map(sum, allocations)), SUPPLY)
                self.assertEqual(tuple(map(sum, zip(*allocations))), DEMAND)
                basis = basis_cells(allocations)
                self.assertEqual(len(basis), len(SUPPLY) + len(DEMAND) - 1)
                self.assertEqual(sum(COSTS[i][j] * allocations[i][j] for i, j in basis), total)
                u, v, moves = solve_potentials(COSTS, basis)
                self.assertEqual((u, v), (expected_u, expected_v))
                seen = {("u", 0): 0}
                for move in moves:
                    i, j = move.cell
                    target = (move.axis, move.index)
                    other = ("v", j) if move.axis == "u" else ("u", i)
                    eligible = [
                        (row, col) for row, col in basis
                        if (("u", row) in seen) != (("v", col) in seen)
                    ]
                    self.assertEqual(move.cell, eligible[0])
                    self.assertEqual(move.known, seen[other])
                    self.assertNotIn(target, seen)
                    self.assertEqual(move.value + move.known, COSTS[i][j])
                    seen[target] = move.value
                rc = reduced_costs(COSTS, basis, u, v)
                self.assertEqual(tuple(rc.values()), expected_rc)
                alt_u, alt_v, _ = solve_potentials(COSTS, basis, anchor=5)
                self.assertEqual(rc, reduced_costs(COSTS, basis, alt_u, alt_v))
                if method == "VAM":
                    self.assertTrue(all(value > 0 for value in rc.values()))
                    self.assertEqual(sum(a * b for a, b in zip(u, SUPPLY))
                                     + sum(a * b for a, b in zip(v, DEMAND)), total)

    def test_penalty_and_cost_ties(self):
        choice = choose_cell("VAM", ((3, 6), (1, 4)), (4, 5), (5, 4))
        self.assertEqual([p.index for p in choice.tied_lines], [0, 1])
        self.assertEqual(choice.cell, (1, 0))
        tied = choose_cell("VAM", ((1, 1), (1, 1)), (3, 5), (2, 6))
        self.assertEqual((tied.line.axis, tied.line.index), ("row", 1))
        self.assertEqual(tied.candidates, ((0, 0), (0, 1), (1, 0), (1, 1)))
        self.assertEqual(tied.cell, (1, 1))
        tied = choose_cell("LCM", ((1, 2), (1, 3)), (2, 4), (4, 2))
        self.assertEqual(tied.candidates, ((0, 0), (1, 0)))
        self.assertEqual(tied.cell, (1, 0))
        same_amount = choose_cell("LCM", ((1, 1), (1, 1)), (2, 2), (2, 2))
        self.assertEqual(same_amount.cell, (0, 0))

    def test_playback_reveals_selection_allocations_and_optimality_in_order(self):
        for method, (_, total, _, _, expected_rc) in EXPECTED.items():
            with self.subTest(method=method):
                states = build_states(method)
                start = int(method == "VAM")
                self.assertEqual(len(states), 35 + start)
                self.assertIn(f"In {method}, we", states[0]["body"])
                if method == "VAM":
                    self.assertIn("more per carton", states[0]["body"])
                    self.assertEqual(states[0]["penalties"], states[1]["penalties"])
                    self.assertIn("Which row or column has the greatest penalty", states[1]["body"])
                    forced_prompt = states[start + 4 * 3]["body"]
                    self.assertIn("down the column from top to bottom", forced_prompt)
                    self.assertIn("across the row from left to right", forced_prompt)
                self.assertEqual(sum(bool(state.get("note")) for state in states), 1 + int(method == "NWCR"))
                for index in range(start, start + 18, 3):
                    question, selection, update = states[index:index + 3]
                    self.assertNotIn("selected", question)
                    self.assertEqual(question["grid"], selection["grid"])
                    i, j = selection["selected"]
                    self.assertGreater(update["grid"][i][j], 0)
                    self.assertTrue(update["title"].startswith("Allocate "))
                _, allocations = initial_solution(method)
                products = " + ".join(f"{COSTS[i][j]} × {allocations[i][j]}" for i, j in basis_cells(allocations))
                optimality = states[start + 18:]
                self.assertIn(products, optimality[0]["body"])
                self.assertIn(f"{total:,}", optimality[0]["body"])
                self.assertFalse(optimality[0]["equations"])
                self.assertEqual(len(optimality[1]["equations"]), 6)
                self.assertTrue(optimality[1]["body"].startswith("In a transportation problem, "))
                self.assertEqual(optimality[1]["u"], [None] * 3)
                for count, state in enumerate(optimality[2:9], 1):
                    self.assertEqual(sum(value is not None for value in state["u"] + state["v"]), count)
                    if count > 1:
                        i, j = state["equation"]
                        self.assertEqual(state["highlighted_duals"], [("u", i), ("v", j)])
                for count, state in enumerate(optimality[10:16], 1):
                    self.assertEqual(sum(value is not None for row in state["rc"] for value in row), count)
                self.assertTrue(optimality[9]["body"].startswith("In a transportation problem, "))
                self.assertEqual(
                    tuple(value for row in states[-1]["rc"] for value in row if value is not None),
                    expected_rc,
                )
                self.assertTrue(states[-2]["note"].startswith("<strong>Note.</strong>"))
                self.assertIn("for the same allocation", states[-2]["note"])
                self.assertIn("Compute the reduced cost", states[-2]["title"])
                self.assertEqual(states[-1]["phase"], "Result")
                self.assertIn("is optimal" if method == "VAM" else "is not optimal", states[-1]["title"])
                if method != "VAM":
                    self.assertIn("The presence of a negative reduced cost", states[-1]["body"])
                    self.assertIn(f"₹{total:,}", states[-1]["body"])

    def test_streamlit_start_and_restart_retain_method(self):
        page = Path(__file__).resolve().parents[1] / "pages" / "transportation_problem_example_1.py"
        app = AppTest.from_file(str(page)).run()
        self.assertFalse(app.exception)
        self.assertEqual(app.radio[0].value, "NWCR")
        app.radio[0].set_value("VAM").run()
        app.button(key="powerco_start").click().run()
        self.assertFalse(app.exception)
        self.assertFalse(app.radio)
        app.button(key="powerco_restart").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.radio[0].value, "VAM")

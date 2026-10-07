"""Focused verification of Simplex Algorithm - Example 1."""

import unittest
from fractions import Fraction
from itertools import combinations
from pathlib import Path

from streamlit.testing.v1 import AppTest

from algorithms.simplex import (
    COLUMNS,
    build_simplex_demonstration,
    is_feasible,
    objective_value,
)
from components.simplex import (
    build_simplex_demonstration_html,
    build_simplex_review_state_html,
)


def row(*values: int | Fraction) -> tuple[Fraction, ...]:
    return tuple(Fraction(value) for value in values)


def intersection(
    first: tuple[int, int, int],
    second: tuple[int, int, int],
) -> tuple[Fraction, Fraction] | None:
    """Solve two boundary equations independently of the simplex code."""

    a1, b1, c1 = first
    a2, b2, c2 = second
    determinant = a1 * b2 - a2 * b1
    if determinant == 0:
        return None
    return (
        Fraction(c1 * b2 - c2 * b1, determinant),
        Fraction(a1 * c2 - a2 * c1, determinant),
    )


class SimplexExampleOneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.demo = build_simplex_demonstration()
        cls.states = {state.state_id: state for state in cls.demo.states}

    def test_initial_tableau_and_starting_bfs_are_exact(self) -> None:
        self.assertEqual(COLUMNS, ("Z", "x1", "x2", "s1", "s2", "s3", "s4", "RHS"))
        self.assertEqual(
            self.demo.initial_tableau.rows,
            (
                row(1, -5, -4, 0, 0, 0, 0, 0),
                row(0, 6, 4, 1, 0, 0, 0, 24),
                row(0, 1, 2, 0, 1, 0, 0, 6),
                row(0, -1, 1, 0, 0, 1, 0, 1),
                row(0, 0, 1, 0, 0, 0, 1, 2),
            ),
        )
        start = self.states["S02"].path[-1]
        self.assertEqual(start.values, row(0, 0, 24, 6, 1, 2))
        self.assertEqual(start.objective, 0)
        self.assertEqual(
            self.states["S04"].highlights.basic_columns,
            ("s1", "s2", "s3", "s4"),
        )

    def test_first_pivot_stages_match_every_row_operation(self) -> None:
        pivot, row_zero, row_two, row_three, row_four = self.demo.first_pivot_stages
        self.assertEqual(pivot.basic_variables, ("Z", "x1", "s2", "s3", "s4"))
        self.assertEqual(pivot.rows[1], row(0, 1, Fraction(2, 3), Fraction(1, 6), 0, 0, 0, 4))
        self.assertEqual(row_zero.rows[0], row(1, 0, Fraction(-2, 3), Fraction(5, 6), 0, 0, 0, 20))
        self.assertEqual(row_two.rows[2], row(0, 0, Fraction(4, 3), Fraction(-1, 6), 1, 0, 0, 2))
        self.assertEqual(row_three.rows[3], row(0, 0, Fraction(5, 3), Fraction(1, 6), 0, 1, 0, 5))
        self.assertEqual(row_four.rows[4], row(0, 0, 1, 0, 0, 0, 1, 2))
        self.assertEqual(
            self.demo.first_tableau.rows,
            (
                row(1, 0, Fraction(-2, 3), Fraction(5, 6), 0, 0, 0, 20),
                row(0, 1, Fraction(2, 3), Fraction(1, 6), 0, 0, 0, 4),
                row(0, 0, Fraction(4, 3), Fraction(-1, 6), 1, 0, 0, 2),
                row(0, 0, Fraction(5, 3), Fraction(1, 6), 0, 1, 0, 5),
                row(0, 0, 1, 0, 0, 0, 1, 2),
            ),
        )

    def test_second_pivot_stages_and_final_tableau_are_exact(self) -> None:
        pivot, row_zero, row_one, row_three, row_four = self.demo.second_pivot_stages
        self.assertEqual(pivot.basic_variables, ("Z", "x1", "x2", "s3", "s4"))
        self.assertEqual(pivot.rows[2], row(0, 0, 1, Fraction(-1, 8), Fraction(3, 4), 0, 0, Fraction(3, 2)))
        self.assertEqual(row_zero.rows[0], row(1, 0, 0, Fraction(3, 4), Fraction(1, 2), 0, 0, 21))
        self.assertEqual(row_one.rows[1], row(0, 1, 0, Fraction(1, 4), Fraction(-1, 2), 0, 0, 3))
        self.assertEqual(row_three.rows[3], row(0, 0, 0, Fraction(3, 8), Fraction(-5, 4), 1, 0, Fraction(5, 2)))
        self.assertEqual(row_four.rows[4], row(0, 0, 0, Fraction(1, 8), Fraction(-3, 4), 0, 1, Fraction(1, 2)))
        self.assertEqual(
            self.demo.final_tableau.rows,
            (
                row(1, 0, 0, Fraction(3, 4), Fraction(1, 2), 0, 0, 21),
                row(0, 1, 0, Fraction(1, 4), Fraction(-1, 2), 0, 0, 3),
                row(0, 0, 1, Fraction(-1, 8), Fraction(3, 4), 0, 0, Fraction(3, 2)),
                row(0, 0, 0, Fraction(3, 8), Fraction(-5, 4), 1, 0, Fraction(5, 2)),
                row(0, 0, 0, Fraction(1, 8), Fraction(-3, 4), 0, 1, Fraction(1, 2)),
            ),
        )

    def test_entering_leaving_ratio_and_pivot_metadata(self) -> None:
        self.assertEqual(self.states["S06"].highlights.entering_column, "x1")
        self.assertEqual(
            self.states["S08"].ratios,
            (("s1", "24 / 6 = 4"), ("s2", "6 / 1 = 6")),
        )
        self.assertEqual(self.states["S09"].highlights.excluded_rows, ("s3", "s4"))
        self.assertIn("positive entries 6 and 1", self.states["S08"].body_html)
        self.assertIn("-1 entry", self.states["S09"].body_html)
        self.assertIn("0 entry", self.states["S09"].body_html)
        self.assertEqual(
            (self.states["S10"].highlights.leaving_row, self.states["S10"].highlights.pivot_column),
            ("s1", "x1"),
        )
        self.assertEqual(self.states["S18"].highlights.entering_column, "x2")
        self.assertEqual(self.states["S19"].highlights.leaving_row, "s2")
        self.assertEqual(self.states["S19"].highlights.pivot_column, "x2")

    def test_teaching_flow_has_27_compact_states_and_six_pause_questions(self) -> None:
        self.assertEqual(tuple(state.state_id for state in self.demo.states), tuple(f"S{i:02d}" for i in range(1, 28)))
        questions = tuple(state.state_id for state in self.demo.states if state.kind == "question")
        self.assertEqual(questions, ("S05", "S07", "S15", "S17", "S23", "S25"))
        for question_id, answer_id in (
            ("S05", "S06"), ("S07", "S08"), ("S15", "S16"),
            ("S17", "S18"), ("S23", "S24"), ("S25", "S26"),
        ):
            self.assertEqual(int(answer_id[1:]), int(question_id[1:]) + 1)
        all_text = " ".join(f"{state.title} {state.body_html}" for state in self.demo.states).lower()
        self.assertNotIn("normalize", all_text)

    def test_questions_are_not_duplicated(self) -> None:
        relocated_questions = {
            "S05": "Why can a negative coefficient in row 0 indicate improvement for a maximization objective?",
            "S07": "Why can x₁ not keep increasing?",
        }
        for state_id in ("S05", "S07", "S15", "S17", "S23", "S25"):
            state = self.states[state_id]
            self.assertNotIn(state.title, state.body_html)
            self.assertEqual(
                state.body_html,
                relocated_questions.get(state_id, "")
                + '<span class="pause">Pause and think before pressing Next.</span>',
            )

    def test_overview_alignment_uses_only_the_requested_headings(self) -> None:
        headings = {
            "S02": "Start from an initial basic feasible solution (BFS)",
            "S05": "We now need to choose an incoming variable (i.e., a nonbasic variable) to enter the basis",
            "S07": "Choose an outgoing basic variable to leave the basis",
            "S16": "Read the neighbouring BFS: Z has improved",
            "S18": "Continue: choose x₂ as the next incoming variable",
            "S24": "Read the neighbouring BFS: Z has improved",
            "S26": "Stop: no neighbouring BFS can improve Z",
        }
        for state_id, title in headings.items():
            self.assertEqual(self.states[state_id].title, title)
        self.assertEqual(self.states["S17"].title, "Have we reached the optimum?")
        self.assertEqual(self.states["S25"].title, "How do we know this solution is optimal?")

    def test_landing_overview_and_view_specific_scrolling(self) -> None:
        page = Path(__file__).resolve().parents[1] / "pages" / "simplex_algorithm.py"
        app = AppTest.from_file(str(page)).run()
        self.assertFalse(app.exception)
        overview = [item.value for item in app.markdown if item.value.startswith("1. **Start")]
        self.assertEqual(len(overview), 1)
        self.assertIn("corner (extreme) point", overview[0])
        self.assertIn("**Move to a neighbouring BFS such that $Z$ improves.**", overview[0])
        self.assertIn("**Continue until no neighbouring BFS can improve $Z$.**", overview[0])
        # The overview belongs to the main reading flow, not an action column.
        main_children = list(app.main.children.values())
        overview_element = next(item for item in app.markdown if item.value == overview[0])
        self.assertIn(overview_element, main_children)
        self.assertIn(app.button(key="simplex_start"), main_children)
        self.assertLess(
            main_children.index(overview_element),
            main_children.index(app.button(key="simplex_start")),
        )
        self.assertIn("overflow: auto;", app.markdown[0].value)
        app.button(key="simplex_start").click().run()
        self.assertFalse(app.exception)
        self.assertIn("overflow: clip;", app.markdown[0].value)
        app.button(key="simplex_restart").click().run()
        self.assertIn("overflow: auto;", app.markdown[0].value)

    def test_first_ratio_explanation_is_split_as_requested(self) -> None:
        positive = self.states["S08"]
        other = self.states["S09"]
        self.assertEqual(positive.title, "How do the positive coefficients restrict x₁?")
        self.assertNotIn("-1 entry", positive.body_html)
        self.assertNotIn("minimum ratio", positive.body_html.lower())
        self.assertIn("From Row 1 we have", positive.body_html)
        self.assertEqual(other.title, "Why are the other entries not used in the ratio test?")
        self.assertIn("From Row 3 we have", other.body_html)
        self.assertIn("Row 0 is excluded from the ratio test", other.body_html)
        self.assertNotIn('class="decision-equation"', other.body_html)

    def test_pivots_keep_reference_tableau_and_reveal_rows_progressively(self) -> None:
        first_ids = ("S11", "S12", "S13", "S14")
        first_reveals = (
            ("x1",), ("x1", "Z"), ("x1", "Z", "s2"),
            ("x1", "Z", "s2", "s3", "s4"),
        )
        for state_id, revealed in zip(first_ids, first_reveals):
            state = self.states[state_id]
            self.assertEqual(state.reference_tableau, self.demo.initial_tableau)
            self.assertEqual(state.revealed_rows, revealed)

        second_ids = ("S20", "S21", "S22")
        second_reveals = (
            ("x2",), ("x2", "Z", "x1"), ("x2", "Z", "x1", "s3", "s4"),
        )
        for state_id, revealed in zip(second_ids, second_reveals):
            state = self.states[state_id]
            self.assertEqual(state.reference_tableau, self.demo.first_tableau)
            self.assertEqual(state.revealed_rows, revealed)

    def test_each_completed_tableau_is_followed_by_solution_reading(self) -> None:
        self.assertEqual(self.states["S15"].title, "How do we read the current solution?")
        self.assertIn("(4, 0, 0, 2, 5, 2)", self.states["S16"].body_html)
        self.assertIn("five equations", self.states["S16"].body_html)
        self.assertEqual(self.states["S23"].title, "How do we read the current solution?")
        self.assertIn("(3, 3/2, 0, 0, 5/2, 1/2)", self.states["S24"].body_html)

    def test_bfs_path_and_full_variable_values_are_exact(self) -> None:
        path = self.demo.states[-1].path
        self.assertEqual(
            tuple((point.x1, point.x2, point.objective) for point in path),
            ((Fraction(0), Fraction(0), Fraction(0)), (Fraction(4), Fraction(0), Fraction(20)), (Fraction(3), Fraction(3, 2), Fraction(21))),
        )
        self.assertEqual(path[0].values, row(0, 0, 24, 6, 1, 2))
        self.assertEqual(path[1].values, row(4, 0, 0, 2, 5, 2))
        self.assertEqual(path[2].values, row(3, Fraction(3, 2), 0, 0, Fraction(5, 2), Fraction(1, 2)))

    def test_final_solution_and_equation_reconstruction(self) -> None:
        optimality = self.states["S26"]
        final = self.states["S27"]
        reconstruction = self.states["S24"]
        self.assertTrue(final.is_final)
        self.assertTrue(final.workspace_hidden)
        self.assertIsNone(final.tableau)
        self.assertEqual(optimality.tableau, self.demo.final_tableau)
        self.assertIn("nonbasic variables are s<sub>1</sub> and s<sub>2</sub>", reconstruction.body_html)
        self.assertIn("Z = 21", optimality.body_html)
        self.assertIn("takeaway-list", final.body_html)
        self.assertIn("Each new tableau represents a new basic feasible solution", final.body_html)

    def test_requested_notation_and_explanations_are_present(self) -> None:
        self.assertIn("s.t.", self.states["S01"].panel_html)
        self.assertIn("auxiliary variable", self.states["S04"].body_html)
        self.assertNotIn("read directly from the RHS", self.states["S04"].body_html)
        self.assertIn("-5 + 5(1) = 0", self.states["S12"].body_html)
        self.assertIn("1 - 1(1) = 0", self.states["S13"].body_html)
        for state_id in ("S20", "S21", "S22"):
            self.assertNotIn("&Prime;", self.states[state_id].body_html)
        self.assertNotIn('class="decision-equation"', self.states["S19"].body_html)

    def test_corner_enumeration_independently_confirms_unique_optimum(self) -> None:
        boundaries = (
            (1, 0, 0), (0, 1, 0),
            (6, 4, 24), (1, 2, 6), (-1, 1, 1), (0, 1, 2),
        )
        vertices = {
            point
            for first, second in combinations(boundaries, 2)
            if (point := intersection(first, second)) is not None and is_feasible(*point)
        }
        expected = {
            (Fraction(0), Fraction(0)), (Fraction(0), Fraction(1)),
            (Fraction(1), Fraction(2)), (Fraction(2), Fraction(2)),
            (Fraction(3), Fraction(3, 2)), (Fraction(4), Fraction(0)),
        }
        self.assertEqual(vertices, expected)
        values = {point: objective_value(*point) for point in vertices}
        self.assertEqual([point for point, value in values.items() if value == max(values.values())], [(Fraction(3), Fraction(3, 2))])

    def test_each_structural_constraint_is_nonredundant(self) -> None:
        constraints = (
            lambda x1, x2: 6 * x1 + 4 * x2 <= 24,
            lambda x1, x2: x1 + 2 * x2 <= 6,
            lambda x1, x2: -x1 + x2 <= 1,
            lambda x1, x2: x2 <= 2,
        )
        witnesses = ((Fraction(5), Fraction(0)), (Fraction(5, 2), Fraction(2)), (Fraction(0), Fraction(2)), (Fraction(4, 3), Fraction(7, 3)))
        for omitted, witness in enumerate(witnesses):
            self.assertGreaterEqual(witness[0], 0)
            self.assertGreaterEqual(witness[1], 0)
            self.assertFalse(constraints[omitted](*witness))
            self.assertTrue(all(rule(*witness) for index, rule in enumerate(constraints) if index != omitted))

    def test_browser_component_contains_all_states_and_local_navigation(self) -> None:
        html = build_simplex_demonstration_html(self.demo)
        self.assertIn('id="previous"', html)
        self.assertIn('id="next"', html)
        self.assertIn("stateIndex+=1;render()", html)
        self.assertIn("stateIndex-=1;render()", html)
        self.assertIn("Current BFS:", html)
        self.assertIn("6x", html)
        self.assertIn('class="constraint c4"', html)
        self.assertIn("Current tableau", html)
        self.assertIn("Next tableau", html)
        self.assertIn("fresh-reveal", html)
        self.assertEqual(html.count('"id":"'), 27)
        self.assertIn("state.id==='S26'?'Key takeaways'", html)
        self.assertIn('"workspaceHidden":true', html)
        self.assertIn("cloudFooterClearance=window.parent.frameElement?.title==='streamlitApp'?56:0", html)
        self.assertIn("frame.getBoundingClientRect().top-12-cloudFooterClearance", html)

    def test_qa_review_renders_all_states_without_navigation(self) -> None:
        pages = [build_simplex_review_state_html(self.demo, index) for index in range(27)]
        self.assertEqual(len(pages), 27)
        for index, (state, html) in enumerate(zip(self.demo.states, pages)):
            self.assertIn('class="app review-mode"', html)
            self.assertIn(f"const displayOffset={index},displayTotal=27;", html)
            self.assertIn(f'"id":"{state.state_id}"', html)
            self.assertNotIn('<button id="previous"', html)
            self.assertNotIn('<button id="next"', html)

    def test_qa_review_rejects_invalid_state_index(self) -> None:
        with self.assertRaises(IndexError):
            build_simplex_review_state_html(self.demo, 27)

    def test_targeted_readability_changes_preserve_the_state_flow(self) -> None:
        html = build_simplex_demonstration_html(self.demo)
        self.assertNotIn("No simplex point selected yet", html)
        self.assertIn("summary.hidden=!path.length", html)
        self.assertIn(".graph-wrap svg text{font-weight:400}", html)
        self.assertIn('markerWidth="5" markerHeight="5"', html)
        self.assertIn("function constraintLabel", html)
        self.assertIn("rotate(${angle})", html)
        self.assertIn(".teaching-body b,.bfs-equation", html)
        self.assertIn('class="ratio-equations"', self.states["S08"].body_html)
        self.assertIn('class="ratio-conclusion"', self.states["S09"].body_html)
        self.assertIn('class="ratio-note"', self.states["S09"].body_html)
        self.assertEqual(len(self.demo.states), 27)


if __name__ == "__main__":
    unittest.main()

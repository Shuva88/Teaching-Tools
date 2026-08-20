"""Focused verification for the rebuilt Clarke-Wright demonstration."""

import unittest

from algorithms.clarke_wright import (
    PPT_CAPACITY,
    PPT_DEMANDS,
    PPT_EXPECTED_ACCEPTED,
    PPT_EXPECTED_FINAL_ROUTES,
    PPT_SAVINGS,
    order_final_routes_for_display,
    route_load,
    run_clarke_wright_from_savings,
)
from components.clarke_wright import (
    build_click_demonstration_html,
    build_route_animation_html,
    build_savings_list_html,
    route_edges,
)


def canonical_route(route: tuple[str, ...]) -> tuple[str, ...]:
    reversed_route = tuple(reversed(route))
    return min(route, reversed_route)


class ClarkeWrightFixedExampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = run_clarke_wright_from_savings(
            PPT_DEMANDS,
            PPT_DEMANDS,
            PPT_SAVINGS,
            PPT_CAPACITY,
        )

    def test_savings_pairs_are_processed_in_the_given_order(self) -> None:
        expected = (
            (188, "1", "2"),
            (181, "22", "23"),
            (175, "13", "23"),
            (173, "2", "4"),
            (164, "13", "22"),
            (161, "1", "4"),
            (152, "1", "3"),
            (148, "21", "23"),
            (146, "4", "7"),
            (145, "21", "22"),
            (144, "13", "21"),
            (129, "5", "6"),
            (127, "3", "6"),
            (123, "7", "8"),
            (111, "13", "20"),
            (105, "5", "8"),
            (99, "19", "22"),
            (94, "19", "21"),
            (93, "3", "9"),
            (90, "5", "10"),
            (87, "6", "9"),
            (73, "15", "16"),
            (62, "18", "19"),
            (55, "11", "18"),
            (51, "14", "15"),
            (45, "11", "12"),
            (43, "17", "18"),
        )
        self.assertEqual(
            tuple((d.saving, d.i, d.j) for d in self.result.decisions),
            expected,
        )

    def test_expected_acceptances_are_computed_from_route_state(self) -> None:
        actual = tuple(decision.accepted for decision in self.result.decisions)
        self.assertEqual(actual, PPT_EXPECTED_ACCEPTED)
        self.assertEqual(sum(actual), 18)
        self.assertEqual(len(actual) - sum(actual), 9)
        for decision in self.result.decisions:
            expected_change = -1 if decision.accepted else 0
            self.assertEqual(
                len(decision.routes_after) - len(decision.routes_before),
                expected_change,
            )

    def test_rejection_reasons_use_the_actual_current_state(self) -> None:
        expected_reasons = {
            5: "same route / would create a cycle",
            6: "same route / would create a cycle",
            8: "Customer 23 is not at a route end",
            11: "same route / would create a cycle",
            13: "combined load 130 exceeds capacity 100",
            16: "combined load 140 exceeds capacity 100",
            17: "Customer 22 is not at a route end",
            19: "combined load 135 exceeds capacity 100",
            23: "combined load 115 exceeds capacity 100",
        }
        self.assertEqual(
            {
                decision.number: decision.rejection_reason
                for decision in self.result.decisions
                if not decision.accepted
            },
            expected_reasons,
        )

    def test_every_intermediate_route_is_capacity_feasible(self) -> None:
        for decision in self.result.decisions:
            for route in decision.routes_after:
                self.assertLessEqual(route_load(route, PPT_DEMANDS), PPT_CAPACITY)

    def test_final_routes_cover_all_customers_once_with_expected_loads(self) -> None:
        expected = {canonical_route(route) for route in PPT_EXPECTED_FINAL_ROUTES}
        actual = {canonical_route(route) for route in self.result.final_routes}
        self.assertEqual(actual, expected)

        routed_customers = [
            customer for route in self.result.final_routes for customer in route
        ]
        self.assertEqual(len(routed_customers), 23)
        self.assertEqual(len(set(routed_customers)), 23)
        self.assertEqual(set(routed_customers), set(PPT_DEMANDS))

        ordered = order_final_routes_for_display(self.result.final_routes)
        self.assertEqual(
            tuple(route_load(route, PPT_DEMANDS) for route in ordered),
            (95, 90, 90, 90, 95),
        )

    def test_svg_contains_transition_states_for_accepted_and_rejected_clicks(self) -> None:
        accepted = self.result.decisions[0]
        accepted_html = build_route_animation_html(
            accepted.routes_before,
            accepted.routes_after,
            PPT_DEMANDS,
            candidate_pair=(accepted.i, accepted.j),
            accepted=True,
        )
        self.assertIn('data-edge="1-2"', accepted_html)
        self.assertIn("entering-edge", accepted_html)
        self.assertIn("candidate-accepted", accepted_html)
        self.assertIn("nodePulseGreen", accepted_html)
        self.assertIn("transition: stroke 600ms", accepted_html)

        rejected = self.result.decisions[4]
        rejected_html = build_route_animation_html(
            rejected.routes_before,
            rejected.routes_after,
            PPT_DEMANDS,
            candidate_pair=(rejected.i, rejected.j),
            accepted=False,
        )
        self.assertEqual(rejected.routes_before, rejected.routes_after)
        self.assertIn("candidate-rejected", rejected_html)
        self.assertIn("nodePulseRed", rejected_html)

    def test_savings_panel_marks_processed_rows_and_auto_scrolls(self) -> None:
        html = build_savings_list_html(self.result.decisions, processed_count=5)
        self.assertEqual(html.count('class="accepted'), 4)
        self.assertEqual(html.count('class="rejected'), 1)
        self.assertIn('id="current-row"', html)
        self.assertIn("scrollIntoView", html)

    def test_final_svg_contains_compact_route_table(self) -> None:
        ordered = order_final_routes_for_display(self.result.final_routes)
        html = build_route_animation_html(
            self.result.decisions[-1].routes_before,
            ordered,
            PPT_DEMANDS,
            candidate_pair=("17", "18"),
            accepted=True,
            final_routes=ordered,
        )
        self.assertIn('class="final-table"', html)
        self.assertIn("0 – 3 – 1 – 2 – 4 – 7 – 8 – 0", html)
        self.assertIn("Load 95", html)

    def test_initial_individual_routes_have_one_depot_edge_each(self) -> None:
        for customer in PPT_DEMANDS:
            self.assertEqual(route_edges((customer,)), {("0", customer)})

    def test_click_component_contains_the_complete_browser_sequence(self) -> None:
        ordered = order_final_routes_for_display(self.result.final_routes)
        html = build_click_demonstration_html(
            self.result.decisions,
            self.result.decisions[0].routes_before,
            ordered,
            PPT_DEMANDS,
            PPT_CAPACITY,
        )

        self.assertEqual(html.count('id="saving-'), 27)
        self.assertIn('id="previous-button"', html)
        self.assertIn('id="next-button"', html)
        self.assertIn("async function nextSavingsPair()", html)
        self.assertIn("async function previousSavingsPair()", html)
        self.assertIn("nextButton.addEventListener('click',nextSavingsPair)", html)
        self.assertNotIn("runAnimation", html)
        self.assertIn("scrollIntoView", html)
        self.assertIn("await sleep(900)", html)
        self.assertIn("await sleep(1200)", html)
        self.assertIn("transition:stroke 1100ms", html)
        self.assertIn('id="edge-1-2"', html)
        self.assertIn("applyEdges(frame.edges)", html)
        self.assertIn("Customer sub-paths are unchanged", html)
        self.assertIn("finalTable.classList.toggle('show'", html)
        self.assertIn("0 – 3 – 1 – 2 – 4 – 7 – 8 – 0", html)

    def test_depot_links_are_hidden_until_a_separate_final_click(self) -> None:
        ordered = order_final_routes_for_display(self.result.final_routes)
        html = build_click_demonstration_html(
            self.result.decisions,
            self.result.decisions[0].routes_before,
            ordered,
            PPT_DEMANDS,
            PPT_CAPACITY,
        )

        frames_javascript = html.split("const frames=", 1)[1].split(
            ";\nconst initialEdges=", 1
        )[0]
        self.assertNotIn('"0-', frames_javascript)
        self.assertIn("const initialEdges={};", html)
        self.assertIn('"0-3"', html)
        self.assertIn("<th>S. No.</th>", html)
        self.assertNotIn("<th>Step</th>", html)
        self.assertIn("Direct depot links are hidden", html)
        self.assertIn("Connect Routes to Depot", html)
        self.assertIn("async function connectRoutesToDepot()", html)
        self.assertIn("applyEdges(finalEdges)", html)
        self.assertIn("if(depotConnected)", html)

    def test_click_component_places_demand_inside_enlarged_nodes(self) -> None:
        ordered = order_final_routes_for_display(self.result.final_routes)
        html = build_click_demonstration_html(
            self.result.decisions,
            self.result.decisions[0].routes_before,
            ordered,
            PPT_DEMANDS,
            PPT_CAPACITY,
        )

        self.assertEqual(html.count('<circle r="25"/>'), 23)
        self.assertIn('class="demand-label" x="0" y="12"', html)
        self.assertIn('(20)</text>', html)
        self.assertNotIn('d=20', html)

    def test_click_component_uses_compact_wide_classroom_geometry(self) -> None:
        ordered = order_final_routes_for_display(self.result.final_routes)
        html = build_click_demonstration_html(
            self.result.decisions,
            self.result.decisions[0].routes_before,
            ordered,
            PPT_DEMANDS,
            PPT_CAPACITY,
        )

        self.assertIn(".app { height:557px", html)
        self.assertIn(".savings-panel { display:flex", html)
        self.assertIn('viewBox="0 25 1000 525"', html)
        self.assertIn('transform="translate(77.6 62.0)"', html)
        self.assertIn('transform="translate(922.4 74.4)"', html)
        self.assertNotIn(".final-table { position:absolute", html)


if __name__ == "__main__":
    unittest.main()

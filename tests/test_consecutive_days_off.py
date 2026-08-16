"""Focused tests for the fixed restaurant-delivery scheduling example."""

import unittest

from algorithms.consecutive_days_off import (
    DAYS,
    RESTAURANT_REQUIREMENTS,
    build_employee_schedule,
    calculate_daily_staffing,
    calculate_excess_staffing,
    generate_consecutive_days_off_steps,
)


class ConsecutiveDaysOffFixedExampleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.steps = generate_consecutive_days_off_steps(RESTAURANT_REQUIREMENTS)
        self.schedule = build_employee_schedule(self.steps)

    def test_verified_pair_sequence_and_requirement_updates(self) -> None:
        self.assertEqual(
            [step.selected_pair.days for step in self.steps],
            [
                ("Sat", "Sun"),
                ("Tue", "Wed"),
                ("Sat", "Sun"),
                ("Mon", "Tue"),
                ("Wed", "Thu"),
                ("Sat", "Sun"),
                ("Mon", "Tue"),
                ("Tue", "Wed"),
            ],
        )
        self.assertEqual(
            [step.after for step in self.steps],
            [
                (5, 2, 4, 3, 7, 4, 4),
                (4, 2, 4, 2, 6, 3, 3),
                (3, 1, 3, 1, 5, 3, 3),
                (3, 1, 2, 0, 4, 2, 2),
                (2, 0, 2, 0, 3, 1, 1),
                (1, 0, 1, 0, 2, 1, 1),
                (1, 0, 0, 0, 1, 0, 0),
                (0, 0, 0, 0, 0, 0, 0),
            ],
        )

    def test_threshold_includes_equal_values_and_pair_totals(self) -> None:
        partner_2 = self.steps[1]
        self.assertEqual(partner_2.threshold, 4)
        self.assertEqual(
            partner_2.included_days,
            ("Tue", "Wed", "Thu", "Sat", "Sun"),
        )
        self.assertEqual(
            [(pair.days, pair.total) for pair in partner_2.eligible_pairs],
            [
                (("Tue", "Wed"), 6),
                (("Wed", "Thu"), 7),
                (("Sat", "Sun"), 8),
            ],
        )

    def test_scheduler_assumption_is_recorded_for_pair_total_ties(self) -> None:
        tied_employee_numbers = [
            step.employee_number
            for step in self.steps
            if step.scheduler_tie_assumption
        ]
        self.assertEqual(tied_employee_numbers, [4, 7, 8])
        self.assertEqual(
            [pair.days for pair in self.steps[3].best_pairs],
            [("Mon", "Tue"), ("Tue", "Wed"), ("Wed", "Thu")],
        )

    def test_final_schedule_staffing_and_minimum_employee_count(self) -> None:
        scheduled = calculate_daily_staffing(self.schedule)
        excess = calculate_excess_staffing(RESTAURANT_REQUIREMENTS, scheduled)

        self.assertEqual(len(self.schedule), 8)
        self.assertEqual(scheduled, (6, 4, 5, 7, 8, 5, 5))
        self.assertEqual(excess, (0, 1, 0, 3, 0, 1, 1))
        self.assertEqual(max(RESTAURANT_REQUIREMENTS), 8)

        first_assignment = self.schedule[0]
        self.assertEqual(first_assignment.days_off, ("Sat", "Sun"))
        self.assertEqual(
            first_assignment.working_days,
            ("Mon", "Tue", "Wed", "Thu", "Fri"),
        )
        self.assertEqual(DAYS, ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"))


if __name__ == "__main__":
    unittest.main()

"""Focused verification for the fixed six-job classroom example."""

import unittest

from algorithms.johnson import (
    ORIGINAL_SEQUENCE,
    PRINT_SHOP_JOBS,
    Candidate,
    build_two_resource_schedule,
    calculate_metrics,
    generate_johnson_steps,
)


class JohnsonRuleFixedExampleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.steps = generate_johnson_steps(PRINT_SHOP_JOBS)
        self.johnson_sequence = tuple(
            job for job in self.steps[-1].partial_sequence if job is not None
        )

    def test_six_expected_decisions_and_final_sequence(self) -> None:
        decisions = [
            (
                step.selected_job,
                step.selected_resource,
                step.placement,
                step.position,
            )
            for step in self.steps
        ]
        self.assertEqual(
            decisions,
            [
                ("B", 2, "latest", 5),
                ("E", 1, "earliest", 0),
                ("A", 1, "earliest", 1),
                ("C", 2, "latest", 4),
                ("F", 1, "earliest", 2),
                ("D", 1, "earliest", 3),
            ],
        )
        self.assertEqual(self.johnson_sequence, ("E", "A", "F", "D", "C", "B"))

    def test_a_c_tie_is_recorded_and_a_is_selected(self) -> None:
        tie_step = self.steps[2]
        self.assertEqual(tie_step.minimum_time, 4)
        self.assertEqual(
            tie_step.tied_candidates,
            (Candidate("A", 1, 4), Candidate("C", 2, 4)),
        )
        self.assertEqual(tie_step.selected_job, "A")

    def test_johnson_schedule_times_and_metrics(self) -> None:
        schedule = build_two_resource_schedule(self.johnson_sequence, PRINT_SHOP_JOBS)
        operation_times = [
            (op.job, op.resource, op.start, op.finish) for op in schedule.operations
        ]
        self.assertEqual(
            operation_times,
            [
                ("E", 1, 0, 3),
                ("E", 2, 3, 10),
                ("A", 1, 3, 7),
                ("A", 2, 10, 18),
                ("F", 1, 7, 12),
                ("F", 2, 18, 24),
                ("D", 1, 12, 18),
                ("D", 2, 24, 34),
                ("C", 1, 18, 27),
                ("C", 2, 34, 38),
                ("B", 1, 27, 34),
                ("B", 2, 38, 40),
            ],
        )

        metrics = calculate_metrics(schedule, PRINT_SHOP_JOBS)
        self.assertEqual(metrics.makespan, 40)
        self.assertEqual(metrics.resource_1_idle, 6)
        self.assertEqual(metrics.resource_2_idle, 3)
        self.assertAlmostEqual(metrics.resource_1_utilization, 0.85)
        self.assertAlmostEqual(metrics.resource_2_utilization, 0.925)
        self.assertAlmostEqual(metrics.average_flow_time, 27.3333333333)

    def test_original_sequence_metrics(self) -> None:
        schedule = build_two_resource_schedule(ORIGINAL_SEQUENCE, PRINT_SHOP_JOBS)
        metrics = calculate_metrics(schedule, PRINT_SHOP_JOBS)

        self.assertEqual(metrics.makespan, 49)
        self.assertEqual(metrics.resource_1_idle, 15)
        self.assertEqual(metrics.resource_2_idle, 12)
        self.assertAlmostEqual(metrics.resource_1_utilization, 34 / 49)
        self.assertAlmostEqual(metrics.resource_2_utilization, 37 / 49)
        self.assertAlmostEqual(metrics.average_flow_time, 29.6666666667)


if __name__ == "__main__":
    unittest.main()

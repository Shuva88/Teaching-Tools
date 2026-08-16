"""Focused tests for the fixed precision-fabrication sequencing example."""

import unittest

from algorithms.single_processor import (
    FABRICATION_JOBS,
    build_single_processor_schedule,
    calculate_sequencing_metrics,
    sequence_edd,
    sequence_fcfs,
    sequence_spt,
)


class SingleProcessorFixedExampleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sequences = {
            "FCFS": sequence_fcfs(FABRICATION_JOBS),
            "SPT": sequence_spt(FABRICATION_JOBS),
            "EDD": sequence_edd(FABRICATION_JOBS),
        }
        self.schedules = {
            rule: build_single_processor_schedule(rule, sequence, FABRICATION_JOBS)
            for rule, sequence in self.sequences.items()
        }
        self.metrics = {
            rule: calculate_sequencing_metrics(schedule)
            for rule, schedule in self.schedules.items()
        }

    def test_expected_sequences(self) -> None:
        self.assertEqual(self.sequences["FCFS"], ("A", "B", "C", "D", "E", "F"))
        self.assertEqual(self.sequences["SPT"], ("C", "A", "D", "F", "B", "E"))
        self.assertEqual(self.sequences["EDD"], ("C", "B", "E", "A", "D", "F"))

    def test_fcfs_order_level_calculations(self) -> None:
        rows = [
            (
                operation.job,
                operation.start,
                operation.processing_time,
                operation.due_time,
                operation.flow_time,
                operation.lateness,
                operation.tardiness,
            )
            for operation in self.schedules["FCFS"].operations
        ]
        self.assertEqual(
            rows,
            [
                ("A", 0, 3, 21, 3, -18, 0),
                ("B", 3, 7, 16, 10, -6, 0),
                ("C", 10, 2, 8, 12, 4, 4),
                ("D", 12, 5, 28, 17, -11, 0),
                ("E", 17, 8, 18, 25, 7, 7),
                ("F", 25, 6, 29, 31, 2, 2),
            ],
        )

    def test_spt_and_edd_order_level_calculations(self) -> None:
        self.assertEqual(
            [(operation.start, operation.flow_time) for operation in self.schedules["SPT"].operations],
            [(0, 2), (2, 5), (5, 10), (10, 16), (16, 23), (23, 31)],
        )
        self.assertEqual(
            [(operation.lateness, operation.tardiness) for operation in self.schedules["EDD"].operations],
            [(-6, 0), (-7, 0), (-1, 0), (-1, 0), (-3, 0), (2, 2)],
        )

    def test_verified_metrics_and_constant_processing_total(self) -> None:
        expected = {
            "FCFS": (16.33, -3.67, 2.17, 3, 7),
            "SPT": (14.50, -5.50, 3.33, 2, 13),
            "EDD": (17.33, -2.67, 0.33, 1, 2),
        }
        for rule, values in expected.items():
            metrics = self.metrics[rule]
            self.assertAlmostEqual(metrics.average_flow_time, values[0], places=2)
            self.assertAlmostEqual(metrics.average_lateness, values[1], places=2)
            self.assertAlmostEqual(metrics.average_tardiness, values[2], places=2)
            self.assertEqual(metrics.tardy_jobs, values[3])
            self.assertEqual(metrics.maximum_tardiness, values[4])
            self.assertEqual(self.schedules[rule].total_processing_time, 31)


if __name__ == "__main__":
    unittest.main()

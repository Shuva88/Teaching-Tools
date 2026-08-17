"""Pure sequencing logic for a fixed single-processor classroom example."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SequencingJob:
    """One order waiting for the single processor at time zero."""

    name: str
    processing_time: int
    due_time: int
    arrival_order: int


@dataclass(frozen=True)
class SequencedOperation:
    """Calculated timing and due-date performance for one scheduled order."""

    job: str
    start: int
    processing_time: int
    due_time: int
    flow_time: int
    lateness: int
    tardiness: int


@dataclass(frozen=True)
class SingleProcessorSchedule:
    """A complete sequence and its calculated order-level schedule."""

    rule: str
    sequence: tuple[str, ...]
    operations: tuple[SequencedOperation, ...]
    total_processing_time: int


@dataclass(frozen=True)
class SequencingMetrics:
    """Aggregate performance measures for a single sequence."""

    average_flow_time: float
    average_lateness: float
    average_tardiness: float
    tardy_jobs: int
    maximum_tardiness: int


@dataclass(frozen=True)
class CriticalRatioCandidate:
    """A recomputed critical ratio for one order at a decision time."""

    job: str
    current_time: int
    due_time: int
    processing_time: int
    critical_ratio: float


@dataclass(frozen=True)
class CriticalRatioDecision:
    """All candidate ratios and the selected order at one CR decision."""

    number: int
    current_time: int
    candidates: tuple[CriticalRatioCandidate, ...]
    selected_job: str


FABRICATION_JOBS: tuple[SequencingJob, ...] = (
    SequencingJob("A", processing_time=3, due_time=21, arrival_order=1),
    SequencingJob("B", processing_time=7, due_time=16, arrival_order=2),
    SequencingJob("C", processing_time=2, due_time=8, arrival_order=3),
    SequencingJob("D", processing_time=5, due_time=28, arrival_order=4),
    SequencingJob("E", processing_time=8, due_time=18, arrival_order=5),
    SequencingJob("F", processing_time=6, due_time=29, arrival_order=6),
)


def sequence_fcfs(jobs: tuple[SequencingJob, ...]) -> tuple[str, ...]:
    """Return jobs in first-come, first-served order."""

    return tuple(job.name for job in sorted(jobs, key=lambda job: job.arrival_order))


def sequence_spt(jobs: tuple[SequencingJob, ...]) -> tuple[str, ...]:
    """Return jobs from shortest to longest processing time."""

    return tuple(
        job.name
        for job in sorted(
            jobs,
            key=lambda job: (job.processing_time, job.arrival_order),
        )
    )


def sequence_edd(jobs: tuple[SequencingJob, ...]) -> tuple[str, ...]:
    """Return jobs from earliest to latest due time."""

    return tuple(
        job.name
        for job in sorted(
            jobs,
            key=lambda job: (job.due_time, job.arrival_order),
        )
    )


def sequence_lpt(jobs: tuple[SequencingJob, ...]) -> tuple[str, ...]:
    """Return jobs from longest to shortest processing time."""

    return tuple(
        job.name
        for job in sorted(
            jobs,
            key=lambda job: (-job.processing_time, job.arrival_order),
        )
    )


def generate_critical_ratio_decisions(
    jobs: tuple[SequencingJob, ...],
) -> tuple[CriticalRatioDecision, ...]:
    """Recompute remaining-job critical ratios after every selected order."""

    remaining = list(sorted(jobs, key=lambda job: job.arrival_order))
    decisions: list[CriticalRatioDecision] = []
    current_time = 0

    while remaining:
        candidates = tuple(
            CriticalRatioCandidate(
                job=job.name,
                current_time=current_time,
                due_time=job.due_time,
                processing_time=job.processing_time,
                critical_ratio=(job.due_time - current_time) / job.processing_time,
            )
            for job in remaining
        )
        selected = min(
            candidates,
            key=lambda candidate: (
                candidate.critical_ratio,
                next(
                    job.arrival_order
                    for job in remaining
                    if job.name == candidate.job
                ),
            ),
        )
        selected_job = next(job for job in remaining if job.name == selected.job)
        decisions.append(
            CriticalRatioDecision(
                number=len(decisions) + 1,
                current_time=current_time,
                candidates=candidates,
                selected_job=selected.job,
            )
        )
        current_time += selected_job.processing_time
        remaining.remove(selected_job)

    return tuple(decisions)


def sequence_cr(jobs: tuple[SequencingJob, ...]) -> tuple[str, ...]:
    """Return the dynamic smallest-critical-ratio sequence."""

    return tuple(
        decision.selected_job
        for decision in generate_critical_ratio_decisions(jobs)
    )


def build_single_processor_schedule(
    rule: str,
    sequence: tuple[str, ...],
    jobs: tuple[SequencingJob, ...],
) -> SingleProcessorSchedule:
    """Construct start, flow, lateness, and tardiness values for a sequence."""

    job_by_name = {job.name: job for job in jobs}
    operations: list[SequencedOperation] = []
    current_time = 0

    for job_name in sequence:
        job = job_by_name[job_name]
        start = current_time
        flow_time = start + job.processing_time
        lateness = flow_time - job.due_time
        tardiness = max(0, lateness)
        operations.append(
            SequencedOperation(
                job=job.name,
                start=start,
                processing_time=job.processing_time,
                due_time=job.due_time,
                flow_time=flow_time,
                lateness=lateness,
                tardiness=tardiness,
            )
        )
        current_time = flow_time

    return SingleProcessorSchedule(
        rule=rule,
        sequence=sequence,
        operations=tuple(operations),
        total_processing_time=current_time,
    )


def calculate_sequencing_metrics(
    schedule: SingleProcessorSchedule,
) -> SequencingMetrics:
    """Calculate the five aggregate measures used in the demonstration."""

    job_count = len(schedule.operations)
    flow_times = [operation.flow_time for operation in schedule.operations]
    lateness_values = [operation.lateness for operation in schedule.operations]
    tardiness_values = [operation.tardiness for operation in schedule.operations]

    return SequencingMetrics(
        average_flow_time=sum(flow_times) / job_count,
        average_lateness=sum(lateness_values) / job_count,
        average_tardiness=sum(tardiness_values) / job_count,
        tardy_jobs=sum(value > 0 for value in tardiness_values),
        maximum_tardiness=max(tardiness_values),
    )

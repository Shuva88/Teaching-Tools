"""Pure Johnson's Rule logic for a two-resource flow shop."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean


@dataclass(frozen=True)
class Job:
    """A job and its processing time on each resource."""

    name: str
    resource_1: int
    resource_2: int


@dataclass(frozen=True)
class Candidate:
    """A processing-time cell tied for the current minimum."""

    job: str
    resource: int
    time: int


@dataclass(frozen=True)
class DecisionStep:
    """One programmatically generated Johnson's Rule decision."""

    number: int
    minimum_time: int
    tied_candidates: tuple[Candidate, ...]
    selected_job: str
    selected_resource: int
    placement: str
    position: int
    partial_sequence: tuple[str | None, ...]


@dataclass(frozen=True)
class Operation:
    """One scheduled job operation on one resource."""

    job: str
    resource: int
    start: int
    finish: int

    @property
    def duration(self) -> int:
        return self.finish - self.start


@dataclass(frozen=True)
class Schedule:
    """A complete two-resource schedule."""

    sequence: tuple[str, ...]
    operations: tuple[Operation, ...]


@dataclass(frozen=True)
class Metrics:
    """Performance measures derived from a complete schedule."""

    makespan: int
    resource_1_idle: int
    resource_2_idle: int
    resource_1_utilization: float
    resource_2_utilization: float
    average_flow_time: float


PRINT_SHOP_JOBS: tuple[Job, ...] = (
    Job("A", 4, 8),
    Job("B", 7, 2),
    Job("C", 9, 4),
    Job("D", 6, 10),
    Job("E", 3, 7),
    Job("F", 5, 6),
)

ORIGINAL_SEQUENCE: tuple[str, ...] = tuple(job.name for job in PRINT_SHOP_JOBS)


def generate_johnson_steps(jobs: tuple[Job, ...]) -> tuple[DecisionStep, ...]:
    """Generate Johnson decisions using input order as the deterministic tie-breaker."""

    remaining = list(jobs)
    sequence: list[str | None] = [None] * len(jobs)
    earliest_position = 0
    latest_position = len(jobs) - 1
    steps: list[DecisionStep] = []

    while remaining:
        minimum_time = min(
            min(job.resource_1, job.resource_2) for job in remaining
        )
        tied_candidates: list[Candidate] = []
        for job in remaining:
            if job.resource_1 == minimum_time:
                tied_candidates.append(Candidate(job.name, 1, minimum_time))
            if job.resource_2 == minimum_time:
                tied_candidates.append(Candidate(job.name, 2, minimum_time))

        selected = tied_candidates[0]
        if selected.resource == 1:
            position = earliest_position
            earliest_position += 1
            placement = "earliest"
        else:
            position = latest_position
            latest_position -= 1
            placement = "latest"

        sequence[position] = selected.job
        remaining = [job for job in remaining if job.name != selected.job]
        steps.append(
            DecisionStep(
                number=len(steps) + 1,
                minimum_time=minimum_time,
                tied_candidates=tuple(tied_candidates),
                selected_job=selected.job,
                selected_resource=selected.resource,
                placement=placement,
                position=position,
                partial_sequence=tuple(sequence),
            )
        )

    return tuple(steps)


def build_two_resource_schedule(
    sequence: tuple[str, ...], jobs: tuple[Job, ...]
) -> Schedule:
    """Schedule a sequence through Resource 1 followed by Resource 2."""

    job_by_name = {job.name: job for job in jobs}
    resource_1_available = 0
    resource_2_available = 0
    operations: list[Operation] = []

    for job_name in sequence:
        job = job_by_name[job_name]

        resource_1_start = resource_1_available
        resource_1_finish = resource_1_start + job.resource_1
        resource_1_available = resource_1_finish

        resource_2_start = max(resource_1_finish, resource_2_available)
        resource_2_finish = resource_2_start + job.resource_2
        resource_2_available = resource_2_finish

        operations.extend(
            (
                Operation(job_name, 1, resource_1_start, resource_1_finish),
                Operation(job_name, 2, resource_2_start, resource_2_finish),
            )
        )

    return Schedule(sequence=sequence, operations=tuple(operations))


def calculate_metrics(schedule: Schedule, jobs: tuple[Job, ...]) -> Metrics:
    """Calculate classroom measures over the interval from zero to makespan."""

    job_by_name = {job.name: job for job in jobs}
    resource_2_finishes = [
        operation.finish
        for operation in schedule.operations
        if operation.resource == 2
    ]
    makespan = max(resource_2_finishes)
    resource_1_busy = sum(job_by_name[name].resource_1 for name in schedule.sequence)
    resource_2_busy = sum(job_by_name[name].resource_2 for name in schedule.sequence)

    return Metrics(
        makespan=makespan,
        resource_1_idle=makespan - resource_1_busy,
        resource_2_idle=makespan - resource_2_busy,
        resource_1_utilization=resource_1_busy / makespan,
        resource_2_utilization=resource_2_busy / makespan,
        average_flow_time=mean(resource_2_finishes),
    )

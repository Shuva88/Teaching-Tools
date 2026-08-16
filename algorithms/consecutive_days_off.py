"""Pure logic for scheduling employees with two consecutive days off."""

from __future__ import annotations

from dataclasses import dataclass


DAYS: tuple[str, ...] = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
CONSECUTIVE_PAIR_INDICES: tuple[tuple[int, int], ...] = tuple(
    (index, index + 1) for index in range(len(DAYS) - 1)
)
RESTAURANT_REQUIREMENTS: tuple[int, ...] = (6, 3, 5, 4, 8, 4, 4)


@dataclass(frozen=True)
class PairOption:
    """An eligible consecutive days-off pair and its remaining-requirement total."""

    day_indices: tuple[int, int]
    days: tuple[str, str]
    total: int


@dataclass(frozen=True)
class DaysOffStep:
    """One programmatically generated employee assignment."""

    employee_number: int
    before: tuple[int, ...]
    threshold: int
    included_days: tuple[str, ...]
    eligible_pairs: tuple[PairOption, ...]
    best_pairs: tuple[PairOption, ...]
    selected_pair: PairOption
    scheduler_tie_assumption: bool
    working_days: tuple[str, ...]
    after: tuple[int, ...]


@dataclass(frozen=True)
class EmployeeAssignment:
    """The final work/off pattern for one employee."""

    employee_number: int
    working_days: tuple[str, ...]
    days_off: tuple[str, str]


def generate_consecutive_days_off_steps(
    requirements: tuple[int, ...],
) -> tuple[DaysOffStep, ...]:
    """Apply the textbook procedure until every remaining requirement is zero."""

    remaining = list(requirements)
    steps: list[DaysOffStep] = []

    while any(value > 0 for value in remaining):
        included_indices: set[int] = set()
        eligible_pair_indices: list[tuple[int, int]] = []
        threshold = 0

        for threshold in sorted(set(remaining)):
            included_indices = {
                index for index, value in enumerate(remaining) if value <= threshold
            }
            eligible_pair_indices = [
                pair
                for pair in CONSECUTIVE_PAIR_INDICES
                if pair[0] in included_indices and pair[1] in included_indices
            ]
            if eligible_pair_indices:
                break

        eligible_pairs = tuple(
            PairOption(
                day_indices=pair,
                days=(DAYS[pair[0]], DAYS[pair[1]]),
                total=remaining[pair[0]] + remaining[pair[1]],
            )
            for pair in eligible_pair_indices
        )
        lowest_pair_total = min(pair.total for pair in eligible_pairs)
        best_pairs = tuple(
            pair for pair in eligible_pairs if pair.total == lowest_pair_total
        )
        selected_pair = best_pairs[0]
        off_indices = set(selected_pair.day_indices)
        working_days = tuple(
            day for index, day in enumerate(DAYS) if index not in off_indices
        )
        updated = tuple(
            value
            if index in off_indices
            else max(0, value - 1)
            for index, value in enumerate(remaining)
        )

        steps.append(
            DaysOffStep(
                employee_number=len(steps) + 1,
                before=tuple(remaining),
                threshold=threshold,
                included_days=tuple(
                    day for index, day in enumerate(DAYS) if index in included_indices
                ),
                eligible_pairs=eligible_pairs,
                best_pairs=best_pairs,
                selected_pair=selected_pair,
                scheduler_tie_assumption=len(best_pairs) > 1,
                working_days=working_days,
                after=updated,
            )
        )
        remaining = list(updated)

    return tuple(steps)


def build_employee_schedule(
    steps: tuple[DaysOffStep, ...],
) -> tuple[EmployeeAssignment, ...]:
    """Build the employee work/off schedule from generated assignment steps."""

    return tuple(
        EmployeeAssignment(
            employee_number=step.employee_number,
            working_days=step.working_days,
            days_off=step.selected_pair.days,
        )
        for step in steps
    )


def calculate_daily_staffing(
    schedule: tuple[EmployeeAssignment, ...],
) -> tuple[int, ...]:
    """Count scheduled employees for each day of the displayed planning week."""

    return tuple(
        sum(day in assignment.working_days for assignment in schedule)
        for day in DAYS
    )


def calculate_excess_staffing(
    required: tuple[int, ...], scheduled: tuple[int, ...]
) -> tuple[int, ...]:
    """Return scheduled staffing above the stated daily minimums."""

    return tuple(
        scheduled_value - required_value
        for required_value, scheduled_value in zip(required, scheduled)
    )

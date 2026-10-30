"""Pet care models and scheduling logic, independent of the Streamlit UI.

Data and completion history are kept in memory. Schedule entries contain
(pet, task, start_datetime, end_datetime). Python 3.10 or newer is required.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from typing import Literal


Priority = Literal["low", "medium", "high"]
Frequency = Literal["daily", "weekly", "once"]
PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def _require_text(value: str, label: str) -> None:
    """Reject missing or blank text values."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be non-empty text.")


def _require_minutes(value: int, label: str, minimum: int) -> None:
    """Require whole minutes at or above the specified minimum."""
    if type(value) is not int or value < minimum:
        raise ValueError(f"{label} must be a whole number of at least {minimum}.")


@dataclass(eq=False)
class Task:
    """A care activity with a duration, recurrence rule, and completion history."""

    title: str
    duration_minutes: int
    priority: Priority
    description: str = ""
    frequency: Frequency = "daily"
    weekday: int | None = None
    due_date: date | None = None
    fixed_start_time: time | None = None
    completed_dates: set[date] = field(default_factory=set, init=False, repr=False)

    def __post_init__(self) -> None:
        """Validate task details and set a default date for one-time tasks."""
        if self.fixed_start_time is not None and (not isinstance(self.fixed_start_time, time) or self.fixed_start_time.tzinfo is not None):
            raise ValueError("Fixed start time must be a local clock time.")
        self._validate_details(self.title, self.duration_minutes, self.priority)
        if not isinstance(self.description, str):
            raise ValueError("Description must be text.")
        if self.frequency not in ("daily", "weekly", "once"):
            raise ValueError("Frequency must be daily, weekly, or once.")
        if self.frequency == "weekly":
            if type(self.weekday) is not int or not 0 <= self.weekday <= 6:
                raise ValueError("Weekly tasks need a weekday: Monday=0 through Sunday=6.")
        elif self.weekday is not None:
            raise ValueError("Only weekly tasks use a weekday.")
        if self.frequency == "once":
            if self.due_date is None:
                self.due_date = date.today()
            if type(self.due_date) is not date:
                raise ValueError("A one-time task needs a date, not a datetime.")
        elif self.due_date is not None:
            raise ValueError("Only one-time tasks use a due date.")

    @staticmethod
    def _validate_details(title: str, duration_minutes: int, priority: Priority) -> None:
        """Validate editable fields before changing any task data."""
        _require_text(title, "Task title")
        _require_minutes(duration_minutes, "Duration", 1)
        if priority not in PRIORITY_ORDER:
            raise ValueError("Priority must be low, medium, or high.")

    def update_details(self, title: str, duration_minutes: int, priority: Priority) -> None:
        """Update the title, duration, and priority after validating all three."""
        self._validate_details(title, duration_minutes, priority)
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority

    @property
    def completed(self) -> bool:
        """Report today's completion status, or permanent completion for one-time tasks."""
        return self.is_completed(date.today())

    def is_completed(self, on_date: date) -> bool:
        """Check completion for a particular date without resetting recurring tasks."""
        if self.frequency == "once":
            return bool(self.completed_dates)
        return on_date in self.completed_dates

    def is_due(self, on_date: date) -> bool:
        """Report whether this task is due and unfinished on the given date."""
        if self.is_completed(on_date):
            return False
        if self.frequency == "weekly":
            return on_date.weekday() == self.weekday
        if self.frequency == "once":
            return self.due_date is not None and on_date >= self.due_date
        return True

    def mark_complete(self, on_date: date | None = None) -> None:
        """Complete a due occurrence, defaulting to today; repeated calls are harmless."""
        completion_date = date.today() if on_date is None else on_date
        if type(completion_date) is not date:
            raise ValueError("Completion date must be a date, not a datetime.")
        if self.is_completed(completion_date):
            return
        if not self.is_due(completion_date):
            raise ValueError("This task is not due on the completion date.")
        self.completed_dates.add(completion_date)


@dataclass(eq=False)
class Pet:
    """A pet and its independent collection of care tasks."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate pet details and take a separate copy of any supplied task list."""
        _require_text(self.name, "Pet name")
        _require_text(self.species, "Species")
        initial_tasks = list(self.tasks)
        self.tasks = []
        for task in initial_tasks:
            self.add_task(task)

    def add_task(self, task: Task) -> None:
        """Add a task instance once while allowing separate tasks with matching details."""
        if not isinstance(task, Task):
            raise TypeError("A pet's care task must be a Task.")
        if task not in self.tasks:
            self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove the specific task instance, raising ValueError if it is absent."""
        self.tasks.remove(task)


class Owner:
    """Owner details, pets, and the available time window for a daily plan."""

    def __init__(
        self,
        name: str,
        available_minutes: int,
        start_time: datetime,
        preferences: list[str] | None = None,
        pets: list[Pet] | None = None,
    ) -> None:
        """Create an owner with a start datetime and a nonnegative minute budget."""
        _require_text(name, "Owner name")
        _require_minutes(available_minutes, "Available minutes", 0)
        if not isinstance(start_time, datetime):
            raise ValueError("Start time must include a date and clock time.")
        self.name = name
        self.available_minutes = available_minutes
        self.start_time = start_time
        self.preferences: list[str] = []
        self.pets: list[Pet] = []
        self.update_preferences(preferences if preferences is not None else [])
        for pet in pets if pets is not None else []:
            self.add_pet(pet)

    def add_pet(self, pet: Pet) -> None:
        """Associate a pet instance with this owner without adding it twice."""
        if not isinstance(pet, Pet):
            raise TypeError("An owner's pet must be a Pet.")
        if pet not in self.pets:
            self.pets.append(pet)

    def update_preferences(self, preferences: list[str]) -> None:
        """Set preferred task titles used to break equal-priority ties."""
        if not isinstance(preferences, list):
            raise ValueError("Preferences must be a list of task titles.")
        for title in preferences:
            _require_text(title, "Preferred task title")
        self.preferences = list(preferences)

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Collect tasks across pets, retaining each pet and rejecting shared instances."""
        tasks: list[tuple[Pet, Task]] = []
        seen: set[int] = set()
        for pet in self.pets:
            for task in pet.tasks:
                if id(task) in seen:
                    raise ValueError("Create a separate Task instance for each pet.")
                seen.add(id(task))
                tasks.append((pet, task))
        return tasks


class Scheduler:
    """Choose due tasks across pets and assign consecutive clock times."""

    def __init__(self, owner: Owner) -> None:
        """Create an empty planner for the supplied owner."""
        if not isinstance(owner, Owner):
            raise TypeError("The scheduler needs an Owner.")
        self.owner = owner
        self.schedule: list[tuple[Pet, Task, datetime, datetime]] = []
        self.explanation: str = ""

    def sort_by_time(self, tasks=None) -> list[tuple[Pet, Task]]:
        """Return pet/task pairs ordered by fixed time, with flexible tasks last."""
        pairs = self.owner.get_all_tasks() if tasks is None else list(tasks)
        return sorted(pairs, key=lambda pair: (
            pair[1].fixed_start_time is None,
            pair[1].fixed_start_time or time.min,
        ))

    def filter_tasks(self, pet_name=None, completed=None, on_date=None) -> list[tuple[Pet, Task]]:
        """Filter by pet name and/or completion status on the planning date."""
        day = self.owner.start_time.date() if on_date is None else on_date
        pairs = self.owner.get_all_tasks()
        if pet_name is not None:
            pairs = [(pet, task) for pet, task in pairs
                     if pet.name.casefold() == pet_name.strip().casefold()]
        if completed is not None:
            pairs = [(pet, task) for pet, task in pairs
                     if task.is_completed(day) == completed]
        return pairs

    def detect_conflicts(self, schedule=None) -> list[str]:
        """Warn about overlapping intervals across all pets; touching endpoints are allowed."""
        entries = sorted(self.schedule if schedule is None else schedule,
                         key=lambda entry: entry[2])
        warnings = []
        for index, first in enumerate(entries):
            for second in entries[index + 1:]:
                if second[2] >= first[3]:
                    break
                if first[2] < second[3] and second[2] < first[3]:
                    warnings.append(
                        f"Conflict: {first[0].name}: {first[1].title} "
                        f"({first[2]:%H:%M}-{first[3]:%H:%M}) overlaps "
                        f"{second[0].name}: {second[1].title} "
                        f"({second[2]:%H:%M}-{second[3]:%H:%M})."
                    )
        return warnings

    def generate_plan(self) -> list[tuple[Pet, Task, datetime, datetime]]:
        """Reserve fixed appointments and fit flexible tasks into the remaining gaps."""
        window_start = self.owner.start_time
        window_end = window_start + timedelta(minutes=self.owner.available_minutes)
        plan_date = window_start.date()
        _require_minutes(self.owner.available_minutes, "Available minutes", 0)
        self.schedule = []
        reasons = ["Fixed times are reserved first. Flexible tasks use priority, "
                   "then preferred titles, then pet/task entry order."]
        preferred = {title.strip().casefold() for title in self.owner.preferences}
        due = []
        for pet, task in self.owner.get_all_tasks():
            label = f"{pet.name}: {task.title}"
            if task.is_completed(plan_date):
                reasons.append(f"Skipped {label}: already completed.")
            elif not task.is_due(plan_date):
                reasons.append(f"Skipped {label}: not due on {plan_date.isoformat()}.")
            else:
                due.append((pet, task))
        flexible = []
        for pet, task in self.sort_by_time(due):
            if task.fixed_start_time is None:
                flexible.append((pet, task))
                continue
            start = datetime.combine(plan_date, task.fixed_start_time,
                                     tzinfo=window_start.tzinfo)
            end = start + timedelta(minutes=task.duration_minutes)
            if start < window_start or end > window_end:
                reasons.append(f"Skipped {pet.name}: {task.title}: fixed time is outside the planning window.")
                continue
            self.schedule.append((pet, task, start, end))
            reasons.append(f"Reserved {pet.name}: {task.title} at {start:%H:%M}.")
        flexible.sort(key=lambda pair: (
            PRIORITY_ORDER[pair[1].priority],
            pair[1].title.strip().casefold() not in preferred,
        ))
        for pet, task in flexible:
            duration = timedelta(minutes=task.duration_minutes)
            start = window_start
            for entry in sorted(self.schedule, key=lambda item: item[2]):
                if start + duration <= entry[2]:
                    break
                if start < entry[3]:
                    start = entry[3]
            end = start + duration
            if end <= window_end:
                self.schedule.append((pet, task, start, end))
                reasons.append(f"Selected {pet.name}: {task.title}: "
                               f"{task.priority} priority; fits an available gap.")
            else:
                reasons.append(f"Skipped {pet.name}: {task.title}: no "
                               f"{task.duration_minutes}-minute gap remains.")
        self.schedule.sort(key=lambda entry: entry[2])
        warnings = self.detect_conflicts()
        reasons.extend(warnings)
        if warnings:
            reasons.append("Resolve the overlapping fixed times before following this plan.")
        if not self.schedule:
            reasons.append("No unfinished, due tasks fit the planning window.")
        # Merge intervals so overlapping reservations are not counted twice.
        occupied = timedelta()
        merged_start = merged_end = None
        for _, _, start, end in self.schedule:
            if merged_end is None or start > merged_end:
                if merged_end is not None:
                    occupied += merged_end - merged_start
                merged_start, merged_end = start, end
            else:
                merged_end = max(merged_end, end)
        if merged_end is not None:
            occupied += merged_end - merged_start
        minutes = int(occupied.total_seconds() / 60)
        reasons.append(f"Reserved clock time: {minutes}/{self.owner.available_minutes} min.")
        self.explanation = "\n".join(reasons)
        return list(self.schedule)

    def explain_plan(self) -> str:
        """Return the explanation from the latest plan, or ask for a plan first."""
        return self.explanation or "Generate a plan first to see its explanation."

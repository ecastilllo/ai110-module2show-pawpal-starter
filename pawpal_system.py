"""Pet care models and scheduling logic, independent of the Streamlit UI.

Data and completion history are kept in memory. Schedule entries contain
(pet, task, start_datetime, end_datetime). Python 3.10 or newer is required.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
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
    completed_dates: set[date] = field(default_factory=set, init=False, repr=False)

    def __post_init__(self) -> None:
        """Validate task details and set a default date for one-time tasks."""
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

    def generate_plan(self) -> list[tuple[Pet, Task, datetime, datetime]]:
        """Schedule due tasks by priority and preference while respecting the time budget."""
        plan_date = self.owner.start_time.date()
        remaining = self.owner.available_minutes
        _require_minutes(remaining, "Available minutes", 0)
        current_time = self.owner.start_time
        self.schedule = []
        reasons = [
            "Tasks are considered by priority (high to low), then preferred titles; "
            "other ties keep pet/task entry order."
        ]
        preferred = {title.strip().casefold() for title in self.owner.preferences}
        all_tasks = self.owner.get_all_tasks()
        candidates: list[tuple[Pet, Task]] = []
        for pet, task in all_tasks:
            label = f"{pet.name}: {task.title}"
            if task.is_completed(plan_date):
                reasons.append(f"Skipped {label}: already completed.")
            elif not task.is_due(plan_date):
                reasons.append(f"Skipped {label}: not due on {plan_date.isoformat()}.")
            else:
                candidates.append((pet, task))
        candidates.sort(
            key=lambda pair: (
                PRIORITY_ORDER[pair[1].priority],
                pair[1].title.strip().casefold() not in preferred,
            )
        )
        for pet, task in candidates:
            label = f"{pet.name}: {task.title}"
            if task.duration_minutes > remaining:
                reasons.append(
                    f"Skipped {label}: needs {task.duration_minutes} min; "
                    f"only {remaining} min remain."
                )
                continue
            end_time = current_time + timedelta(minutes=task.duration_minutes)
            self.schedule.append((pet, task, current_time, end_time))
            preference_note = (
                "; preferred title" if task.title.strip().casefold() in preferred else ""
            )
            reasons.append(
                f"Selected {label}: {task.priority} priority{preference_note}; "
                f"{task.duration_minutes} min fits the remaining time."
            )
            current_time = end_time
            remaining -= task.duration_minutes
        if not all_tasks:
            reasons.append("No care tasks have been added.")
        elif not self.schedule:
            reasons.append("No unfinished, due tasks fit the available time.")
        used = self.owner.available_minutes - remaining
        reasons.append(f"Time used: {used}/{self.owner.available_minutes} min; {remaining} min remaining.")
        self.explanation = "\n".join(reasons)
        return list(self.schedule)

    def explain_plan(self) -> str:
        """Return the explanation from the latest plan, or ask for a plan first."""
        return self.explanation or "Generate a plan first to see its explanation."

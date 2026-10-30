"""Phase 1 class skeletons for PawPal+.

Behavior methods are intentionally empty until the implementation phase.
A schedule entry is (pet, task, start_datetime, end_datetime).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


@dataclass
class Task:
    """A care activity. Duration is in minutes."""

    title: str
    duration_minutes: int
    priority: Literal["low", "medium", "high"]

    def update_details(
        self,
        title: str,
        duration_minutes: int,
        priority: Literal["low", "medium", "high"],
    ) -> None:
        """Update the task's title, duration, and priority."""
        pass


@dataclass
class Pet:
    """A pet and its own care tasks."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        pass

    def remove_task(self, task: Task) -> None:
        """Remove this task instance from this pet's care tasks."""
        pass


class Owner:
    """Owner details and the time window for a daily care plan."""

    def __init__(
        self,
        name: str,
        available_minutes: int,
        start_time: datetime,
        preferences: list[str] | None = None,
        pets: list[Pet] | None = None,
    ) -> None:
        self.name = name
        self.available_minutes = available_minutes
        self.start_time = start_time
        self.preferences = list(preferences) if preferences is not None else []
        self.pets = list(pets) if pets is not None else []

    def add_pet(self, pet: Pet) -> None:
        """Associate a pet with this owner."""
        pass

    def update_preferences(self, preferences: list[str]) -> None:
        """Set preferred task titles for breaking equal-priority ties."""
        pass


class Scheduler:
    """Build and explain a daily plan across the owner's pets."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner
        self.schedule: list[tuple[Pet, Task, datetime, datetime]] = []
        self.explanation: str = ""

    def generate_plan(self) -> list[tuple[Pet, Task, datetime, datetime]]:
        """Plan tasks using priority, preferences, and available minutes.

        Each entry contains its pet, task, start datetime, and end datetime.
        Tasks run consecutively from the owner's start time without overlaps.
        No task may extend beyond the owner's available time window.
        Input validation and scheduling behavior will be implemented later.
        """
        pass

    def explain_plan(self) -> str:
        """Explain selected and skipped tasks, including time constraints."""
        pass

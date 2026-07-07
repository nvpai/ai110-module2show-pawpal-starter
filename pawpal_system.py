"""PawPal+ logic layer.

Class skeletons generated from diagrams/uml.mmd.
Method bodies are stubs (no logic yet) — logic is implemented in a later phase.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum


class TaskType(Enum):
    """Category of a care task."""

    FEEDING = "feeding"
    WALK = "walk"
    MEDICATION = "medication"
    APPOINTMENT = "appointment"
    GROOMING = "grooming"
    OTHER = "other"


@dataclass
class RecurrencePattern:
    """Describes how a task repeats over time."""

    frequency: str  # e.g. "daily", "weekly", "monthly"
    interval: int = 1
    weekdays: list[int] = field(default_factory=list)
    until_date: date | None = None

    def next_occurrence(self, after: datetime) -> datetime:
        """Return the next datetime this task should occur after the given time."""
        raise NotImplementedError


@dataclass
class Task:
    """A single pet care activity."""

    id: str
    title: str
    type: TaskType
    duration_minutes: int
    priority: int = 3  # 1 (low) .. 5 (high)
    scheduled_time: datetime | None = None
    completed: bool = False
    recurrence: RecurrencePattern | None = None

    def check_conflict(self, other: "Task") -> bool:
        """Return True if this task's time overlaps with another task's time."""
        raise NotImplementedError

    def reschedule(self, new_time: datetime) -> None:
        """Move this task to a new scheduled time."""
        raise NotImplementedError

    def mark_completed(self) -> None:
        """Mark this task as done."""
        raise NotImplementedError


@dataclass
class Pet:
    """An animal owned by an Owner. Owns the tasks associated with it."""

    id: str
    name: str
    species: str
    breed: str = ""
    birthdate: date | None = None
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet."""
        raise NotImplementedError

    def remove_task(self, task_id: str) -> None:
        """Remove a task from this pet by id."""
        raise NotImplementedError

    def get_tasks(self) -> list[Task]:
        """Return this pet's tasks."""
        raise NotImplementedError


@dataclass
class Owner:
    """The pet owner and the scheduling constraints they bring."""

    id: str
    name: str
    email: str = ""
    available_minutes: int = 0  # daily time budget for pet care
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        raise NotImplementedError

    def remove_pet(self, pet_id: str) -> None:
        """Remove a pet from this owner by id."""
        raise NotImplementedError

    def get_all_tasks(self) -> list[Task]:
        """Gather tasks across all of this owner's pets."""
        raise NotImplementedError


class Scheduler:
    """Stateless helper that turns an owner's tasks into a daily plan."""

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered for the plan (e.g. by priority, then time)."""
        raise NotImplementedError

    def find_conflicts(self, tasks: list[Task]) -> list[Task]:
        """Return tasks that overlap in time with another task."""
        raise NotImplementedError

    def generate_daily_plan(self, owner: Owner, day: date) -> list[Task]:
        """Build the day's plan within the owner's time budget and priorities."""
        raise NotImplementedError

    def explain_plan(self, owner: Owner, day: date) -> str:
        """Return a human-readable explanation of why the plan was chosen."""
        raise NotImplementedError

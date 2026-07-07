"""PawPal+ logic layer.

Classes implemented from diagrams/uml.mmd. This is the backend "brain":
Owner -> Pets -> Tasks, with a stateless Scheduler that builds a daily plan
from an owner's tasks, respecting their time budget and task priorities.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
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
        if self.frequency == "daily":
            return after + timedelta(days=self.interval)
        if self.frequency == "weekly":
            return after + timedelta(weeks=self.interval)
        if self.frequency == "monthly":
            return after + timedelta(days=30 * self.interval)
        raise ValueError(f"Unknown frequency: {self.frequency}")


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

    def end_time(self) -> datetime | None:
        """Return when this task finishes, or None if it has no scheduled time."""
        if self.scheduled_time is None:
            return None
        return self.scheduled_time + timedelta(minutes=self.duration_minutes)

    def check_conflict(self, other: "Task") -> bool:
        """Return True if this task's time window overlaps another task's window."""
        if self.scheduled_time is None or other.scheduled_time is None:
            return False
        return self.scheduled_time < other.end_time() and other.scheduled_time < self.end_time()

    def reschedule(self, new_time: datetime) -> None:
        """Move this task to a new scheduled time."""
        self.scheduled_time = new_time

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True


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
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove a task from this pet by id."""
        self.tasks = [t for t in self.tasks if t.id != task_id]

    def get_tasks(self) -> list[Task]:
        """Return this pet's tasks."""
        return self.tasks


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
        self.pets.append(pet)

    def remove_pet(self, pet_id: str) -> None:
        """Remove a pet from this owner by id."""
        self.pets = [p for p in self.pets if p.id != pet_id]

    def get_all_tasks(self) -> list[Task]:
        """Gather tasks across all of this owner's pets."""
        tasks: list[Task] = []
        for pet in self.pets:
            tasks.extend(pet.get_tasks())
        return tasks


class Scheduler:
    """Stateless helper that turns an owner's tasks into a daily plan."""

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered by scheduled time, then higher priority first."""
        return sorted(
            tasks,
            key=lambda t: (
                t.scheduled_time or datetime.max,
                -t.priority,
            ),
        )

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered chronologically by scheduled time (unscheduled last)."""
        return sorted(tasks, key=lambda t: t.scheduled_time or datetime.max)

    def filter_by_status(self, tasks: list[Task], completed: bool = False) -> list[Task]:
        """Return only the tasks whose completed flag matches the given status."""
        return [t for t in tasks if t.completed == completed]

    def filter_by_pet(self, owner: Owner, pet_name: str) -> list[Task]:
        """Return tasks belonging to the pet with the given name (case-insensitive)."""
        return [
            t
            for pet in owner.pets
            if pet.name.lower() == pet_name.lower()
            for t in pet.get_tasks()
        ]

    def find_conflicts(self, tasks: list[Task]) -> list[Task]:
        """Return tasks that overlap in time with at least one other task."""
        conflicting: list[Task] = []
        for i, task in enumerate(tasks):
            for j, other in enumerate(tasks):
                if i != j and task.check_conflict(other):
                    conflicting.append(task)
                    break
        return conflicting

    def detect_conflicts(self, tasks: list[Task]) -> list[str]:
        """Return human-readable warning messages for each pair of overlapping tasks."""
        ordered = self.sort_by_time(tasks)
        warnings: list[str] = []
        for i in range(len(ordered)):
            for j in range(i + 1, len(ordered)):
                a, b = ordered[i], ordered[j]
                if a.check_conflict(b):
                    when = a.scheduled_time.strftime("%H:%M") if a.scheduled_time else "--:--"
                    warnings.append(
                        f"⚠️ Conflict at {when}: '{a.title}' overlaps with '{b.title}'"
                    )
        return warnings

    def mark_task_complete(self, pet: Pet, task: Task) -> Task | None:
        """Complete a task; if it recurs, add the next occurrence to the pet and return it.

        Returns the newly created follow-up task, or None for one-off tasks.
        """
        task.mark_complete()
        if task.recurrence is None or task.scheduled_time is None:
            return None
        next_time = task.recurrence.next_occurrence(task.scheduled_time)
        next_task = Task(
            id=f"{task.id}-{next_time.date().isoformat()}",
            title=task.title,
            type=task.type,
            duration_minutes=task.duration_minutes,
            priority=task.priority,
            scheduled_time=next_time,
            completed=False,
            recurrence=task.recurrence,
        )
        pet.add_task(next_task)
        return next_task

    def _tasks_for_day(self, owner: Owner, day: date) -> list[Task]:
        """Return the owner's uncompleted tasks scheduled on the given day."""
        return [
            t
            for t in owner.get_all_tasks()
            if t.scheduled_time is not None
            and t.scheduled_time.date() == day
            and not t.completed
        ]

    def generate_daily_plan(self, owner: Owner, day: date) -> list[Task]:
        """Select tasks that fit the owner's time budget, highest priority first."""
        candidates = self._tasks_for_day(owner, day)
        # Choose which tasks make the cut by priority (then earliest time).
        by_priority = sorted(
            candidates,
            key=lambda t: (-t.priority, t.scheduled_time or datetime.max),
        )
        plan: list[Task] = []
        used_minutes = 0
        budget = owner.available_minutes or sum(t.duration_minutes for t in candidates)
        for task in by_priority:
            if used_minutes + task.duration_minutes <= budget:
                plan.append(task)
                used_minutes += task.duration_minutes
        # Present the chosen tasks in chronological order.
        return self.sort_tasks(plan)

    def explain_plan(self, owner: Owner, day: date) -> str:
        """Return a human-readable explanation of why the plan was chosen."""
        candidates = self._tasks_for_day(owner, day)
        plan = self.generate_daily_plan(owner, day)
        chosen_ids = {t.id for t in plan}
        skipped = [t for t in candidates if t.id not in chosen_ids]
        used = sum(t.duration_minutes for t in plan)

        lines = [
            f"Plan for {owner.name} on {day.isoformat()}:",
            f"  Time budget: {owner.available_minutes} min | scheduled: {used} min "
            f"across {len(plan)} task(s).",
        ]
        for task in plan:
            when = task.scheduled_time.strftime("%H:%M") if task.scheduled_time else "--:--"
            lines.append(
                f"  {when} — {task.title} ({task.duration_minutes} min) "
                f"[priority {task.priority}]"
            )
        if skipped:
            lines.append("  Skipped (over budget or lower priority):")
            for task in skipped:
                lines.append(f"    - {task.title} [priority {task.priority}]")
        return "\n".join(lines)

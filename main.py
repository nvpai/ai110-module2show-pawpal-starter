"""CLI demo for PawPal+.

Builds a small owner/pet/task setup and exercises the scheduling algorithms:
sorting, filtering, conflict detection, recurring tasks, and the daily plan.
Run with: python main.py
"""

from datetime import datetime

from pawpal_system import Owner, Pet, RecurrencePattern, Scheduler, Task, TaskType

TODAY = datetime(2026, 7, 6)


def build_demo() -> Owner:
    """Create a sample owner with two pets and several tasks (added out of order)."""
    owner = Owner(
        id="o1",
        name="Alex",
        email="alex@example.com",
        available_minutes=60,  # tight budget so the scheduler has to make choices
        preferences=["mornings"],
    )

    biscuit = Pet(id="p1", name="Biscuit", species="dog", breed="Golden Retriever")
    mochi = Pet(id="p2", name="Mochi", species="cat", breed="Tabby")
    owner.add_pet(biscuit)
    owner.add_pet(mochi)

    # Tasks are intentionally added out of chronological order.
    mochi.add_task(
        Task("t4", "Grooming", TaskType.GROOMING, duration_minutes=45, priority=2,
             scheduled_time=TODAY.replace(hour=11, minute=0))
    )
    biscuit.add_task(
        Task("t2", "Breakfast", TaskType.FEEDING, duration_minutes=10, priority=5,
             scheduled_time=TODAY.replace(hour=9, minute=0),
             recurrence=RecurrencePattern(frequency="daily"))
    )
    biscuit.add_task(
        Task("t1", "Morning walk", TaskType.WALK, duration_minutes=30, priority=5,
             scheduled_time=TODAY.replace(hour=8, minute=0))
    )
    mochi.add_task(
        Task("t3", "Give medication", TaskType.MEDICATION, duration_minutes=5, priority=4,
             scheduled_time=TODAY.replace(hour=9, minute=30))
    )
    # Overlaps Biscuit's 8:00 walk to demonstrate conflict detection.
    mochi.add_task(
        Task("t5", "Vet call", TaskType.APPOINTMENT, duration_minutes=20, priority=4,
             scheduled_time=TODAY.replace(hour=8, minute=10))
    )

    return owner


def main() -> None:
    """Run the demo and exercise each scheduling algorithm."""
    owner = build_demo()
    scheduler = Scheduler()
    all_tasks = owner.get_all_tasks()

    print("=" * 48)
    print("PawPal+ Demo")
    print("=" * 48)

    print("\n[Sorting] All tasks by time:")
    for t in scheduler.sort_by_time(all_tasks):
        when = t.scheduled_time.strftime("%H:%M")
        print(f"  {when} — {t.title}")

    print("\n[Filtering] Tasks for Biscuit:")
    for t in scheduler.filter_by_pet(owner, "Biscuit"):
        print(f"  - {t.title}")

    print("\n[Conflict detection]")
    conflicts = scheduler.detect_conflicts(all_tasks)
    for warning in conflicts or ["  No conflicts found."]:
        print(f"  {warning}")

    print("\n[Recurring tasks] Completing Biscuit's daily 'Breakfast':")
    biscuit = owner.pets[0]
    breakfast = next(t for t in biscuit.get_tasks() if t.title == "Breakfast")
    follow_up = scheduler.mark_task_complete(biscuit, breakfast)
    if follow_up:
        print(f"  Next occurrence created: {follow_up.title} on "
              f"{follow_up.scheduled_time.date().isoformat()}")

    print("\n[Filtering] Pending (not completed) tasks for Biscuit:")
    for t in scheduler.filter_by_status(scheduler.filter_by_pet(owner, "Biscuit"), completed=False):
        print(f"  - {t.title} ({t.scheduled_time.date().isoformat()})")

    print("\n" + "=" * 48)
    print("Today's Schedule")
    print("=" * 48)
    print(scheduler.explain_plan(owner, TODAY.date()))


if __name__ == "__main__":
    main()

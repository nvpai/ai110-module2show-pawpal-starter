"""CLI demo for PawPal+.

Builds a small owner/pet/task setup and prints today's generated plan.
Run with: python main.py
"""

from datetime import datetime

from pawpal_system import Owner, Pet, Scheduler, Task, TaskType

TODAY = datetime(2026, 7, 6)


def build_demo() -> Owner:
    """Create a sample owner with two pets and several tasks."""
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

    biscuit.add_task(
        Task("t1", "Morning walk", TaskType.WALK, duration_minutes=30, priority=5,
             scheduled_time=TODAY.replace(hour=8, minute=0))
    )
    biscuit.add_task(
        Task("t2", "Breakfast", TaskType.FEEDING, duration_minutes=10, priority=5,
             scheduled_time=TODAY.replace(hour=9, minute=0))
    )
    mochi.add_task(
        Task("t3", "Give medication", TaskType.MEDICATION, duration_minutes=5, priority=4,
             scheduled_time=TODAY.replace(hour=9, minute=30))
    )
    mochi.add_task(
        Task("t4", "Grooming", TaskType.GROOMING, duration_minutes=45, priority=2,
             scheduled_time=TODAY.replace(hour=11, minute=0))
    )

    return owner


def main() -> None:
    """Run the demo and print today's schedule."""
    owner = build_demo()
    scheduler = Scheduler()

    print("=" * 44)
    print("PawPal+ — Today's Schedule")
    print("=" * 44)
    print(scheduler.explain_plan(owner, TODAY.date()))


if __name__ == "__main__":
    main()

"""Quick tests for core PawPal+ behaviors."""

from datetime import datetime

from pawpal_system import Owner, Pet, Scheduler, Task, TaskType


def make_task(task_id: str = "t1", **kwargs) -> Task:
    """Build a simple task for testing."""
    defaults = dict(title="Walk", type=TaskType.WALK, duration_minutes=30, priority=3)
    defaults.update(kwargs)
    return Task(id=task_id, **defaults)


def test_mark_complete_changes_status():
    """Calling mark_complete() flips the task's completed flag to True."""
    task = make_task()
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """Adding a task to a Pet increases that pet's task count."""
    pet = Pet(id="p1", name="Biscuit", species="dog")
    assert len(pet.get_tasks()) == 0
    pet.add_task(make_task())
    assert len(pet.get_tasks()) == 1


def test_daily_plan_respects_time_budget():
    """Scheduler drops lower-priority tasks that exceed the owner's time budget."""
    owner = Owner(id="o1", name="Alex", available_minutes=40)
    pet = Pet(id="p1", name="Biscuit", species="dog")
    owner.add_pet(pet)
    pet.add_task(make_task("t1", priority=5, duration_minutes=30,
                           scheduled_time=datetime(2026, 7, 6, 8, 0)))
    pet.add_task(make_task("t2", priority=1, duration_minutes=30,
                           scheduled_time=datetime(2026, 7, 6, 9, 0)))

    plan = Scheduler().generate_daily_plan(owner, datetime(2026, 7, 6).date())

    plan_ids = [t.id for t in plan]
    assert plan_ids == ["t1"]  # only the high-priority task fits in 40 min

"""Quick tests for core PawPal+ behaviors."""

from datetime import datetime

from pawpal_system import Owner, Pet, RecurrencePattern, Scheduler, Task, TaskType


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


def test_sort_by_time_orders_chronologically():
    """sort_by_time() returns tasks earliest-first regardless of insertion order."""
    late = make_task("t1", scheduled_time=datetime(2026, 7, 6, 11, 0))
    early = make_task("t2", scheduled_time=datetime(2026, 7, 6, 8, 0))
    ordered = Scheduler().sort_by_time([late, early])
    assert [t.id for t in ordered] == ["t2", "t1"]


def test_filter_by_status_and_pet():
    """Filtering returns only pending tasks for the named pet."""
    owner = Owner(id="o1", name="Alex")
    pet = Pet(id="p1", name="Biscuit", species="dog")
    owner.add_pet(pet)
    done = make_task("t1")
    done.mark_complete()
    pet.add_task(done)
    pet.add_task(make_task("t2"))

    scheduler = Scheduler()
    biscuit_tasks = scheduler.filter_by_pet(owner, "biscuit")  # case-insensitive
    pending = scheduler.filter_by_status(biscuit_tasks, completed=False)
    assert [t.id for t in pending] == ["t2"]


def test_detect_conflicts_returns_warning():
    """Overlapping tasks produce a warning message; separate ones do not."""
    a = make_task("t1", duration_minutes=30, scheduled_time=datetime(2026, 7, 6, 8, 0))
    b = make_task("t2", duration_minutes=20, scheduled_time=datetime(2026, 7, 6, 8, 10))
    c = make_task("t3", duration_minutes=10, scheduled_time=datetime(2026, 7, 6, 12, 0))
    warnings = Scheduler().detect_conflicts([a, b, c])
    assert len(warnings) == 1
    assert "overlaps" in warnings[0]


def test_mark_task_complete_creates_next_occurrence():
    """Completing a daily task marks it done and adds tomorrow's occurrence to the pet."""
    pet = Pet(id="p1", name="Biscuit", species="dog")
    task = make_task("t1", scheduled_time=datetime(2026, 7, 6, 9, 0),
                     recurrence=RecurrencePattern(frequency="daily"))
    pet.add_task(task)

    follow_up = Scheduler().mark_task_complete(pet, task)

    assert task.completed is True
    assert follow_up is not None
    assert follow_up.completed is False
    assert follow_up.scheduled_time == datetime(2026, 7, 7, 9, 0)
    assert len(pet.get_tasks()) == 2


def test_mark_task_complete_no_recurrence_returns_none():
    """A one-off task completes without spawning a follow-up."""
    pet = Pet(id="p1", name="Biscuit", species="dog")
    task = make_task("t1", scheduled_time=datetime(2026, 7, 6, 9, 0))
    pet.add_task(task)
    assert Scheduler().mark_task_complete(pet, task) is None
    assert len(pet.get_tasks()) == 1

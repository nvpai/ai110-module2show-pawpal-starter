# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## ✨ Features

- **Owner & pets** — manage an owner and multiple pets, each with their own list of care tasks.
- **Tasks** — track title, type (walk/feeding/medication/etc.), duration, priority (1–5), time, and completion.
- **Sorting by time** — tasks are ordered chronologically (`Scheduler.sort_by_time()`), or by time-then-priority for the plan (`sort_tasks()`).
- **Filtering** — filter tasks by pet name (case-insensitive) or completion status.
- **Budget-aware daily plan** — fits the highest-priority tasks into the owner's available minutes and explains what was chosen or skipped.
- **Conflict warnings** — detects overlapping time windows and returns a warning message instead of crashing.
- **Daily/weekly recurrence** — completing a recurring task automatically schedules its next occurrence.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

Output from running `python main.py`:

```
================================================
PawPal+ Demo
================================================

[Sorting] All tasks by time:
  08:00 — Morning walk
  08:10 — Vet call
  09:00 — Breakfast
  09:30 — Give medication
  11:00 — Grooming

[Filtering] Tasks for Biscuit:
  - Breakfast
  - Morning walk

[Conflict detection]
  ⚠️ Conflict at 08:00: 'Morning walk' overlaps with 'Vet call'

[Recurring tasks] Completing Biscuit's daily 'Breakfast':
  Next occurrence created: Breakfast on 2026-07-07

[Filtering] Pending (not completed) tasks for Biscuit:
  - Morning walk (2026-07-06)
  - Breakfast (2026-07-07)

================================================
Today's Schedule
================================================
Plan for Alex on 2026-07-06:
  Time budget: 60 min | scheduled: 55 min across 3 task(s).
  08:00 — Morning walk (30 min) [priority 5]
  08:10 — Vet call (20 min) [priority 4]
  09:30 — Give medication (5 min) [priority 4]
  Skipped (over budget or lower priority):
    - Grooming [priority 2]
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest

# Run with coverage:
pytest --cov
```

**What the tests cover** (`tests/test_pawpal.py`):

- **Core behavior** — marking a task complete flips its status; adding a task to a pet increases its task count.
- **Sorting correctness** — `sort_by_time()` returns tasks in chronological order regardless of insertion order.
- **Filtering** — filtering by pet name (case-insensitive) and by completion status returns the right subset.
- **Budget scheduling** — `generate_daily_plan()` drops lower-priority tasks that exceed the owner's time budget.
- **Recurrence logic** — completing a daily task marks it done and auto-creates the next day's occurrence; one-off tasks do not.
- **Conflict detection** — overlapping and exact-same-time tasks are flagged; back-to-back (non-overlapping) tasks are not.
- **Edge cases** — a pet with no tasks produces an empty plan and no conflicts without crashing.

Sample test output:

```
============================= test session starts ==============================
platform darwin -- Python 3.12.7, pytest-9.0.3, pluggy-1.6.0
collected 11 items

tests/test_pawpal.py ...........                                         [100%]

============================== 11 passed in 0.02s ==============================
```

**Confidence level: ★★★★☆ (4/5)** — All 11 tests pass and cover the core logic, algorithms, and key edge cases. Held back one star because time-zone handling and multi-day/weekly recurrence over month boundaries aren't yet exercised.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.sort_tasks()` | `sort_by_time()` orders chronologically; `sort_tasks()` orders by time then higher priority |
| Filtering | `Scheduler.filter_by_pet()`, `Scheduler.filter_by_status()` | Filter tasks by pet name (case-insensitive) or completion status |
| Budgeting | `Scheduler.generate_daily_plan()` | Fills the owner's `available_minutes` budget highest-priority-first; skips tasks that don't fit |
| Conflict detection | `Task.check_conflict()`, `Scheduler.detect_conflicts()` | Pairwise overlap check; returns warning messages instead of crashing |
| Recurring tasks | `Scheduler.mark_task_complete()`, `RecurrencePattern.next_occurrence()` | Completing a daily/weekly task auto-creates the next occurrence via `timedelta` |

## 📸 Demo Walkthrough

Run the app with `streamlit run app.py`. The UI is organized top-to-bottom so a
pet owner can go from setup to a finished plan in one pass.

**Main UI features / actions a user can perform:**

- **Owner setup** — set the owner's name and the *available minutes* they have for pet care today.
- **Add a pet** — enter a name and species; the pet is stored in `st.session_state` so it persists across interactions.
- **Add a task** — pick which pet, then set title, type, duration, priority, and time.
- **Current tasks table** — shows all tasks sorted by time (then priority), with a ✅ for completed ones.
- **Conflict warnings** — overlapping tasks are flagged inline with a ⚠️ warning; a green "no conflicts" message shows otherwise.
- **Generate schedule** — builds today's plan within the time budget and offers a "Why this plan?" explanation.

**Example workflow:**

1. Set available minutes to `60`.
2. Add a pet — *Biscuit (dog)*.
3. Add three tasks: *Morning walk* (8:00, 30 min, high), *Vet call* (8:10, 20 min, high), *Grooming* (11:00, 45 min, low).
4. The current-tasks table shows them sorted by time, and a ⚠️ warning appears because the walk and vet call overlap.
5. Click **Generate schedule** — the plan keeps the two high-priority morning tasks within the 60-minute budget and skips low-priority grooming, with an explanation of why.

**Key Scheduler behaviors shown:** chronological sorting, budget-based selection, priority ordering, conflict warnings, and the plan explanation.

**Sample CLI output** (from `python main.py`):

```
================================================
PawPal+ Demo
================================================

[Sorting] All tasks by time:
  08:00 — Morning walk
  08:10 — Vet call
  09:00 — Breakfast
  09:30 — Give medication
  11:00 — Grooming

[Filtering] Tasks for Biscuit:
  - Breakfast
  - Morning walk

[Conflict detection]
  ⚠️ Conflict at 08:00: 'Morning walk' overlaps with 'Vet call'

[Recurring tasks] Completing Biscuit's daily 'Breakfast':
  Next occurrence created: Breakfast on 2026-07-07

[Filtering] Pending (not completed) tasks for Biscuit:
  - Morning walk (2026-07-06)
  - Breakfast (2026-07-07)

================================================
Today's Schedule
================================================
Plan for Alex on 2026-07-06:
  Time budget: 60 min | scheduled: 55 min across 3 task(s).
  08:00 — Morning walk (30 min) [priority 5]
  08:10 — Vet call (20 min) [priority 4]
  09:30 — Give medication (5 min) [priority 4]
  Skipped (over budget or lower priority):
    - Grooming [priority 2]
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->

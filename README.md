# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

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
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.sort_tasks()` | `sort_by_time()` orders chronologically; `sort_tasks()` orders by time then higher priority |
| Filtering | `Scheduler.filter_by_pet()`, `Scheduler.filter_by_status()` | Filter tasks by pet name (case-insensitive) or completion status |
| Budgeting | `Scheduler.generate_daily_plan()` | Fills the owner's `available_minutes` budget highest-priority-first; skips tasks that don't fit |
| Conflict detection | `Task.check_conflict()`, `Scheduler.detect_conflicts()` | Pairwise overlap check; returns warning messages instead of crashing |
| Recurring tasks | `Scheduler.mark_task_complete()`, `RecurrencePattern.next_occurrence()` | Completing a daily/weekly task auto-creates the next occurrence via `timedelta` |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->

# PawPal+ Project Reflection

## 1. System Design

Three core actions:
- Enter pet and owner info
- Add and edit Task for pets based on owner time and priority
- View the daily plan with reasoning

Objects:
- Owner
    * Attributes: id, name, email, available_minutes (daily time budget), preferences, list of Pets
    * Methods: add_pet(), remove_pet(), get_all_tasks()
- Pet
    * Attributes: id, name, species, breed, birthdate, list of Tasks
    * Methods: add_task(), remove_task(), get_tasks()
- Task
    * Attributes: id, title, type (TaskType), scheduled_time, duration_minutes, priority (1-5), completed, recurrence
    * Methods: check_conflict(other), reschedule(), mark_complete()
- Scheduler (stateless)
    * Methods: sort_tasks(), find_conflicts(), generate_daily_plan(owner, date), explain_plan(owner, date)
- Supporting types
    * TaskType: enum (Feeding, Walk, Medication, Appointment, Grooming, Other)
    * RecurrencePattern: frequency, interval, weekdays, until_date, next_occurrence()

Relationships:
- Owner "1" — "*" Pet (an owner owns many pets)
- Pet "1" — "*" Task (each task belongs to one pet)
- Task references a TaskType and an optional RecurrencePattern
- Scheduler reads an Owner (and its pets' tasks) to build a daily plan


**a. Initial design**

My initial UML has four main classes plus two supporting types:

- **Owner** — represents the pet owner. Holds identity info (name, email), the daily time budget (`available_minutes`) and `preferences` used as scheduling constraints, and the list of pets. Responsible for managing pets and gathering all tasks across those pets (`get_all_tasks()`).
- **Pet** — represents one animal (name, species, breed, birthdate) and owns the list of tasks associated with it. Responsible for adding/removing/retrieving its own tasks. Tasks live here as the single source of truth.
- **Task** — represents one care activity. Holds title, type, scheduled time, duration, priority, completion status, and an optional recurrence. Responsible for its own behavior: detecting conflicts with another task, rescheduling, and marking itself complete.
- **Scheduler** — a stateless helper that turns an owner's tasks into a daily plan. Responsible for sorting tasks (by priority/time), detecting conflicts, generating the daily plan within the owner's time budget, and explaining the reasoning.
- **TaskType** (enum) and **RecurrencePattern** support the Task class by categorizing tasks and describing how they repeat.


**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler considers three things:
- **Time budget** — the owner's `available_minutes` caps how much care can be planned in a day. The scheduler adds tasks only while the running total stays within this budget.
- **Priority** — each task has a priority (1 low – 5 high). When the budget is tight, the scheduler fills it highest-priority-first so the most important tasks always make the cut.
- **Scheduled time** — used to order the final plan chronologically (and to detect conflicts between overlapping tasks).

I decided **priority mattered most for *selection*** (deciding *which* tasks make it into a limited day) and **time mattered most for *presentation*** (deciding the *order* they appear). This mirrors the real scenario: a busy owner would rather guarantee the walk and medication happen than fit in optional grooming.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

One tradeoff: the scheduler fills the budget strictly by priority, so a **low-priority task can be dropped even when there is an open time slot later in the day**. For example, with a 60-minute budget the plan keeps the walk, breakfast, and medication (45 min total) but skips grooming — even though grooming is scheduled at 11:00 when nothing else is happening.

This is reasonable for the scenario because the goal is *consistency on what matters*, not packing the calendar. A busy owner benefits more from a short, high-confidence list of essential tasks than from a full agenda where a critical task might get squeezed out. The tradeoff is also transparent — `explain_plan()` shows exactly what was skipped and why — so the owner can raise the budget if they want the extra tasks included.

A second tradeoff is in conflict detection (`detect_conflicts()`). I chose to check for **overlapping durations** (does task A's time window intersect task B's?) rather than only **exact start-time matches**. Exact-match checking would be simpler and faster, but it would miss the common real case where a 30-minute walk at 8:00 collides with a vet call at 8:10. The cost is a slower O(n²) pairwise comparison and a reliance on each task's `duration_minutes` being accurate. For a single owner with a handful of daily tasks this is negligible, and the method only *warns* (returns messages) rather than blocking or auto-rescheduling, leaving the owner in control.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used AI across every phase, but for different jobs:
- **Design brainstorming** — generating the first Mermaid UML and the class skeleton from my brainstormed attributes/methods.
- **Scaffolding** — turning the UML into dataclass stubs, then fleshing out method bodies.
- **Algorithm implementation** — sorting with `lambda` keys, `timedelta`-based recurrence, and a lightweight conflict-detection strategy.
- **Test generation** — drafting the pytest suite and suggesting edge cases (empty pet, exact-time conflicts, back-to-back boundaries).
- **Documentation** — drafting the Features list and Demo Walkthrough.

The most helpful prompts were **specific and grounded in my files** — e.g. "based on my skeleton, how should the Scheduler retrieve all tasks from the Owner's pets?" and "give me a *lightweight* conflict-detection strategy that returns a warning instead of crashing." Open-ended prompts produced generic code; constraint-loaded prompts produced code that fit my design.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

The AI initially modeled tasks on **both** `Owner` and `Pet`, which meant task data was duplicated in two places. I rejected that and consolidated tasks onto `Pet` as the single source of truth, with `Owner.get_all_tasks()` gathering across pets — this removed a whole class of "which copy is correct?" bugs. I also changed conflict detection from the AI's first idea (exact start-time match) to full interval-overlap checking, because exact-match would miss a 30-min walk overlapping a call 10 minutes later.

I verified suggestions three ways: reading the logic line by line, running `main.py` to watch real output, and running `pytest` to confirm the behavior held (including deliberately adding overlapping tasks to confirm the warning fired).

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I tested the core behaviors and the algorithmic layer: task completion and addition, chronological sorting, filtering by pet/status, budget-based plan selection, recurrence (a completed daily task spawns tomorrow's occurrence), and conflict detection (overlap, exact-same-time, and a back-to-back non-conflict boundary). I also tested edge cases like a pet with no tasks producing an empty plan without crashing. These matter because sorting, budgeting, and conflict detection are the "smart" parts users rely on — a silent bug there produces a wrong-but-plausible plan, which is worse than an obvious crash.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I'm fairly confident (★★★★☆ / 4 of 5) — all 11 tests pass and cover the main paths and key edges. With more time I'd test weekly/monthly recurrence across month boundaries, time-zone handling, tasks with no scheduled time flowing through the plan, and very large task lists (to confirm the O(n²) conflict check is still acceptable).

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I'm most satisfied with the clean separation between the logic layer (`pawpal_system.py`) and the UI (`app.py`). Because I built and verified the "brain" CLI-first with `main.py` and tests, wiring it into Streamlit was mostly plumbing — and the same methods (`sort_tasks`, `detect_conflicts`, `generate_daily_plan`) powered both the terminal demo and the app.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I'd let the scheduler *use* the conflict information rather than just warn about it — e.g. offer to auto-reschedule the lower-priority task to the next free slot. I'd also make recurrence smarter (respect `weekdays` and `until_date`, which exist on `RecurrencePattern` but aren't fully used yet).

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

The biggest lesson was that **being the "lead architect" means owning the design decisions even when the AI writes the code.** The AI is excellent at producing plausible code fast, but it will happily introduce duplication or subtle logic gaps (like tasks living in two places, or exact-match conflicts). My job was to hold the mental model of the system, insist on a single source of truth, and verify every suggestion against real output and tests. Using separate chat sessions per phase helped a lot — keeping design, algorithms, and testing in their own contexts stopped earlier decisions from muddying later ones and made each conversation focused.

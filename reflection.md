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

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

from datetime import datetime

import streamlit as st

# Step 1: bring the logic layer classes into the UI.
from pawpal_system import Owner, Pet, Scheduler, Task, TaskType

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Plan your pets' care for the day, prioritized to fit your available time.")

st.divider()

st.subheader("Quick Demo Inputs")

# Step 2: Streamlit re-runs this script top-to-bottom on every click, so we keep
# the Owner (and its pets/tasks) in st.session_state so the data persists.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(id="owner", name="Jordan", available_minutes=120)
if "next_id" not in st.session_state:
    st.session_state.next_id = 1

owner = st.session_state.owner
scheduler = Scheduler()


def new_id(prefix: str) -> str:
    """Return a unique id for a newly created pet or task."""
    value = f"{prefix}{st.session_state.next_id}"
    st.session_state.next_id += 1
    return value


owner.name = st.text_input("Owner name", value=owner.name)
owner.available_minutes = st.number_input(
    "Available minutes today", min_value=0, max_value=1440, value=owner.available_minutes, step=10
)

st.markdown("#### Add a pet")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
# Step 3: adding a pet in the browser calls Owner.add_pet() on the stored object.
if st.button("Add pet") and pet_name:
    owner.add_pet(Pet(id=new_id("p"), name=pet_name, species=species))
    st.success(f"Added {pet_name}.")

if owner.pets:
    st.caption("Pets: " + ", ".join(f"{p.name} ({p.species})" for p in owner.pets))

st.markdown("### Tasks")
st.caption("Add a few tasks. These feed into your scheduler below.")

# The UI shows friendly labels; Task uses a 1-5 priority scale.
PRIORITY_LABELS = {"low": 1, "medium": 3, "high": 5}

if not owner.pets:
    st.info("Add a pet above before adding tasks.")
else:
    pet_by_label = {f"{p.name} ({p.species})": p for p in owner.pets}
    pet_label = st.selectbox("For which pet?", list(pet_by_label.keys()))

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", list(PRIORITY_LABELS.keys()), index=2)

    col4, col5 = st.columns(2)
    with col4:
        task_type = st.selectbox("Type", [t.name.title() for t in TaskType])
    with col5:
        task_time = st.time_input("Time")

    # Step 3: adding a task calls Pet.add_task() on the selected pet.
    if st.button("Add task") and task_title:
        pet = pet_by_label[pet_label]
        pet.add_task(
            Task(
                id=new_id("t"),
                title=task_title,
                type=TaskType[task_type.upper()],
                duration_minutes=int(duration),
                priority=PRIORITY_LABELS[priority],
                scheduled_time=datetime.combine(datetime.now().date(), task_time),
            )
        )
        st.success(f"Added '{task_title}' for {pet.name}.")

    all_tasks = owner.get_all_tasks()
    if all_tasks:
        st.write("Current tasks (sorted by time, then priority):")
        st.table(
            [
                {
                    "task": t.title,
                    "time": t.scheduled_time.strftime("%H:%M") if t.scheduled_time else "--:--",
                    "duration_minutes": t.duration_minutes,
                    "priority": t.priority,
                    "done": "✅" if t.completed else "",
                }
                for t in scheduler.sort_tasks(all_tasks)
            ]
        )
        # Surface scheduling conflicts as warnings so the owner can fix them.
        conflicts = scheduler.detect_conflicts(all_tasks)
        if conflicts:
            for warning in conflicts:
                st.warning(warning)
        else:
            st.success("No scheduling conflicts. 🎉")
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generates today's plan by fitting the highest-priority tasks into your available time.")

if st.button("Generate schedule"):
    today = datetime.now().date()
    plan = scheduler.generate_daily_plan(owner, today)
    if not plan:
        st.warning("No tasks fit today's plan. Add tasks or increase available minutes.")
    else:
        for task in plan:
            when = task.scheduled_time.strftime("%H:%M") if task.scheduled_time else "--:--"
            st.markdown(
                f"- **{when}** — {task.title} ({task.duration_minutes} min) · priority {task.priority}"
            )
        with st.expander("Why this plan?"):
            st.code(scheduler.explain_plan(owner, today))

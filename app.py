"""Streamlit interface for PawPal's in-memory care planner."""

from datetime import date, datetime, time

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.write("Organize your pets' care and build a plan that fits your day.")
st.caption("Your data stays available during this browser session. Reloading the page or restarting the app can reset it.")

if "owner" not in st.session_state:
    st.session_state.owner = Owner(
        "Jordan", 45, datetime.combine(date.today(), time(8, 0))
    )
if "show_plan" not in st.session_state:
    st.session_state.show_plan = False

owner = st.session_state.owner

st.subheader("Your planning window")
with st.form("owner_settings"):
    name = st.text_input("Owner name", value=owner.name)
    plan_date = st.date_input("Planning date", value=owner.start_time.date())
    start_time = st.time_input("Start time", value=owner.start_time.time())
    available = st.number_input(
        "Available minutes", min_value=0, max_value=1440,
        value=owner.available_minutes, step=5,
    )
    preferences = st.text_input(
        "Preferred task titles (comma-separated)",
        value=", ".join(owner.preferences),
        help="Preferences break ties between tasks with the same priority.",
    )
    save_settings = st.form_submit_button("Save planning settings")
if save_settings:
    try:
        updated = Owner(
            name.strip(), int(available), datetime.combine(plan_date, start_time),
            [item.strip() for item in preferences.split(",") if item.strip()],
            owner.pets,
        )
        st.session_state.owner = updated
        owner = updated
        st.session_state.show_plan = False
        st.success("Planning settings saved.")
    except ValueError as error:
        st.error(str(error))

st.subheader("Your pets")
with st.form("add_pet"):
    pet_name = st.text_input("Pet name")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    add_pet = st.form_submit_button("Add pet")
if add_pet:
    try:
        owner.add_pet(Pet(pet_name.strip(), species))
        st.session_state.show_plan = False
        st.success(f"Added {pet_name.strip()}.")
    except ValueError as error:
        st.error(str(error))

if owner.pets:
    st.table([
        {"Pet": pet.name, "Species": pet.species, "Tasks": len(pet.tasks)}
        for pet in owner.pets
    ])
else:
    st.info("Add a pet to start creating care tasks.")

st.subheader("Care tasks")
if owner.pets:
    with st.form("add_task"):
        pet_index = st.selectbox(
            "Pet", options=list(range(len(owner.pets))),
            format_func=lambda index: f"{index + 1}. {owner.pets[index].name}",
        )
        title = st.text_input("Task title")
        description = st.text_input("Description (optional)")
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=10)
        priority = st.selectbox("Priority", ["high", "medium", "low"])
        frequency = st.selectbox("Frequency", ["daily", "weekly", "once"])
        weekday = st.selectbox(
            "Weekday (weekly tasks only)", options=list(range(7)),
            format_func=lambda index: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][index],
        )
        due_date = st.date_input("Due date (one-time tasks only)", value=owner.start_time.date())
        add_task = st.form_submit_button("Add task")
    if add_task:
        try:
            task = Task(
                title.strip(), int(duration), priority,
                description=description, frequency=frequency,
                weekday=weekday if frequency == "weekly" else None,
                due_date=due_date if frequency == "once" else None,
            )
            owner.pets[pet_index].add_task(task)
            st.session_state.show_plan = False
            st.success(f"Added {task.title} for {owner.pets[pet_index].name}.")
        except ValueError as error:
            st.error(str(error))

all_tasks = owner.get_all_tasks()
if all_tasks:
    planning_day = owner.start_time.date()
    st.table([
        {
            "Pet": pet.name,
            "Task": task.title,
            "Minutes": task.duration_minutes,
            "Priority": task.priority,
            "Frequency": task.frequency,
            "Status": "Completed" if task.is_completed(planning_day) else (
                "Due" if task.is_due(planning_day) else "Not due"
            ),
        }
        for pet, task in all_tasks
    ])
    with st.form("complete_task"):
        task_index = st.selectbox(
            "Task to complete for the saved planning date",
            options=list(range(len(all_tasks))),
            format_func=lambda index: f"{index + 1}. {all_tasks[index][0].name}: {all_tasks[index][1].title}",
        )
        complete = st.form_submit_button("Mark complete")
    if complete:
        try:
            all_tasks[task_index][1].mark_complete(planning_day)
            st.session_state.show_plan = False
            st.rerun()
        except ValueError as error:
            st.error(str(error))

st.subheader("Daily schedule")
st.caption(
    f"Saved plan: {owner.start_time:%Y-%m-%d at %H:%M} | "
    f"{owner.available_minutes} minutes. Save any changed settings before generating."
)
if st.button("Generate schedule", disabled=not all_tasks):
    st.session_state.show_plan = True

if st.session_state.show_plan:
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()
    if plan:
        st.table([
            {
                "Start": start.strftime("%Y-%m-%d %H:%M"),
                "End": end.strftime("%Y-%m-%d %H:%M"),
                "Pet": pet.name,
                "Task": task.title,
                "Priority": task.priority,
            }
            for pet, task, start, end in plan
        ])
    else:
        st.info("No unfinished tasks due on this date fit the available time.")
    st.text(scheduler.explain_plan())

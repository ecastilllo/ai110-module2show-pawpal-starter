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
if "notice" in st.session_state:
    st.success(st.session_state.pop("notice"))

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
        due_date = st.date_input("First due date (all frequencies)", value=owner.start_time.date())
        use_fixed_time = st.checkbox("Use a fixed start time")
        fixed_time = st.time_input("Fixed start time (when enabled)", value=time(8, 0))
        add_task = st.form_submit_button("Add task")
    if add_task:
        try:
            task = Task(
                title.strip(), int(duration), priority,
                description=description, frequency=frequency,
                weekday=weekday if frequency == "weekly" else None,
                due_date=due_date,
                fixed_start_time=fixed_time if use_fixed_time else None,
            )
            owner.pets[pet_index].add_task(task)
            st.session_state.show_plan = False
            st.success(f"Added {task.title} for {owner.pets[pet_index].name}.")
        except ValueError as error:
            st.error(str(error))

all_tasks = owner.get_all_tasks()
if all_tasks:
    planning_day = owner.start_time.date()
    view_scheduler = Scheduler(owner)
    pet_filter = st.selectbox("Filter by pet name", [None] + sorted({pet.name for pet in owner.pets}), format_func=lambda name: "All pets" if name is None else name)
    status_filter = st.selectbox("Filter by status", ["All", "Incomplete", "Completed"])
    completed_filter = {"All": None, "Incomplete": False, "Completed": True}[status_filter]
    visible_tasks = view_scheduler.sort_by_time(view_scheduler.filter_tasks(pet_name=pet_filter, completed=completed_filter))
    st.caption(f"Showing {len(visible_tasks)} of {len(all_tasks)} occurrences, sorted by fixed time. Automatic tasks appear last. Filters affect this list only.")
    if not visible_tasks:
        st.info("No tasks match these filters.")
    st.table([
        {
            "Pet": pet.name,
            "Task": task.title,
            "Minutes": task.duration_minutes,
            "Priority": task.priority,
            "Frequency": task.frequency,
            "Due date": task.due_date.isoformat(),
            "Fixed start": task.fixed_start_time.strftime("%H:%M") if task.fixed_start_time else "Automatic",
            "Status": "Completed" if task.is_completed(planning_day) else (
                "Due" if task.is_due(planning_day) else "Not due"
            ),
        }
        for pet, task in visible_tasks
    ])
    editable = [(pet, task) for pet, task in all_tasks if not task.completed]
    if editable:
        with st.expander("Edit a task or resolve a time conflict"):
            edit_index = st.selectbox(
                "Occurrence to edit", range(len(editable)),
                format_func=lambda i: f"{i + 1}. {editable[i][0].name}: {editable[i][1].title} (due {editable[i][1].due_date})",
            )
            edit_pet, edit_task = editable[edit_index]
            # Different form keys keep values from a previously selected task separate.
            with st.form(f"edit_task_{id(edit_task)}"):
                edit_title = st.text_input("Title", value=edit_task.title)
                edit_minutes = st.number_input("Minutes", min_value=1, value=edit_task.duration_minutes)
                edit_priority = st.selectbox("Task priority", ["high", "medium", "low"], index=["high", "medium", "low"].index(edit_task.priority))
                edit_fixed = st.checkbox("Keep a fixed time", value=edit_task.fixed_start_time is not None)
                edit_clock = st.time_input("Appointment time", value=edit_task.fixed_start_time or time(8))
                save_edit = st.form_submit_button("Save task changes")
            if save_edit:
                try:
                    edit_task.update_details(edit_title.strip(), int(edit_minutes), edit_priority)
                    edit_task.fixed_start_time = edit_clock if edit_fixed else None
                    st.session_state.show_plan = False
                    st.session_state.notice = f"Updated {edit_task.title}. Generate the schedule to check the new time."
                    st.rerun()
                except ValueError as error:
                    st.error(str(error))
    with st.form("complete_task"):
        task_index = st.selectbox(
            "Task to complete for the saved planning date",
            options=list(range(len(all_tasks))),
            format_func=lambda index: f"{index + 1}. {all_tasks[index][0].name}: {all_tasks[index][1].title} (due {all_tasks[index][1].due_date})",
        )
        complete = st.form_submit_button("Mark complete")
    if complete:
        try:
            pet, task = all_tasks[task_index]
            upcoming = Scheduler(owner).mark_task_complete(pet, task, planning_day)
            st.session_state.notice = f"Completed {task.title}." + (f" Next occurrence: {upcoming.due_date}." if upcoming else "")
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
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        st.warning("This plan has overlapping appointments. Open ‘Edit a task or resolve a time conflict’, change one fixed time, then generate again.")
        for warning in conflicts:
            st.warning(warning)
    elif plan:
        st.success("Your plan is ready. No overlapping appointments were found.")
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
    with st.expander("Why this plan?", expanded=bool(conflicts)):
        st.text(scheduler.explain_plan())

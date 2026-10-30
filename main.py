"""Run a two-pet CLI demonstration with no external dependencies."""

from datetime import date, datetime, time

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    """Build today's example plan and print readable times and selection reasons."""
    today = date.today()
    owner = Owner("Jordan", 45, datetime.combine(today, time(8, 0)), ["Feeding"])
    biscuit = Pet("Biscuit", "dog")
    mochi = Pet("Mochi", "cat")
    owner.add_pet(biscuit)
    owner.add_pet(mochi)

    biscuit.add_task(Task("Morning walk", 25, "high", description="A morning walk outside."))
    biscuit.add_task(Task("Grooming", 20, "low", frequency="weekly", weekday=today.weekday()))
    mochi.add_task(Task("Feeding", 10, "high", description="Serve breakfast."))
    mochi.add_task(Task("Enrichment", 10, "medium", description="Interactive play."))
    mochi.add_task(Task("Restock food", 15, "low", frequency="once", due_date=today))

    completed_task = Task("Refresh water", 5, "high")
    mochi.add_task(completed_task)
    Scheduler(owner).mark_task_complete(mochi, completed_task)

    # Deliberately add fixed tasks out of chronological order.
    biscuit.add_task(Task("Bath", 15, "medium", fixed_start_time=time(8, 15)))
    mochi.add_task(Task("Breakfast appointment", 20, "high", fixed_start_time=time(8, 0)))

    scheduler = Scheduler(owner)
    print("Tasks sorted by fixed time (automatic tasks last):")
    for pet, task in scheduler.sort_by_time():
        clock = task.fixed_start_time.strftime("%H:%M") if task.fixed_start_time else "Automatic"
        print(f"{clock} | {pet.name}: {task.title}")
    print("\nIncomplete tasks for Mochi:")
    for pet, task in scheduler.filter_tasks(pet_name="Mochi", completed=False):
        print(f"- {pet.name}: {task.title}")
    print()
    plan = scheduler.generate_plan()
    print(f"Today's Schedule - {today.isoformat()}")
    print(f"Owner: {owner.name} | Available time: {owner.available_minutes} minutes")
    print()
    for pet, task, start, end in plan:
        print(
            f"{start:%H:%M}-{end:%H:%M} | {pet.name} ({pet.species}) | "
            f"{task.title} ({task.duration_minutes} min) "
            f"[priority: {task.priority}, frequency: {task.frequency}]"
        )
    if not plan:
        print("No tasks scheduled.")
    print("\nWhy this plan:")
    print(scheduler.explain_plan())
    print("\nRecurring task check:")
    next_task = scheduler.mark_task_complete(mochi, completed_task)
    print(f"Completed: {completed_task.title}, due {completed_task.due_date}")
    print(f"Next: {next_task.title}, due {next_task.due_date}, completed={next_task.completed}")
    print(f"Next occurrence count: {sum(task is next_task for task in mochi.tasks)}")


if __name__ == "__main__":
    main()

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
    completed_task.mark_complete()

    scheduler = Scheduler(owner)
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


if __name__ == "__main__":
    main()

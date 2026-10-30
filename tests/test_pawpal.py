"""Phase 2 checks for task completion and adding tasks to pets."""

from pawpal_system import Pet, Task


def test_mark_complete_changes_task_status():
    """Completing a task changes its status from unfinished to finished."""
    task = Task("Feeding", 10, "high")

    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """Adding a task increases the count and preserves the existing task."""
    pet = Pet("Mochi", "cat")
    existing_task = Task("Feeding", 10, "high")
    pet.add_task(existing_task)
    initial_count = len(pet.tasks)
    new_task = Task("Enrichment", 15, "medium")

    pet.add_task(new_task)

    assert len(pet.tasks) == initial_count + 1
    assert existing_task in pet.tasks
    assert new_task in pet.tasks

"""Core behavior and edge-case checks for PawPal+ (run with python -m pytest)."""

from datetime import date, datetime, time, timedelta
import pytest
from pawpal_system import Owner, Pet, Scheduler, Task

DAY = date(2026, 10, 29)


def make_task(title="Feeding", minutes=10, priority="high", **kwargs):
    """Create a task with a fixed date so tests do not depend on today's date."""
    return Task(title, minutes, priority, due_date=DAY, **kwargs)


def make_scheduler(tasks=(), minutes=60):
    """Create a small owner/pet fixture without sharing mutable state."""
    pet = Pet("Mochi", "cat", list(tasks))
    owner = Owner("Jordan", minutes, datetime.combine(DAY, time(8)), pets=[pet])
    return Scheduler(owner), pet


def test_mark_complete_changes_task_status():
    task = make_task()
    assert not task.completed
    task.mark_complete(DAY)
    assert task.completed


def test_add_task_increases_pet_task_count():
    pet = Pet("Mochi", "cat")
    first, second = make_task("Feeding"), make_task("Play")
    pet.add_task(first)
    pet.add_task(second)
    assert pet.tasks == [first, second]


def test_pet_task_lists_are_independent():
    first, second = Pet("First", "cat"), Pet("Second", "dog")
    first.add_task(make_task())
    assert len(first.tasks) == 1
    assert second.tasks == []


def test_sorting_is_chronological_and_keeps_flexible_tasks_last():
    late = make_task("Late", fixed_start_time=time(9))
    flexible = make_task("Flexible")
    early = make_task("Early", fixed_start_time=time(8))
    scheduler, pet = make_scheduler([late, flexible, early])
    assert [task for _, task in scheduler.sort_by_time()] == [early, late, flexible]
    assert pet.tasks == [late, flexible, early]  # Sorting must not change stored order.


def test_sorting_equal_times_is_stable():
    first = make_task("First", fixed_start_time=time(8))
    second = make_task("Second", fixed_start_time=time(8))
    scheduler, _ = make_scheduler([first, second])
    assert [task for _, task in scheduler.sort_by_time()] == [first, second]


def test_empty_pet_has_no_tasks_plan_or_conflicts():
    scheduler, _ = make_scheduler()
    assert scheduler.sort_by_time() == []
    assert scheduler.filter_tasks() == []
    assert scheduler.generate_plan() == []
    assert scheduler.detect_conflicts() == []


def test_filter_combines_pet_name_and_completion_status():
    finished, pending = make_task("Finished"), make_task("Pending")
    finished.mark_complete(DAY)
    scheduler, pet = make_scheduler([finished, pending])
    other = Pet("Biscuit", "dog", [make_task("Walk")])
    scheduler.owner.add_pet(other)
    assert scheduler.filter_tasks(pet_name=" moCHI ", completed=False) == [(pet, pending)]
    assert scheduler.filter_tasks(completed=True) == [(pet, finished)]
    assert scheduler.filter_tasks(pet_name="Unknown") == []


@pytest.mark.parametrize("frequency,days", [("daily", 1), ("weekly", 7)])
def test_recurrence_creates_a_new_attached_occurrence(frequency, days):
    task = make_task("Care", frequency=frequency,
                     weekday=DAY.weekday() if frequency == "weekly" else None,
                     description="Care details", fixed_start_time=time(8, 15))
    scheduler, pet = make_scheduler([task])
    upcoming = scheduler.mark_task_complete(pet, task, DAY)
    assert upcoming is not task
    assert upcoming in pet.tasks and task in pet.tasks
    assert task.completed and not upcoming.completed
    assert upcoming.due_date == DAY + timedelta(days=days)
    assert (upcoming.title, upcoming.description, upcoming.duration_minutes,
            upcoming.priority, upcoming.frequency, upcoming.fixed_start_time) == (
        task.title, task.description, task.duration_minutes,
        task.priority, task.frequency, task.fixed_start_time)
    assert not upcoming.is_due(DAY)
    assert upcoming.is_due(upcoming.due_date)


def test_repeated_completion_does_not_duplicate_next_occurrence():
    task = make_task()
    scheduler, pet = make_scheduler([task])
    upcoming = scheduler.mark_task_complete(pet, task, DAY)
    assert scheduler.mark_task_complete(pet, task, DAY) is upcoming
    assert pet.tasks == [task, upcoming]


def test_one_time_task_does_not_recur():
    task = make_task(frequency="once")
    scheduler, pet = make_scheduler([task])
    assert scheduler.mark_task_complete(pet, task, DAY) is None
    assert task.completed and pet.tasks == [task]


def test_future_task_cannot_be_completed_early():
    future = Task("Future", 10, "high", due_date=DAY + timedelta(days=1))
    scheduler, pet = make_scheduler([future])
    with pytest.raises(ValueError, match="not due"):
        scheduler.mark_task_complete(pet, future, DAY)
    assert not future.completed and pet.tasks == [future]


def test_daily_recurrence_crosses_year_boundary():
    day = date(2026, 12, 31)
    task = Task("Feed", 10, "high", due_date=day)
    upcoming = task.mark_complete(day)
    assert upcoming.due_date == date(2027, 1, 1)


@pytest.mark.parametrize("different_pets", [False, True])
def test_identical_start_times_raise_conflict_warnings(different_pets):
    first = make_task("Bath", fixed_start_time=time(8))
    second = make_task("Walk", fixed_start_time=time(8))
    scheduler, pet = make_scheduler([first])
    if different_pets:
        scheduler.owner.add_pet(Pet("Biscuit", "dog", [second]))
    else:
        pet.add_task(second)
    assert len(scheduler.generate_plan()) == 2
    warnings = scheduler.detect_conflicts()
    assert len(warnings) == 1
    assert "Bath" in warnings[0] and "Walk" in warnings[0]


def test_overlapping_durations_are_detected_with_different_start_times():
    first = make_task("Long", minutes=30, fixed_start_time=time(8))
    second = make_task("Inside", minutes=5, fixed_start_time=time(8, 10))
    scheduler, _ = make_scheduler([second, first])
    scheduler.generate_plan()
    assert len(scheduler.detect_conflicts()) == 1


def test_touching_endpoints_do_not_conflict():
    first = make_task("First", fixed_start_time=time(8))
    second = make_task("Second", fixed_start_time=time(8, 10))
    scheduler, _ = make_scheduler([second, first])
    scheduler.generate_plan()
    assert scheduler.detect_conflicts() == []


def test_flexible_task_fits_exactly_between_fixed_appointments():
    first = make_task("First", fixed_start_time=time(8))
    last = make_task("Last", fixed_start_time=time(8, 20))
    flexible = make_task("Flexible")
    scheduler, _ = make_scheduler([last, flexible, first], minutes=30)
    plan = scheduler.generate_plan()
    assert [task for _, task, _, _ in plan] == [first, flexible, last]
    assert plan[1][2].time() == time(8, 10)
    assert plan[-1][3].time() == time(8, 30)
    assert scheduler.detect_conflicts() == []


def test_oversized_task_does_not_block_a_smaller_task():
    large, small = make_task("Large", minutes=90), make_task("Small", minutes=10)
    scheduler, _ = make_scheduler([large, small], minutes=10)
    assert [task for _, task, _, _ in scheduler.generate_plan()] == [small]


def test_priority_precedes_preference_and_preferences_break_ties():
    low = make_task("Preferred low", priority="low")
    high = make_task("High")
    preferred_high = make_task("Preferred high")
    scheduler, _ = make_scheduler([low, high, preferred_high], minutes=30)
    scheduler.owner.update_preferences(["Preferred low", "Preferred high"])
    assert [task for _, task, _, _ in scheduler.generate_plan()] == [preferred_high, high, low]


def test_zero_budget_produces_no_plan():
    scheduler, _ = make_scheduler([make_task()], minutes=0)
    assert scheduler.generate_plan() == []


def test_completed_future_and_outside_window_tasks_are_excluded():
    done = make_task("Done")
    done.mark_complete(DAY)
    future = Task("Future", 10, "high", due_date=DAY + timedelta(days=1))
    outside = make_task("Outside", fixed_start_time=time(7, 55))
    scheduler, _ = make_scheduler([done, future, outside])
    assert scheduler.generate_plan() == []


def test_regenerating_plan_does_not_duplicate_or_complete_tasks():
    task = make_task()
    scheduler, _ = make_scheduler([task])
    first = scheduler.generate_plan()
    assert scheduler.generate_plan() == first
    first.clear()
    assert len(scheduler.schedule) == 1
    assert not task.completed


@pytest.mark.parametrize("minutes", [0, -1, 1.5, True])
def test_invalid_task_durations_are_rejected(minutes):
    with pytest.raises(ValueError):
        make_task(minutes=minutes)

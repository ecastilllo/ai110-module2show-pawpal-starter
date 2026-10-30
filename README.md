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

Captured from the Phase 4 CLI demo. Dates follow the day the demo is run. The overlapping appointments are intentional, to demonstrate warnings.

```text
Tasks sorted by fixed time (automatic tasks last):
08:00 | Mochi: Breakfast appointment | due 2026-10-29 | completed=False
08:15 | Biscuit: Bath | due 2026-10-29 | completed=False
Automatic | Biscuit: Morning walk | due 2026-10-29 | completed=False
Automatic | Biscuit: Grooming | due 2026-10-29 | completed=False
Automatic | Mochi: Feeding | due 2026-10-29 | completed=False
Automatic | Mochi: Enrichment | due 2026-10-29 | completed=False
Automatic | Mochi: Restock food | due 2026-10-29 | completed=False
Automatic | Mochi: Refresh water | due 2026-10-29 | completed=True
Automatic | Mochi: Refresh water | due 2026-10-30 | completed=False

Incomplete tasks for Mochi:
- Mochi: Feeding | due 2026-10-29
- Mochi: Enrichment | due 2026-10-29
- Mochi: Restock food | due 2026-10-29
- Mochi: Refresh water | due 2026-10-30
- Mochi: Breakfast appointment | due 2026-10-29

Today's Schedule - 2026-10-29
Owner: Jordan | Available time: 45 minutes

08:00-08:20 | Mochi (cat) | Breakfast appointment (20 min) [priority: high, frequency: daily]
08:15-08:30 | Biscuit (dog) | Bath (15 min) [priority: medium, frequency: daily]
08:30-08:40 | Mochi (cat) | Feeding (10 min) [priority: high, frequency: daily]

Why this plan:
Fixed times are reserved first. Flexible tasks use priority, then preferred titles, then pet/task entry order.
Skipped Mochi: Refresh water: already completed.
Skipped Mochi: Refresh water: not due on 2026-10-29.
Reserved Mochi: Breakfast appointment at 08:00.
Reserved Biscuit: Bath at 08:15.
Selected Mochi: Feeding: high priority; fits an available gap.
Skipped Biscuit: Morning walk: no 25-minute gap remains.
Skipped Mochi: Enrichment: no 10-minute gap remains.
Skipped Biscuit: Grooming: no 20-minute gap remains.
Skipped Mochi: Restock food: no 15-minute gap remains.
Conflict: Mochi: Breakfast appointment (08:00-08:20) overlaps Biscuit: Bath (08:15-08:30).
Resolve the overlapping fixed times before following this plan.
Reserved clock time: 40/45 min.

Recurring task check:
Completed: Refresh water, due 2026-10-29
Next: Refresh water, due 2026-10-30, completed=False
Next occurrence count: 1
```

## 🧪 Testing PawPal+

Run the automated suite from the repository folder:

```powershell
# Windows
py -m pip install pytest
py -m pytest
```

The equivalent command when Python is available as `python` is `python -m pytest`.
Optional coverage requires installing `pytest-cov` before running `python -m pytest --cov=pawpal_system`.

The 27 tests cover five core behaviors:

- Chronological sorting, equal-time ordering, and flexible tasks placed last.
- Filtering by pet and completion status, including unknown pets and empty lists.
- Daily and weekly recurrence, one-time completion, duplicate prevention, future dates, and year-end rollover.
- Conflict detection for identical starts and overlapping durations across pets, while allowing adjacent tasks.
- Scheduling within available time, exact gap fits, priorities/preferences, zero budgets, oversized tasks, and repeated generation.

The suite also checks task addition, independent pet task lists, completion status, and invalid durations. Fixed dates keep algorithm tests independent of the day they run.

Successful run from the project folder on Windows:

```text
========================== test session starts ===========================
platform win32 -- Python 3.11.3, pytest-9.2.0, pluggy-1.7.0
plugins: anyio-4.15.1
collected 27 items

tests\test_pawpal.py ...........................                    [100%]

=========================== 27 passed in 0.06s ===========================
```

**Confidence level: 4/5 stars (★★★★☆).** The tested core behaviors pass, and the browser's basic pet, task, schedule, and completion flows were checked manually. This is not exhaustive verification: automated browser tests, large task collections, overnight windows, and time-zone/daylight-saving scenarios remain to be tested. Data remains session-only; saving across restarts is not implemented.

## 📐 Smarter Scheduling

| Feature | Method(s) | Behavior |
|---------|-----------|----------|
| Time sorting | `Scheduler.sort_by_time()` | Sorts pet/task pairs by optional fixed clock time; automatic tasks come last. Uses Python time objects and stable `sorted()`. |
| Filtering | `Scheduler.filter_tasks()` | Filters by case-insensitive pet name, completion status, or both. Defaults to the planning date. Incomplete tasks may include future occurrences. |
| Planning | `Scheduler.generate_plan()` | Reserves fixed appointments inside the planning window first, then places flexible tasks in gaps using priority and preferences. |
| Conflict detection | `Scheduler.detect_conflicts()` | Warns about overlapping durations across the same or different pets. Adjacent intervals are allowed. Conflicting fixed tasks stay visible for the owner to resolve. |
| Recurrence | `Task.mark_complete()`, `Scheduler.mark_task_complete()` | Creates and attaches a new task for completion date +1 day (daily) or +7 days (weekly). One-time tasks do not repeat. Duplicate completion does not add another copy. |

Each task is an individual occurrence with a due date. Unfinished overdue occurrences remain eligible. Completing a late weekly task shifts the next occurrence to seven days after completion. Copies retain the title, description, duration, priority, frequency, and fixed time.

Use `Scheduler.mark_task_complete(pet, task)` in the UI and CLI: it both completes the occurrence and adds the returned next task to the pet. Calling `Task.mark_complete()` alone returns the new task but does not attach it.

Conflict detection keeps explicit loops for readability and stops the inner loop once later start times cannot overlap. Its worst-case cost is O(n²), which is acceptable for a small daily schedule. Time sorting is O(n log n), and filtering is O(n). Warnings do not automatically resolve conflicts. Reserved clock time counts the union of occupied intervals, so overlaps are counted only once.

## 📸 Demo Walkthrough

1. Open a terminal in the repository folder with Python 3.10 or newer available.
2. Run `py main.py` on Windows, or `python main.py` on other platforms.
3. The demo creates two pets, adds fixed tasks out of order, and completes a daily water task to create its next occurrence.
4. Read the time-sorted list, incomplete-task filter, intentional conflict warning, and next-occurrence check.
5. Run `py -m pytest` to run all 27 automated checks.

For the browser app, run `py -m streamlit run app.py`. Add pets and tasks, optionally set fixed times, generate a plan, and mark tasks complete. The Owner object is stored in Streamlit session state between interactions. All data is in memory; restarting or reloading the session may reset it.

# PawPal+

PawPal+ is a Streamlit pet-care planner with a Python backend and a terminal demo. It helps an owner organize care across multiple pets, assign clock times, and see why tasks were selected or skipped.

## Features

- Manage multiple pets and their individual care tasks.
- Add tasks with descriptions, durations, priorities, due dates, and optional fixed times.
- Edit an unfinished occurrence's title, duration, priority, and fixed time.
- View tasks sorted by fixed time and filter the list by pet name or completion status.
- Reserve fixed appointments and place flexible tasks into remaining gaps.
- Display warnings for overlapping appointments, including appointments for different pets.
- Mark tasks complete and create the next daily or weekly occurrence without duplicates.
- Retain data during Streamlit interactions using session state.
- Verify the backend with 27 automated tests.

## Setup and run

Requires Python 3.10 or newer. From the repository folder on Windows:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open the local URL printed in the terminal. Stop the server with Ctrl+C.

For macOS/Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

If using an existing environment on Windows, run `py -m pip install -r requirements.txt`, then `py -m streamlit run app.py`. The CLI demo runs with `py main.py` (or the virtual environment's Python executable).

## Architecture

- `pawpal_system.py`: Owner, Pet, Task, and Scheduler classes.
- `app.py`: Streamlit forms, session state, filtered tables, and conflict warnings.
- `main.py`: repeatable terminal demonstration.
- `tests/test_pawpal.py`: automated backend checks.
- [Final UML source](diagrams/uml_final.mmd): final public class attributes, methods, and relationships.
- [Reflection](reflection.md): design decisions, tradeoffs, testing, and AI collaboration.

An Owner contains Pets, each Pet holds Task occurrences, and the Scheduler gathers those tasks to build and explain a plan. Completing a recurring Task produces a new occurrence, which the Scheduler attaches to the correct Pet.

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

## Demo Walkthrough

1. Launch the browser app and save the owner's name, planning date, start time, available minutes, and optional preferred task titles.
2. Add a pet, such as Moosh Moosh. Add another pet to demonstrate planning across pets.
3. Add a daily Feeding task lasting 10 minutes. For weekly tasks, choose a first due date that matches the selected weekday.
4. Use the pet-name and completion filters to narrow the task list. The list is sorted by fixed clock time, with automatic tasks last; filters do not change which tasks the planner considers.
5. Generate a schedule. Fixed appointments are reserved first; flexible tasks use priority and preferences to fit into gaps.
6. Add two fixed tasks that overlap, such as an 08:00–08:20 feeding and an 08:10–08:20 bath. Generate again to see named warnings with both time ranges.
7. Open **Edit a task or resolve a time conflict**, move the bath to 08:20, save, and regenerate. Adjacent appointments do not overlap.
8. Mark a daily task complete for the saved planning date. The completed occurrence stays visible, and a new unfinished occurrence appears with the following day's due date.
9. Open **Why this plan?** to see selection, skipping, and conflict explanations.
10. Run `py main.py` for the CLI demonstration shown above, or `py -m pytest` for the 27 backend checks.

## Current limits

Data is kept in memory. Reloading the browser or restarting the app can reset the session. Fixed-time conflicts are reported, not automatically resolved. Occurrence editing does not change an entire recurrence series. Filtering by a pet name includes all pets with that same name. Overnight and time-zone/daylight-saving scenarios are not yet verified.

The Phase 6 UI passed Python syntax validation. Automated Streamlit interaction checks could not start in the agent environment because local socket initialization stalled; manual verification of the new filters and edit form is pending. The 27 backend tests are separate from UI verification.

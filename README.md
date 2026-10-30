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

Captured from running `py main.py` on Windows. The demo uses the current date when run.

```text
Today's Schedule - 2026-10-29
Owner: Jordan | Available time: 45 minutes

08:00-08:10 | Mochi (cat) | Feeding (10 min) [priority: high, frequency: daily]
08:10-08:35 | Biscuit (dog) | Morning walk (25 min) [priority: high, frequency: daily]
08:35-08:45 | Mochi (cat) | Enrichment (10 min) [priority: medium, frequency: daily]

Why this plan:
Tasks are considered by priority (high to low), then preferred titles; other ties keep pet/task entry order.
Skipped Mochi: Refresh water: already completed.
Selected Mochi: Feeding: high priority; preferred title; 10 min fits the remaining time.
Selected Biscuit: Morning walk: high priority; 25 min fits the remaining time.
Selected Mochi: Enrichment: medium priority; 10 min fits the remaining time.
Skipped Biscuit: Grooming: needs 20 min; only 0 min remain.
Skipped Mochi: Restock food: needs 15 min; only 0 min remain.
Time used: 45/45 min; 0 min remaining.
```

## 🧪 Testing PawPal+

```powershell
# Windows: install and run the initial tests
py -m pip install pytest
py -m pytest
```

On other platforms, use `python -m pytest`. Optional coverage requires installing `pytest-cov` before running `python -m pytest --cov=pawpal_system`.

Verified on Windows with Python 3.11.3 and pytest 9.2.0. The two initial tests cover task completion and adding a task to a pet.

```text
collected 2 items

tests\test_pawpal.py ..                                             [100%]

=========================== 2 passed in 0.01s ============================
```

These initial tests do not exhaustively verify the scheduler's recurrence and time-budget behavior.

## 📐 Smarter Scheduling

The core scheduler is implemented and exercised by the terminal demo.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.generate_plan()` | High priority first; preferred titles break ties, then pet/task entry order. |
| Filtering | `Task.is_due()`, `Task.is_completed()`, `Scheduler.generate_plan()` | Skip completed, not-due, or oversized tasks; continue considering smaller tasks. |
| Conflict handling | `Scheduler.generate_plan()` | Place tasks consecutively from the owner's start time within the minute budget. Fixed appointment times are not supported. |
| Recurring tasks | `Task.is_due()`, `Task.mark_complete()` | Daily, weekly on a selected weekday, or one-time. Completion is tracked by date; overdue one-time tasks remain due. |

## 📸 Demo Walkthrough

1. Open a terminal in the repository folder with Python 3.10 or newer available.
2. Run `py main.py` on Windows, or `python main.py` on other platforms.
3. The demo creates Jordan, Biscuit, and Mochi, adds six care tasks, and marks the water task complete.
4. Read the timed schedule and the reasons for including or skipping each task.
5. Run `py -m pytest` to check completion and task addition.

Phase 2 uses the terminal. All data is in memory and the demo starts fresh each run; the Streamlit interface will be connected in a later phase.

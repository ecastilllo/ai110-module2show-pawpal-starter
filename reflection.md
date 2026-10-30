# PawPal+ Project Reflection

## 1. System Design

**Three core user actions**

1. Add owner and pet information so care tasks can be associated with the correct pet.
2. Add or edit pet care tasks, including a title, duration in minutes, and priority (low, medium, or high).
3. Generate and view today's care plan with actual start and end times, based on the owner's planning start time, available minutes, and task priorities, with an explanation of the selections.

**a. Initial design**

The initial design uses four classes. Owner stores the owner's name, available minutes, planning start date and time, preferred task titles, and pets. Pet stores a pet's name, species, and care tasks. Task stores a care activity's title, duration in minutes, and priority (low, medium, or high). Scheduler uses the owner's time window and the pets' tasks to build and explain a daily plan.

An owner can have multiple pets, and each task instance belongs to one pet. Pet and Task use Python dataclasses, with a separate task list for each pet. The Mermaid blueprint is saved in `diagrams/uml.mmd`; matching class skeletons are in `pawpal_system.py`.

Each schedule entry will retain the pet, task, start datetime, and end datetime. The scheduler is intended to select higher-priority tasks first, use preferred task titles to break equal-priority ties, and place selected tasks consecutively within the available time. The behavior methods are empty in Phase 1.

**b. Design changes**

During the Phase 1 design review, the first draft returned only an ordered list of tasks. After comparing that approach with the README's sample clock times, we revised the design to include a planning start datetime and start/end datetimes for each scheduled task. This makes the plan easier to follow and supports checking for overlaps.

The AI review also identified that a schedule covering multiple pets must preserve which pet each task is for. Each schedule entry therefore includes the pet along with the task and its times. This keeps the four-class design while making the output unambiguous.

These are design-stage refinements; scheduling logic has not been implemented or tested yet.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

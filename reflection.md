# PawPal+ Project Reflection

## 1. System Design

**Three core user actions**

1. Add owner and pet information so care tasks can be associated with the correct pet.
2. Add or edit pet care tasks, including a title, duration in minutes, and priority (low, medium, or high).
3. Generate and view today's care plan with actual start and end times, based on the owner's planning start time, available minutes, and task priorities, with an explanation of the selections.

**a. Initial design**

My initial design has four classes: Owner, Pet, Task, and Scheduler. Owner holds the owner's name, pets, preferences, and the time they have available for pet care, including when they want to start. Pet holds the pet's name, species, and care tasks. Task holds the details of each activity, like feeding or walking, including how long it takes and its priority.

The Scheduler's job is to take those tasks and organize them into a plan that fits the owner's available time. It will decide which tasks can fit, give them actual start and end times, and explain why they were included or left out. Higher-priority tasks will come first, and the owner's preferences will help decide between tasks with the same priority.

An owner can have more than one pet, so each pet has its own tasks. Pet and Task use Python dataclasses to keep the code simple. The UML diagram is saved in `diagrams/uml.mmd`, and the matching class skeletons are in `pawpal_system.py`. At the end of Phase 1, the classes had their attributes and empty methods. The scheduling logic was added in later phases.

**b. Design changes**

The first draft was going to create an ordered list of tasks. After discussing that option with AI and looking at the README's sample output, I chose to use actual times. I prefer a schedule with actual times because it adds a layer of organization that is needed for this pet service. I think of dogs as creatures of routine, so a set schedule would be more useful for keeping their care consistent.

To support this, we added a starting date and time to Owner and start and end times to each entry in the schedule. The plan is for tasks to run one after another so they do not overlap or go beyond the owner's available time.

During the AI review, we also made sure each scheduled task keeps track of which pet it belongs to. This matters if an owner has multiple pets, since a task like feeding needs to show which pet it is for. These changes were made during the design stage. At that stage, I had checked Python syntax, but the scheduling methods were still empty. Since then, I ran the CLI demo, checked the browser interactions, and confirmed the two initial pytest tests passed.

In Phase 4, we added optional fixed start times, pet/status filters, and overlap warnings. We also changed recurrence from reusing one task to keeping the completed occurrence and creating a separate next occurrence. This makes the due dates and completion history easier to distinguish.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

My scheduler considers the planning date, available time, fixed appointments, task duration, completion status, priority, and owner preferences. Fixed appointments are reserved first, and flexible tasks are placed in the remaining gaps. Higher-priority flexible tasks come first, with preferences used to break ties. This keeps the plan organized around the time the owner actually has available.

**b. Tradeoffs**

One tradeoff is that the scheduler warns about overlapping fixed appointments instead of automatically changing their times. I want the owner to see the problem and decide what to move, since a fixed time may be important for the pet's routine. The schedule still displays those appointments, so a warning means the owner needs to resolve the overlap before following the plan.

I also compared the conflict-detection loops with a shorter list comprehension suggested by AI. I chose to keep the explicit loops because they are easier to follow and can stop checking once later tasks cannot overlap. They can still compare every pair in the worst case, but that is reasonable for a small pet-care schedule. I would rather understand the code than make it shorter just for the sake of it.

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

With AI's help, I expanded the test suite to 27 checks and ran it in my VS Code terminal. All 27 passed. The tests cover time sorting, filtering by pet and completion status, recurring tasks, overlapping appointments, and fitting tasks into the available time.

I also checked cases that could easily cause problems, like a pet with no tasks, two tasks starting at the same time, a task that is too long, and completing the same task twice. The recurrence tests check that a new task is created for the correct date without duplicating it. These checks matter because an organized schedule is only useful if its times and task statuses are reliable.

**b. Confidence**

Based on these results, I would rate confidence in the core system at 4 out of 5 stars. The automated tests passed, and I also checked the basic app actions in the browser. That gives me evidence that the main features work together, but passing these tests does not mean every possible situation has been covered.

With more time, I would test larger task lists, schedules that cross midnight, and time-zone or daylight-saving changes. I would also add automated browser tests so the forms and session memory are checked along with the Python logic.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

# PawPal+ Project Reflection

## 1. System Design

**Three core user actions**

1. Add owner and pet information so care tasks can be associated with the correct pet.
2. Add or edit pet care tasks, including a title, duration in minutes, and priority (low, medium, or high).
3. Generate and view today's care plan with actual start and end times, based on the owner's planning start time, available minutes, and task priorities, with an explanation of the selections.

**a. Initial design**

My initial design has four classes: Owner, Pet, Task, and Scheduler. Owner holds the owner's name, pets, preferences, and the time they have available for pet care, including when they want to start. Pet holds the pet's name, species, and care tasks. Task holds the details of each activity, like feeding or walking, including how long it takes and its priority.

The Scheduler's job is to take those tasks and organize them into a plan that fits the owner's available time. It will decide which tasks can fit, give them actual start and end times, and explain why they were included or left out. Higher-priority tasks will come first, and the owner's preferences will help decide between tasks with the same priority.

An owner can have more than one pet, so each pet has its own tasks. Pet and Task use Python dataclasses to keep the code simple. The UML diagram is saved in `diagrams/uml.mmd`, and the matching class skeletons are in `pawpal_system.py`. At this point, the classes have their attributes and empty methods. The scheduling logic comes next.

**b. Design changes**

The first draft was going to create an ordered list of tasks. After discussing that option with AI and looking at the README's sample output, I chose to use actual times. I prefer a schedule with actual times because it adds a layer of organization that is needed for this pet service. I think of dogs as creatures of routine, so a set schedule would be more useful for keeping their care consistent.

To support this, we added a starting date and time to Owner and start and end times to each entry in the schedule. The plan is for tasks to run one after another so they do not overlap or go beyond the owner's available time.

During the AI review, we also made sure each scheduled task keeps track of which pet it belongs to. This matters if an owner has multiple pets, since a task like feeding needs to show which pet it is for. These changes were made during the design stage. I have checked the Python file for syntax errors, but the scheduling methods are still empty, so the scheduling behavior has not been tested yet.

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

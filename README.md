# Designing-an-Intelligent-Timetabling-System

# Introduction
Timetabling is a complex scheduling problem where multiple constraints must be satisfied
simultaneously. In this assignment, an intelligent timetabling system is developed to
generate an optimal timetable for the Department of Computer Engineering. The system
uses constraint-based modeling combined with a Simulated Annealing optimization
approach to produce a feasible and near-optimal solution.

# Personalized Parameter Derivation
The parameters for this system are derived from my registration number 2022/E/042.
• A = 2 (last digit)
• B = 4 (second last digit)
• C = 0 → replaced by 1
Using these values:
• Number of Courses = 8 + (2 mod 3) = 10
• Number of Lecturers = 5 + (4 mod 2) = 5
• Time slots per day = 4 + (1 mod 2) = 5
These parameters were used throughout the implementation.

# Knowledge Base Representation
To model the system logically, the following predicates are defined:
• Course(c) → c is a course
• Lecturer(l) → l is a lecturer
• Room(r) → r is a classroom
• Day(d) → d is a working day
• Slot(s) → s is a time slot
• Assigned(c, r, d, s) → course c is scheduled in room r on day d at slot s
• Teaches(l, c) → lecturer l teaches course c
• Group(c, g) → course c belongs to student group g
• Lab(c) → c is a lab session
These predicates form the basis for expressing constraints.

# Hard Constraints
The following hard constraints must always be satisfied.
HC1: No resource conflicts
A lecturer, room, or student group cannot be assigned to more than one course at the same
time.
∀c1, c2, d, s:
If Assigned(c1, r1, d, s) and Assigned(c2, r2, d, s) and they share the same lecturer or
group, then c1 = c2
HC2: Special room and day restriction
Course C1 must be conducted in room R1 and only on Tuesday or Thursday.
Assigned(C1, r, d, s) → (r = R1 ∧ d ∈ {Tue, Thu})
HC3: Course ordering
Course C2 must be scheduled immediately after C3 on the same day.
Assigned(C3, r1, d, s) → Assigned(C2, r2, d, s+1)
HC4: Lecturer availability
Lecturer L4 is not available on Friday during slots 4 and 5.
Assigned(c, r, Fri, s) ∧ Teaches(L4, c) → s ≠ 4,5

# Soft Constraints
Unlike hard constraints, soft constraints can be violated but are minimized.
SC1: Lecturer Compactness (Penalty = 7 [5+2])
Lecturers prefer to have consecutive classes instead of spread-out schedules.
SC1 = Σ (spread of slots − number of assigned slots)
SC2: Free slot before lab (Penalty = 7[3+4])
Students should ideally have a free slot before a lab session.
SC2 = Number of lab sessions where the previous slot is occupied
SC3: Room Balancing (Penalty = 3[2+1])
Room usage should be evenly distributed.
SC3 = Variance of room usage

# Heuristic Function
The quality of a timetable is evaluated using:
H = (HC × K) +( SC1 × 7) +( SC2 × 7) +( SC3 × 3)
Where K = 1000.
This ensures that hard constraints are always prioritized over soft constraints.

# Simulated Annealing Approach
Simulated Annealing is used to search for an optimal timetable.
The reason for selecting this method is that the timetable problem has a large and complex
search space with many local minima. A simple local search algorithm can easily get
stuck, but Simulated Annealing allows occasional acceptance of worse solutions to
escape these local minima.
The acceptance probability is given by:
P = e((current − new)/T)
Parameter Settings
• Initial temperature = 100
• Cooling rate = 0.999
• Termination when temperature < 0.01 or maximum iterations reached
These values were chosen to allow sufficient exploration at the beginning and gradual
convergence.

# Hard Constraint Verification
The final solution satisfies all hard constraints:
• No lecturer conflicts
• No room conflicts
• No group conflicts
• Course C1 is scheduled only on Tuesday and Thursday in room R1
• Course C2 follows C3 correctly
• Lecturer L4 is not assigned on Friday afternoon
Therefore:
HC violations = 0

# Score Analysis
The final score obtained is:
Final Score = 20
Breakdown:
• HC = 0 → 0 × 1000 = 0
• SC1 = 0 → 0 × 7 = 0
• SC2 = 2 → 2 × 7 = 14
• SC3 = 2 → 2 × 3 = 6
Total = 20

# Discussion
The system successfully minimized lecturer spread (SC1 = 0), which indicates efficient
scheduling. A small number of violations exist in SC2 and SC3, which is acceptable since
soft constraints are not strictly enforced. The result demonstrates a good balance between
feasibility and optimization.

# Critical Analysis
One limitation of this approach is that it assumes a static environment. In real-world
scenarios, timetables may need to be updated frequently due to changes such as lecturer
availability or room issues.

# Conclusion
This assignment successfully demonstrates the use of constraint-based modeling and
Simulated Annealing for solving a complex timetabling problem. The system produces a
valid timetable that satisfies all hard constraints and minimizes soft constraint violations
effectively.

# References
 Russell, S., & Norvig, P. Artificial Intelligence: A Modern Approach
 Wikipedia – Simulated Annealing

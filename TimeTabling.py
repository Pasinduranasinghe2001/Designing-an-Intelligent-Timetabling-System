# G.D.P.D RANASINGHE
# 2022/E/042

import random
import math
import copy
import tkinter as tk
from tkinter import ttk, messagebox

# Personalized Parameters for 2022/E/042
# A=2, B=4, C=1
COURSES = [f"C{i+1}" for i in range(10)]
LECTURERS = [f"L{i+1}" for i in range(5)]
ROOMS = ["R1", "R2", "R3"] # R1 is specialized
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]
SLOTS = [1, 2, 3, 4, 5]

# Course assignments (Lecturer, YearGroup, isLab)
COURSE_INFO = {
    "C1": {"lecturer": "L1", "group": "G1", "isLab": True},  # Specialized
    "C2": {"lecturer": "L2", "group": "G1", "isLab": True},  # Follows C3
    "C3": {"lecturer": "L2", "group": "G1", "isLab": False},
    "C4": {"lecturer": "L3", "group": "G2", "isLab": False},
    "C5": {"lecturer": "L3", "group": "G2", "isLab": False},
    "C6": {"lecturer": "L4", "group": "G3", "isLab": False},
    "C7": {"lecturer": "L4", "group": "G3", "isLab": False},
    "C8": {"lecturer": "L5", "group": "G1", "isLab": False},
    "C9": {"lecturer": "L5", "group": "G2", "isLab": False},
    "C10": {"lecturer": "L1", "group": "G3", "isLab": False},
}

# Each course needs 2 slots per week
COURSE_SLOTS = {c: 2 for c in COURSES}

# Penalties
PENALTY_HC = 1000
PENALTY_SC1 = 7  # 5 + A
PENALTY_SC2 = 7  # 3 + B
PENALTY_SC3 = 3  # 2 + C

class Timetable:
    def __init__(self):
        self.schedule = [] # List of (course, room, day, slot)

    def randomize(self):
        self.schedule = []
        for course, num_slots in COURSE_SLOTS.items():
            for _ in range(num_slots):
                room = random.choice(ROOMS)
                day = random.choice(DAYS)
                slot = random.choice(SLOTS)
                self.schedule.append({"course": course, "room": room, "day": day, "slot": slot})

    def get_violations(self):
        hc_violations = 0
        sc1_violations = 0 # Lecturer compactness
        sc2_violations = 0 # Student free slot before lab
        sc3_violations = 0 # Room balancing

        # HC1: Single Assignment
        # Lecturer conflicts
        lecturer_slots = {}
        # Room conflicts
        room_slots = {}
        # Group conflicts
        group_slots = {}

        for entry in self.schedule:
            c = entry["course"]
            r = entry["room"]
            d = entry["day"]
            s = entry["slot"]
            l = COURSE_INFO[c]["lecturer"]
            g = COURSE_INFO[c]["group"]

            # Key for unique check
            time_key = (d, s)
            
            # Lecturer check
            l_key = (l, d, s)
            if l_key in lecturer_slots: hc_violations += 1
            lecturer_slots[l_key] = c

            # Room check
            r_key = (r, d, s)
            if r_key in room_slots: hc_violations += 1
            room_slots[r_key] = c

            # Group check
            g_key = (g, d, s)
            if g_key in group_slots: hc_violations += 1
            group_slots[g_key] = c

            # HC2: C1 specialized room R1 on Tue/Thu
            if c == "C1":
                if r != "R1" or d not in ["Tue", "Thu"]:
                    hc_violations += 1

            # HC4: L4 unavailable on Fri afternoon (4, 5)
            if l == "L4" and d == "Fri" and s in [4, 5]:
                hc_violations += 1

        # HC3: C2 must follow C3 on same day
        for d in DAYS:
            c3_slots = [e["slot"] for e in self.schedule if e["course"] == "C3" and e["day"] == d]
            c2_slots = [e["slot"] for e in self.schedule if e["course"] == "C2" and e["day"] == d]
            for s3 in c3_slots:
                if (s3 + 1) not in c2_slots:
                    hc_violations += 1

        # SC1: Lecturer Compactness
        # For each lecturer on each day, count the range of slots vs number of slots
        for l in LECTURERS:
            for d in DAYS:
                l_day_slots = sorted([e["slot"] for e in self.schedule if COURSE_INFO[e["course"]]["lecturer"] == l and e["day"] == d])
                if len(l_day_slots) > 1:
                    spread = l_day_slots[-1] - l_day_slots[0] + 1
                    if spread > len(l_day_slots):
                        sc1_violations += (spread - len(l_day_slots))

        # SC2: Free slot before Lab
        # Maximize free slots immediately before a lab slot
        for entry in self.schedule:
            if COURSE_INFO[entry["course"]]["isLab"]:
                d = entry["day"]
                s = entry["slot"]
                g = COURSE_INFO[entry["course"]]["group"]
                if s > 1:
                    # Check if group has a slot at s-1
                    prev_slot_busy = any(e["day"] == d and e["slot"] == s-1 and COURSE_INFO[e["course"]]["group"] == g for e in self.schedule)
                    if prev_slot_busy:
                        sc2_violations += 1
                else:
                    # Slot 1 lab has no "immediately before" free slot in the same day context usually, let's count it as violation for maximizing
                    sc2_violations += 1

        # SC3: Room Balancing
        room_counts = {r: 0 for r in ROOMS}
        for entry in self.schedule:
            room_counts[entry["room"]] += 1
        
        counts = list(room_counts.values())
        avg = sum(counts) / len(counts)
        variance = sum((x - avg) ** 2 for x in counts) / len(counts)
        sc3_violations = int(variance * 10) # Weighted to contribute

        return hc_violations, sc1_violations, sc2_violations, sc3_violations

    def get_score(self):
        hc, sc1, sc2, sc3 = self.get_violations()
        return hc * PENALTY_HC + sc1 * PENALTY_SC1 + sc2 * PENALTY_SC2 + sc3 * PENALTY_SC3

def simulated_annealing():
    current_tt = Timetable()
    current_tt.randomize()
    current_score = current_tt.get_score()
    
    best_tt = copy.deepcopy(current_tt)
    best_score = current_score

    t = 100.0
    cooling_rate = 0.999
    
    for i in range(10000):
        new_tt = copy.deepcopy(current_tt)
        # Tweak: Move one course assignment
        idx = random.randrange(len(new_tt.schedule))
        new_tt.schedule[idx]["room"] = random.choice(ROOMS)
        new_tt.schedule[idx]["day"] = random.choice(DAYS)
        new_tt.schedule[idx]["slot"] = random.choice(SLOTS)
        
        new_score = new_tt.get_score()
        
        if new_score < current_score or random.random() < math.exp((current_score - new_score) / t):
            current_tt = new_tt
            current_score = new_score
            if current_score < best_score:
                best_tt = copy.deepcopy(current_tt)
                best_score = current_score
        
        t *= cooling_rate
        if t < 0.01: break
        
    return best_tt, best_score

class TimetableGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Timetable Optimization - 2022/E/042")
        self.root.geometry("900x600")

        # Style configuration
        style = ttk.Style()
        style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'))

        # Main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Control Panel
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.pack(fill=tk.X, pady=5)

        self.run_btn = ttk.Button(control_frame, text="Run Optimization", command=self.run_optimization)
        self.run_btn.pack(side=tk.LEFT, padx=5)

        self.score_label = ttk.Label(control_frame, text="Current Score: N/A")
        self.score_label.pack(side=tk.LEFT, padx=20)

        # Table for Timetable
        table_frame = ttk.LabelFrame(main_frame, text="Optimized Timetable", padding="10")
        table_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        columns = ("Day", "Slot", "Course", "Lecturer", "Room")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Violation breakdown
        violations_frame = ttk.LabelFrame(main_frame, text="Violations Breakdown", padding="10")
        violations_frame.pack(fill=tk.X, pady=5)

        self.hc_label = ttk.Label(violations_frame, text="HC: -")
        self.hc_label.pack(side=tk.LEFT, padx=10)
        self.sc1_label = ttk.Label(violations_frame, text="SC1: -")
        self.sc1_label.pack(side=tk.LEFT, padx=10)
        self.sc2_label = ttk.Label(violations_frame, text="SC2: -")
        self.sc2_label.pack(side=tk.LEFT, padx=10)
        self.sc3_label = ttk.Label(violations_frame, text="SC3: -")
        self.sc3_label.pack(side=tk.LEFT, padx=10)

    def run_optimization(self):
        self.run_btn.config(state=tk.DISABLED)
        self.root.update()
        
        try:
            best_tt, score = simulated_annealing()
            hc, sc1, sc2, sc3 = best_tt.get_violations()
            
            # Update labels
            self.score_label.config(text=f"Final Score: {score}")
            self.hc_label.config(text=f"HC: {hc}")
            self.sc1_label.config(text=f"SC1: {sc1}")
            self.sc2_label.config(text=f"SC2: {sc2}")
            self.sc3_label.config(text=f"SC3: {sc3}")

            # Clear and update table
            for item in self.tree.get_children():
                self.tree.delete(item)

            for day in DAYS:
                day_entries = [e for e in best_tt.schedule if e["day"] == day]
                day_entries.sort(key=lambda x: x["slot"])
                for e in day_entries:
                    self.tree.insert("", tk.END, values=(
                        e['day'], 
                        e['slot'], 
                        e['course'], 
                        COURSE_INFO[e['course']]['lecturer'], 
                        e['room']
                    ))
            
            messagebox.showinfo("Success", "Optimization Complete!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            self.run_btn.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = TimetableGUI(root)
    root.mainloop()

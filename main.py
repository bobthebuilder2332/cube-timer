import tkinter as tk
import random
import time
import json
import os

class CubeTimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Speedcube Timer")
        self.root.geometry('1200x750')
        self.root.configure(bg='#1e1e1e')

        self.timer_running = False
        self.start_time = 0
        self.press_start_time = 0
        self.timer_state = 'idle' # idle, holding, ready, running
        self.release_timer_id = None

        self.last_solve = -1
        self.fastest_solve = -1
        self.mo3 = -1
        self.ao3 = -1
        self.ao12 = -1

        self.solves = []
        self.current_scramble = ""

        self.load_data()

        self.title_label = tk.Label(root, text="Speedcubing Timer and Stats", font=('Arial', 20, 'bold'), bg='#1e1e1e', fg='white')
        self.title_label.pack(pady=20)

        self.scramble_label = tk.Label(root, text="Generating scramble...", font=('Courier', 14), justify='center', bg='#1e1e1e', fg='white')
        self.scramble_label.pack(pady=10)

        self.timer_label = tk.Label(root, text="0.00", font=('Arial', 48, 'bold'), bg='#1e1e1e', fg='white')
        self.timer_label.pack(pady=20)

        self.pb_label = tk.Label(root, text=f"Fastest Solve: {self.fastest_solve if self.fastest_solve != -1 else 'N/A'}", font=('Arial', 14), bg='#1e1e1e', fg='white')
        self.pb_label.pack(pady=5)

        self.mo3_label = tk.Label(root, text=f"Mo3: {self.mo3 if self.mo3 != -1 else 'N/A'}", font=('Arial', 14), bg='#1e1e1e', fg='white')
        self.mo3_label.pack(pady=5)

        self.ao3_label = tk.Label(root, text=f"Ao3: {self.ao3 if self.ao3 != -1 else 'N/A'}", font=('Arial', 14), bg='#1e1e1e', fg='white')
        self.ao3_label.pack(pady=5)

        self.ao12_label = tk.Label(root, text=f"Ao12: {self.ao12 if self.ao12 != -1 else 'N/A'}", font=('Arial', 14), bg='#1e1e1e', fg='white')
        self.ao12_label.pack(pady=5)

        self.history_button = tk.Button(root, text="View History", font=('Arial', 12), bg='#333333', fg='#1e1e1e', command=self.open_history_window)
        self.history_button.pack(pady=5)

        self.history_win = None
        self.history_text_area = None

        self.root.bind('<KeyPress-space>', self.on_space_press)
        self.root.bind('<KeyRelease-space>', self.on_space_release)
        self.root.bind('<Escape>', self.on_escape)
        self.root.bind('<r>', self.new_scramble)

        self.new_scramble()

        self.update_stats_display()

    # Attempts to load data from data.json
    def load_data(self):
        if os.path.exists('data.json'):
            try:
                with open('data.json', 'r') as f:
                    self.solves = json.load(f)

                valid_times = [s['time'] for s in self.solves if s['status'] == 'OK']
                if valid_times:
                    self.fastest_solve = min(valid_times)
                    self.last_solve = self.solves[0]['time'] if self.solves[0]['status'] == 'OK' else -1
            except (json.JSONDecodeError, KeyError):
                self.solves = []

    # Save data to data.json
    def save_data(self):
        with open('data.json', 'w') as f:
            json.dump(self.solves, f, indent=4) # json.dump converts Python data structure to JSON format; indent for readability

    # Record the solve and associated data to the top of the data list
    def record_solve(self, elapsed, status='OK'):
        solve_number = len(self.solves) + 1
        entry = {
            "number": solve_number,
            "time": round(elapsed, 3),
            "status": status,
            "scramble": self.current_scramble
        }
        self.solves.insert(0, entry)
        self.save_data()

        if self.history_win is not None and self.history_text_area is not None:
            self.history_text_area.configure(state=tk.NORMAL)
            self.history_text_area.delete('1.0', tk.END)
            self.populate_history_text()
            self.history_text_area.configure(state=tk.DISABLED)

    # Calculates the current metrics (pb, mo3, ao3, ao12)
    def update_stats_display(self):
        valid_solves = [s['time'] for s in self.solves if s['status'] == 'OK']

        if valid_solves:
            self.fastest_solve = min(valid_solves)
            self.pb_label.config(text=f"Fastest Solve: {self.fastest_solve:.3f}")

        chronological_solves = self.solves[::-1]

        if len(chronological_solves) >= 3:
            last_3 = chronological_solves[-3:]
            if any(s['status'] == 'DNF' for s in last_3):
                self.mo3_label.config(text="Mo3: DNF")
            else:
                mo3_val = sum(s['time'] for s in last_3) / 3
                self.mo3_label.config(text=f"Mo3: {mo3_val:.3f}")

        if len(chronological_solves) >= 3:
            last_3 = chronological_solves[-3:]
            dnf_count = sum(1 for s in last_3 if s['status'] == 'DNF')

            if dnf_count >= 2:
                self.ao3_label.config(text="Ao3: DNF")
            else:
                times_only = [s['time'] if s['status'] == 'OK' else float('inf') for s in last_3]
                times_only.sort()

                ao3_val = times_only[1]
                self.ao3_label.config(text=f"Ao3: {ao3_val:.3f}")

        if len(chronological_solves) >= 12:
            last_12 = chronological_solves[-12:]
            dnf_count = sum(1 for s in last_12 if s['status'] == 'DNF')

            if dnf_count >= 2:
                self.ao12_label.config(text="Ao12: DNF")
            else:
                times_only = [s['time'] if s['status'] == 'OK' else float('inf') for s in last_12]
                times_only.sort()

                ao12_val = sum(times_only[1:11]) / 10
                self.ao12_label.config(text=f"Ao12: {ao12_val:.3f}")

    # Opens a second window with saved solve data
    def open_history_window(self):
        if self.history_win is not None and self.history_win.winfo_exists():
            self.history_win.destroy()

        self.history_win = tk.Toplevel(self.root)
        self.history_win.title("Solve History Log")
        self.history_win.geometry('800x500')
        self.history_win.configure(bg='#1e1e1e')

        self.history_win.protocol('WM_DELETE_WINDOW', self.on_history_close)

        history_title = tk.Label(self.history_win, text="Solve Data", font=('Arial', 16, 'bold'), bg='#1e1e1e', fg='white')
        history_title.pack(pady=10)

        self.history_text_area = tk.Text(self.history_win, bg='#2d2d2d', fg='white', font=('Courier', 10))
        self.history_text_area.pack(expand=True, fill='both', padx=10, pady=10)

        self.history_text_area.tag_config('dnf_color', foreground='red')
        self.history_text_area.tag_config('pb_color', foreground='purple')
        self.history_text_area.tag_config('normal_color', foreground='white')

        self.populate_history_text()

        self.history_text_area.configure(state=tk.DISABLED)

    # Reset history open flag
    def on_history_close(self):
        if self.history_win is not None:
            self.history_win.destroy()
        self.history_win = None
        self.history_text_area = None

    # Update data into history window
    def populate_history_text(self):
        if not self.solves:
            self.history_text_area.insert(tk.END, "No solves recorded yet")
        else:
            for s in self.solves:
                time_display = f"{s['time']:.3f}" if s['status'] == 'OK' else "DNF"
                row_text = f"Solve #{s['number']:<4} | {time_display:<7} | Scramble: {s['scramble']}\n"

                if s['status'] == 'DNF':
                    color = 'dnf_color'
                elif round(s['time'], 3) == round(self.fastest_solve, 3): # Round because of floating point precision issues
                    color = 'pb_color'
                else:
                    color = 'normal_color'
                
                self.history_text_area.insert(tk.END, row_text, color)

    # Generates a random 3x3 scramble in WCA format
    def new_scramble(self, event=None):
        self.scramble_label.config(fg='white')
        self.title_label.config(text="Speedcubing Timer and Stats")

        moves = ["R", "L", "U", "D", "F", "B"]
        modifiers = ["", "'", "2"]

        scramble = []
        last_move = ""

        for _ in range(20):
            available_moves = [m for m in moves if m != last_move]
            move = random.choice(available_moves)
            modifier = random.choice(modifiers)

            scramble.append((move + modifier).center(3))
            last_move = move

        self.current_scramble = "".join(scramble)

        self.scramble_label.config(text=self.current_scramble)

    def on_escape(self, event=None):
        if self.timer_state == 'holding' or self.timer_state == 'ready': # Cancel start
            self.timer_state = 'idle'
            self.timer_label.config(text="0.000", fg='white')

        elif self.timer_state == 'running': # Early start -> DNF
            self.timer_running = False
            self.timer_state = 'idle'
            elapsed = time.time() - self.start_time
            self.timer_label.config(text=f"DNF ({elapsed:.3f})", fg='red')
            self.last_solve = -1

            self.record_solve(elapsed, status='DNF')
            self.new_scramble()
            self.update_stats_display()

    def on_space_press(self, event=None):
        if self.release_timer_id is not None: # Cancel if the release timer is running (debounce filter)
            self.root.after_cancel(self.release_timer_id)
            self.release_timer_id = None
            return

        if self.timer_running:
            self.timer_running = False
            self.timer_state = 'idle'

            elapsed = time.time() - self.start_time
            self.timer_label.config(text=f"{elapsed:.3f}")

            if elapsed < self.fastest_solve or self.fastest_solve == -1:
                self.fastest_solve = elapsed
                self.timer_label.config(fg='purple')
            elif elapsed < self.last_solve or self.last_solve == -1:
                self.last_solve = elapsed
                self.timer_label.config(fg='green')
            else:
                self.timer_label.config(fg='orange')

            self.last_solve = elapsed

            self.record_solve(elapsed, status='OK')
            self.update_stats_display()

            self.new_scramble()

            return

        if self.timer_state != 'idle': return # Ignore if not idle

        # Start negative countdown after holding down space
        self.timer_state = 'holding'
        self.press_start_time = time.time()
        self.timer_label.config(fg='red')
        self.check_hold_progress()


    def check_hold_progress(self):
        if self.timer_state == 'holding':
            elapsed_hold = time.time() - self.press_start_time
            remaining = elapsed_hold - .5

            if remaining >= 0:
                self.timer_label.config(text="0.000", fg='green')
                self.timer_state = 'ready'
            else:
                self.timer_label.config(text=f"{remaining:.3f}", fg='red')
                self.root.after(20, self.check_hold_progress)

    def on_space_release(self, event=None):
        if self.release_timer_id is not None:
            self.root.after_cancel(self.release_timer_id)

        self.release_timer_id = self.root.after(30, self.confirm_release)

    def confirm_release(self):
        self.release_timer_id = None

        if self.timer_state == 'holding':
            self.timer_state = 'idle'
            self.timer_label.config(text="0.000", fg='white')
        elif self.timer_state == 'ready':
            self.timer_state = 'running'
            self.timer_running = True
            self.start_time = time.time()
            self.timer_label.config(fg='white')
            self.scramble_label.config(fg='#1e1e1e')
            self.title_label.config(text="Solving...")
            self.update_timer()

    def update_timer(self):
        if self.timer_running:
            elapsed = time.time() - self.start_time
            self.timer_label.config(text=f"{elapsed:.3f}")
            self.root.after(10, self.update_timer)

if __name__ == '__main__':
    root = tk.Tk()
    app = CubeTimerApp(root)
    root.mainloop()
import tkinter as tk
import random
import time

class CubeTimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Speedcube Timer")
        self.root.geometry('800x500')
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

        self.load_times()

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

        self.root.bind('<KeyPress-space>', self.on_space_press)
        self.root.bind('<KeyRelease-space>', self.on_space_release)
        self.root.bind('<Escape>', self.on_escape)
        self.root.bind('<r>', self.new_scramble)

        self.new_scramble()

    # Attempts to load data from times.txt
    def load_times(self):
        try:
            with open('times.txt', 'r') as f:
                lines = f.readlines()
                valid_times = []
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('DNF'):
                        try:
                            valid_times.append(float(line))
                        except ValueError:
                            pass

                if valid_times:
                    self.fastest_solve = min(valid_times)
                    self.last_solve = valid_times[-1]
        except FileNotFoundError:
            pass

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

        self.scramble_label.config(text="".join(scramble))

    def on_escape(self, event=None):
        if self.timer_state == 'holding' or self.timer_state == 'ready': # Cancel start
            self.timer_state = 'idle'
            self.timer_label.config(text="0.000", fg='white')

        elif self.timer_state == 'running': # Early start -> DNF
            self.timer_running = False
            self.timer_state = 'idle'
            self.timer_label.config(text=f"DNF ({(time.time() - self.start_time):.3f})", fg='red')
            self.last_solve = -1
            self.new_scramble()

            with open('times.txt', 'a') as f:
                f.write('DNF')

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
            self.new_scramble()

            with open('times.txt', 'a') as f:
                f.write(f"{elapsed:.3f}\n")

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
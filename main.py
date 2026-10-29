import tkinter as tk
import random
import time

class CubeTimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Speedcube Timer")
        self.root.geometry("800x500")

        self.root.configure(bg="#1e1e1e")

        self.timer_running = False
        self.start_time = 0
        self.press_start_time = 0  
        self.timer_state = 'idle'  # idle, holding, ready, running
        self.release_timer_id = None # Debounce filter for ghost key releases
        
        self.title_label = tk.Label(root, text="Rubik's Cube Timer & Stats", font=("Arial", 20, "bold"), bg="#1e1e1e", fg="white")
        self.title_label.pack(pady=20)
        
        self.scramble_label = tk.Label(root, text="Generating scramble...", font=("Courier", 14), wraplength=700, justify="center", bg="#1e1e1e", fg="white")
        self.scramble_label.pack(pady=10)

        self.timer_label = tk.Label(root, text="0.000", font=("Arial", 48, "bold"), bg="#1e1e1e", fg="white")
        self.timer_label.pack(pady=20)

        self.root.bind("<KeyPress-space>", self.on_space_press)
        self.root.bind("<KeyRelease-space>", self.on_space_release)
        self.root.bind("<Escape>", self.on_escape)
        self.root.bind("<r>", self.new_scramble)

        self.new_scramble()

    # Generates a random 3x3 scamble in WCA format
    def new_scramble(self, event=None):
        moves = ["R", "L", "U", "D", "F", "B"]
        modifiers = ["", "'", "2"]
        
        scramble = []
        last_face = ""
        
        for _ in range(20):
            available_moves = [m for m in moves if m != last_face]
            face = random.choice(available_moves)
            modifier = random.choice(modifiers)
            
            scramble.append(face + modifier)
            last_face = face
            
        scramble_text = " ".join(scramble)
        self.scramble_label.config(text=scramble_text)

    def on_escape(self, event=None):
        if self.timer_state == 'holding' or 'ready':
            self.timer_state = 'idle'
            self.timer_label.config(text="0.000", fg='white')

    def on_space_press(self, event=None):
        # Cancel if the release timer is running (debounce filter)
        if self.release_timer_id is not None:
            self.root.after_cancel(self.release_timer_id)
            self.release_timer_id = None
            return

        # If the timer is running, stop it
        if self.timer_running:
            self.timer_running = False
            self.timer_state = 'idle'
            elapsed = time.time() - self.start_time
            self.timer_label.config(text=f"{elapsed:.3f}", fg='white')
            self.new_scramble()
            self.scramble_label.config(fg='white')
            self.title_label.config(text="Rubik's Cube Timer & Stats")
            return

        # Ignore if not idle (prevents spamming while holding)
        if self.timer_state != 'idle':
            return

        # Start holding down for the negative countdown
        self.timer_state = 'holding'
        self.press_start_time = time.time()
        self.timer_label.config(fg='red')
        self.check_hold_progress()

    # Active loop that counts up from negative time (-0.500 to 0.000) while holding space
    def check_hold_progress(self):
        if self.timer_state == 'holding':
            elapsed_hold = time.time() - self.press_start_time
            remaining = elapsed_hold - 0.5
            
            if remaining >= 0:
                # Reached 0.000—ready to go!
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
            self.scramble_label.config(fg="#1e1e1e")
            self.title_label.config(text="Solving...")
            self.update_timer()

    # Updates the timer display every 10ms while running
    def update_timer(self):
        if self.timer_running:
            elapsed = time.time() - self.start_time
            self.timer_label.config(text=f"{elapsed:.3f}")
            self.root.after(10, self.update_timer)

if __name__ == "__main__":
    root = tk.Tk()
    app = CubeTimerApp(root)
    root.mainloop()
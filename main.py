import tkinter as tk

class CubeTimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Speedcube Timer")
        self.root.geometry("800x500")
        
        # A simple title label to test the window layout
        self.title_label = tk.Label(root, text="Rubik's Cube Timer & Stats", font=("Arial", 20, "bold"))
        self.title_label.pack(pady=20)

if __name__ == "__main__":
    root = tk.Tk()
    app = CubeTimerApp(root)
    root.mainloop()

# Python Speedcube Timer

A professional-grade, WCA-compliant speedcubing timer and statistics tracker built in Python using `tkinter`. Designed to mirror the workflow and aesthetics of popular competitive timers like **csTimer**.

---

## Features

* **WCA-Compliant Statistics Engine:** Real-time calculation of **Fastest Solve (PB)**, **Mo3** (Mean of 3), **Ao3** (Average of 3), and **Ao12** (Average of 12), with strict WCA handling for DNFs (treated as worst-case infinite values).
* **Live Color-Coded History Log:** A toggleable secondary `Toplevel` window displaying past solves, complete with color-coding for Personal Bests (purple), DNFs (red), and standard solves (white).
* **Persistent Storage:** Automatically saves and loads your entire solve history and scrambles locally via `data.json`.
* **WCA Scramble Generator:** Generates random, regulation-compliant 3x3 scramble strings using standard move notations.
* **Responsive Keyboard Shortcuts:** Optimized for speedcubing muscle memory so you never have to touch your mouse during practice.

---

## Keyboard Shortcuts

| Key | Action |
| :--- | :--- |
| **`Space` (Hold & Release)** | Hold to ready up (turns green at 0.5s), release to start timer, press again to stop and log solve. |
| **`Escape`** | Cancel a ready state or trigger an early-stop **DNF** penalty during a solve. |
| **`R`** | Generate a brand-new random scramble. |
| **`H`** | Toggle the live Solve History window open or closed. |

---

## Getting Started

### Prerequisites
Make sure you have **Python 3.x** installed on your system. *(No external pip packages are required since `tkinter`, `json`, and `random` are built directly into Python's standard library!)*

### Installation & Running
1. Clone or download this repository.
2. Open your terminal or command prompt in the project directory.
3. Run the application:
   ```bash
   python main.py

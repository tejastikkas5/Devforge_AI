"""
Experiment No. 8: Program to Simulate the Working of a Keylogger

AIM:
To understand the working principle of keylogging by simulating it in a safe, self-contained manner.

REQUIREMENTS:
Python 3.x with the built-in tkinter library.

NOTE:
In the journal text, 'entry.bind("", on_key)' was printed because the '<Key>' event tag
was stripped by document processors. In Tkinter, '<Key>' is required to capture keypresses.
Similarly, 'show_log()' is populated with the captured keystrokes for viewing.
"""

import tkinter as tk
from datetime import datetime

log = []


def on_key(e):
    key_char = e.char or e.keysym
    entry_line = f"[{datetime.now().strftime('%H:%M:%S')}] {key_char}"
    log.append(entry_line)
    print(f"Captured: {entry_line}")


def show_log():
    w = tk.Toplevel(root)
    w.title("Captured Keystroke Log")
    text_box = tk.Text(w, width=45, height=15)
    text_box.pack(padx=10, pady=10)
    if log:
        text_box.insert(tk.END, "\n".join(log))
    else:
        text_box.insert(tk.END, "No keystrokes logged yet. Type something in the input box!")


root = tk.Tk()
root.title("Keylogger Simulation (Safe/Self-Contained)")
root.geometry("380x150")

label = tk.Label(root, text="Type below (keystrokes logged locally):")
label.pack(pady=5)

entry = tk.Entry(root, width=30)
entry.pack(pady=5)
entry.bind("<Key>", on_key)

tk.Button(root, text="Show Log", command=show_log).pack(pady=10)

if __name__ == "__main__":
    print("Keylogger simulator GUI started. Close the GUI window to exit.")
    root.mainloop()

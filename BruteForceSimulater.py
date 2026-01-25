import tkinter as tk
from tkinter import ttk, messagebox
import multiprocessing as mp
import time
import string
import math

# ==========================
# random config stuff
# ==========================

CHARSET = string.ascii_lowercase + string.ascii_uppercase + string.digits
BASE = len(CHARSET)
WORKERS = 2   # dont increase too much or pc cries (it depends on how powerful you cpu is + you will need to enhance the code this is the best for if your pc have only two cores)


# ==========================
# convert number -> password
# ==========================

def num_to_password(n, length):
    chars = []

    for _ in range(length):
        n, r = divmod(n, BASE)
        chars.append(CHARSET[r])

    return "".join(reversed(chars))


# ==========================
# worker process
# ==========================

def worker(start, end, target, length, stop_event, found_q, speed_q):

    attempts = 0
    last_time = time.perf_counter()
    last_attempts = 0

    for i in range(start, end):

        if stop_event.is_set():
            return

        pwd = num_to_password(i, length)
        attempts += 1

        if pwd == target:
            stop_event.set()
            found_q.put(pwd)
            return

        # speed update (IMPORTANT: dont touch)
        if attempts % 5000 == 0:
            now = time.perf_counter()
            elapsed = now - last_time

            if elapsed > 0:
                speed = int((attempts - last_attempts) / elapsed)
                speed_q.put(speed)

                last_attempts = attempts
                last_time = now


# ==========================
# GUI
# ==========================

root = tk.Tk()
root.title("Brute-Force Simulator (Educational)")
root.geometry("760x640")
root.resizable(False, False)
root.configure(bg="#121212")

FONT_TITLE = ("Segoe UI", 18, "bold")
FONT_TEXT = ("Consolas", 11)
FONT_BTN = ("Segoe UI", 11, "bold")


# ==========================
# TITLE
# ==========================

tk.Label(
    root,
    text="🔐 Brute-Force Simulator (made by Ali)",
    font=FONT_TITLE,
    bg="#121212",
    fg="white"
).pack(pady=10)

tk.Label(
    root,
    text="Alphanumeric | Multiprocessing | Educational Only",
    font=("Segoe UI", 10),
    bg="#121212",
    fg="gray"
).pack()


# ==========================
# MODE SELECT
# ==========================

mode_var = tk.IntVar(value=4)

frame_mode = tk.Frame(root, bg="#121212")
frame_mode.pack(pady=10)

tk.Label(
    frame_mode,
    text="Mode:",
    font=("Segoe UI", 11),
    bg="#121212",
    fg="white"
).grid(row=0, column=0, padx=5)

def update_mode():
    password_var.set("")
    if mode_var.get() == 6:
        warning_label.config(text="⚠️ 6-character mode can take HOURS or DAYS")
    else:
        warning_label.config(text="")

tk.Radiobutton(
    frame_mode, text="4 Characters (Fast)",
    variable=mode_var, value=4,
    command=update_mode,
    bg="#121212", fg="white", selectcolor="#121212"
).grid(row=0, column=1, padx=10)

tk.Radiobutton(
    frame_mode, text="6 Characters (Very Slow)",
    variable=mode_var, value=6,
    command=update_mode,
    bg="#121212", fg="white", selectcolor="#121212"
).grid(row=0, column=2, padx=10)

warning_label = tk.Label(
    root,
    text="",
    font=("Segoe UI", 10),
    bg="#121212",
    fg="orange"
)
warning_label.pack()


# ==========================
# PASSWORD INPUT
# ==========================

frame_input = tk.Frame(root, bg="#121212")
frame_input.pack(pady=15)

tk.Label(
    frame_input,
    text="Target Password:",
    font=("Segoe UI", 11),
    bg="#121212",
    fg="white"
).grid(row=0, column=0, padx=5)

password_var = tk.StringVar()

def limit_length(*args):
    password_var.set(password_var.get()[:mode_var.get()])

password_var.trace_add("write", limit_length)

password_entry = tk.Entry(
    frame_input,
    textvariable=password_var,
    font=("Consolas", 12),
    width=22,
    show="*"
)
password_entry.grid(row=0, column=1, padx=5)


# ==========================
# OUTPUT BOX
# ==========================

output = tk.Text(
    root,
    height=10,
    width=90,
    bg="#1e1e1e",
    fg="#00ff88",
    font=FONT_TEXT,
    border=0
)
output.pack(pady=15)

output.insert(tk.END, "Waiting for input...\n")
output.config(state="disabled")


# ==========================
# PROGRESS + STATUS
# ==========================

progress = ttk.Progressbar(root, orient="horizontal", length=650)
progress.pack(pady=10)

status = tk.Label(
    root,
    text="Status: Idle",
    font=("Segoe UI", 11),
    bg="#121212",
    fg="yellow"
)
status.pack()


# ==========================
# GLOBALS (yeah yeah)
# ==========================

processes = []
stop_event = None
found_q = None
speed_q = None

start_time = None
total_space = 0


# ==========================
# START
# ==========================

def start():
    global stop_event, found_q, speed_q, start_time, total_space

    target = password_var.get()
    length = mode_var.get()

    if len(target) != length:
        messagebox.showerror("Error", f"Password must be exactly {length} characters")
        return

    for c in target:
        if c not in CHARSET:
            messagebox.showerror("Error", "Allowed: a–z A–Z 0–9")
            return

    total_space = BASE ** length

    stop_event = mp.Event()
    found_q = mp.Queue()
    speed_q = mp.Queue()
    processes.clear()

    chunk = math.ceil(total_space / WORKERS)
    start_time = time.time()

    progress["maximum"] = total_space
    progress["value"] = 0

    status.config(text="Status: Running...", fg="orange")

    output.config(state="normal")
    output.delete("1.0", tk.END)
    output.insert(
        tk.END,
        f"Mode: {length} characters\n"
        f"Total combinations: {total_space:,}\n"
    )
    output.config(state="disabled")

    for i in range(WORKERS):
        s = i * chunk
        e = min(s + chunk, total_space)

        p = mp.Process(
            target=worker,
            args=(s, e, target, length, stop_event, found_q, speed_q)
        )
        p.start()
        processes.append(p)

    root.after(100, monitor)


# ==========================
# MONITOR (speed stays same)
# ==========================

def monitor():
    if stop_event.is_set():

        if not found_q.empty():
            pwd = found_q.get()
            elapsed = time.time() - start_time

            status.config(text="Status: PASSWORD FOUND!", fg="#00ff88")

            output.config(state="normal")
            output.insert(
                tk.END,
                f"\n\n✅ FOUND: {pwd}\nTime: {elapsed:.2f}s"
            )
            output.config(state="disabled")

        return

    speed = 0
    while not speed_q.empty():
        speed += speed_q.get()

    # IMPORTANT: same update logic as original
    progress["value"] += speed // 10

    elapsed = time.time() - start_time
    remaining = max(total_space - progress["value"], 1)
    eta = remaining / speed if speed > 0 else 0

    output.config(state="normal")
    output.delete("1.0", tk.END)
    output.insert(
        tk.END,
        f"Speed: {speed:,} / sec\n"
        f"Progress: {int(progress['value']):,} / {total_space:,}\n"
        f"Elapsed: {int(elapsed)} sec\n"
        f"ETA: {int(eta)} sec"
    )
    output.config(state="disabled")

    root.after(100, monitor)


# ==========================
# STOP / EXIT
# ==========================

def stop():
    if stop_event:
        stop_event.set()
        status.config(text="Status: Stopped", fg="red")

def exit_app():
    if stop_event:
        stop_event.set()

    for p in processes:
        if p.is_alive():
            p.terminate()

    root.destroy()


# ==========================
# BUTTONS
# ==========================

frame_buttons = tk.Frame(root, bg="#121212")
frame_buttons.pack(pady=20)

tk.Button(
    frame_buttons, text="▶ Start",
    font=FONT_BTN, bg="#00aa66", fg="white",
    width=16, command=start
).grid(row=0, column=0, padx=10)

tk.Button(
    frame_buttons, text="⏹ Stop",
    font=FONT_BTN, bg="#aa3333", fg="white",
    width=16, command=stop
).grid(row=0, column=1, padx=10)

tk.Button(
    frame_buttons, text="🚪 Exit",
    font=FONT_BTN, bg="#444444", fg="white",
    width=16, command=exit_app
).grid(row=0, column=2, padx=10)


# ==========================
# RUN
# ==========================

if __name__ == "__main__":
    mp.freeze_support()
    root.mainloop()

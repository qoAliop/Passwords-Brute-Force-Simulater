# 🔐 Brute-Force Simulator (Educational)

Made by Ali

This is a Brute-Force Password Simulator built with Python + Tkinter.
It demonstrates how brute-force attacks work internally, using multiprocessing to speed things up across CPU cores.

⚠️ Educational use only
This project is made to learn cybersecurity concepts, NOT to attack real systems.

# ✨ Features

🔢 Alphanumeric passwords
(a–z, A–Z, 0–9)

⚙️ Multiprocessing support (uses multiple CPU cores)

🔄 4-character & 6-character modes

📊 Live speed tracking (attempts/sec)

⏳ ETA & progress bar

🛑 Stop / Exit buttons

🖥️ Separate GUI window (Tkinter)

🧠 Clean and understandable logic

# 🧪 Modes Explained
✅ 4-Character Mode

--Much faster

--Good for demonstrations

--Millions of combinations

⚠️ 6-Character Mode

--EXTREMELY slow

--Can take hours or days

--Added to show why strong passwords matter

# 🛠️ How It Works (High Level)

Converts numbers into passwords using a custom charset

Splits the keyspace into chunks

Each worker process brute-forces its own range

(the base minimum for this to work is that your pc should have two cpu cores at least)
Workers report speed back to the main UI

Stops instantly once the password is found

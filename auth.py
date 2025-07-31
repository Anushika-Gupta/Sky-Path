import sqlite3
from colorama import Fore, init
from database import get_db_path

init(autoreset=True)


def register():
    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()

    username = input(Fore.CYAN + "👤 Choose a username: ").strip()
    password = input(Fore.CYAN + "🔑 Choose a password (visible): ").strip()

    try:
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        print(Fore.GREEN + "✅ Registered successfully! Please log in.")
    except sqlite3.IntegrityError:
        print(Fore.RED + "❌ Username already exists. Try another one.")
    finally:
        conn.close()


def login():
    conn = sqlite3.connect(get_db_path())  # ✅ Use same database as register()
    cur = conn.cursor()

    username = input(Fore.CYAN + "Username: ").strip()
    password = input(Fore.CYAN + "Password: ").strip()

    cur.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
    row = cur.fetchone()

    if row:
        print(Fore.GREEN + "✅ Login successful!")
        conn.close()
        return row[0], username
    else:
        print(Fore.RED + "❌ Invalid credentials.")
        conn.close()
        return None, None

import sqlite3
import os

def get_db_path():
    return os.path.join(os.path.dirname(__file__), "flight_data.db")

def init_db():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS trips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        start TEXT,
        end TEXT,
        start_time INTEGER,
        itinerary TEXT,
        arrival_time TEXT,
        delay_minutes INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    conn.commit()
    conn.close()
    print("✅ Tables created successfully.")

import sqlite3
from datetime import datetime

def mark_attendance(user_id, name):
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()

    # Create attendance table if not exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER,
        name TEXT,
        date TEXT,
        time TEXT
    )
    """)

    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    cursor.execute("INSERT INTO attendance VALUES (?, ?, ?, ?)", (user_id, name, date, time))

    conn.commit()
    conn.close()

    print("Attendance marked for", name)
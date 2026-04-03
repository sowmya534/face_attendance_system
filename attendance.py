import sqlite3
from datetime import datetime

def mark_attendance(id, name):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    cursor.execute("INSERT INTO attendance VALUES (?, ?, ?, ?)", (id, name, date, time))

    conn.commit()
    conn.close()
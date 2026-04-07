from flask import Flask, render_template, request, jsonify, redirect, session
import sqlite3, numpy as np, smtplib
from datetime import datetime
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- DATABASE ----------------
def get_db():
    conn = sqlite3.connect("attendance.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        face_encoding BLOB,
        image TEXT
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        date TEXT,
        time TEXT
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    # default admin
    conn.execute("INSERT OR IGNORE INTO admins VALUES (1,'admin','admin')")

    conn.commit()
    conn.close()

init_db()

# ---------------- ROUTES ----------------

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/camera")
def camera():
    return render_template("camera.html")

@app.route("/register")
def register():
    return render_template("register.html")

# ---------- REGISTER FACE ----------
@app.route("/register_face", methods=["POST"])
def register_face():
    data = request.json
    name = data["name"]
    descriptor = np.array(data["descriptor"], dtype=np.float32).tobytes()

    conn = get_db()
    conn.execute(
        "INSERT INTO users (name, face_encoding, image) VALUES (?, ?, ?)",
        (name, descriptor, "")
    )
    conn.commit()
    conn.close()

    return jsonify({"status": "registered"})

# ---------- MARK ATTENDANCE ----------
@app.route("/mark_attendance", methods=["POST"])
def mark_attendance():
    descriptor = np.array(request.json["descriptor"])

    conn = get_db()
    users = conn.execute("SELECT * FROM users").fetchall()

    best_match = None
    min_distance = 999

    for user in users:
        stored = np.frombuffer(user["face_encoding"], dtype=np.float32)
        dist = np.linalg.norm(stored - descriptor)

        if dist < min_distance:
            min_distance = dist
            best_match = user["name"]

    if min_distance < 0.6:
        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        time = now.strftime("%H:%M:%S")

        existing = conn.execute(
            "SELECT * FROM attendance WHERE name=? AND date=?",
            (best_match, date)
        ).fetchone()

        if not existing:
            conn.execute(
                "INSERT INTO attendance (name, date, time) VALUES (?, ?, ?)",
                (best_match, date, time)
            )
            conn.commit()

        conn.close()
        return jsonify({"message": f"Attendance marked for {best_match}"})

    conn.close()
    return jsonify({"message": "Face not recognized"})

# ---------- ADMIN LOGIN ----------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        conn = get_db()
        admin = conn.execute(
            "SELECT * FROM admins WHERE username=? AND password=?",
            (request.form["username"], request.form["password"])
        ).fetchone()

        if admin:
            session["admin"] = True
            return redirect("/dashboard")

    return render_template("login.html")

# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect("/login")

    conn = get_db()

    users = conn.execute("SELECT * FROM users").fetchall()
    attendance = conn.execute("SELECT * FROM attendance").fetchall()

    total_users = len(users)
    total_attendance = len(attendance)

    conn.close()

    return render_template(
        "dashboard.html",
        users=users,
        attendance=attendance,
        total_users=total_users,
        total_attendance=total_attendance
    )

# ---------- EMAIL REPORT ----------
@app.route("/send_email")
def send_email():
    sender = "your_email@gmail.com"
    password = "your_app_password"
    receiver = "receiver_email@gmail.com"

    msg = MIMEText("Attendance Report Generated")
    msg["Subject"] = "Attendance Report"
    msg["From"] = sender
    msg["To"] = receiver

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(sender, password)
    server.sendmail(sender, receiver, msg.as_string())
    server.quit()

    return "Email Sent"

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
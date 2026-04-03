from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3
import subprocess
import pandas as pd
from datetime import datetime

app = Flask(__name__)
app.secret_key = "face_attendance_secret_key"


# Home Page
@app.route('/')
def index():
    return render_template('index.html')


# Mark Attendance (Runs recognize.py)
@app.route('/mark_attendance')
def mark_attendance():
    subprocess.call(["python", "recognize.py"])
    return redirect('/')


# Admin Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Change username and password here
        if username == "admin" and password == "admin123":
            session['admin'] = True
            return redirect('/dashboard')
        else:
            return "Invalid Username or Password"

    return render_template('login.html')


# Admin Dashboard
@app.route('/dashboard')
def dashboard():
    if 'admin' not in session:
        return redirect('/login')

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    cursor.execute("SELECT * FROM attendance")
    attendance = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM attendance")
    total_attendance = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM attendance WHERE date = date('now')")
    today_attendance = cursor.fetchone()[0]

    conn.close()

    return render_template("dashboard.html",
                           users=users,
                           attendance=attendance,
                           total_users=total_users,
                           total_attendance=total_attendance,
                           today_attendance=today_attendance)


# Register User Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'admin' not in session:
        return redirect('/login')

    if request.method == 'POST':
        user_id = request.form['user_id']
        name = request.form['name']

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO users VALUES (?, ?)", (user_id, name))
        conn.commit()
        conn.close()

        # Capture face after registering
        subprocess.call(["python", "capture_faces.py"])
        subprocess.call(["python", "train_model.py"])

        return redirect('/dashboard')

    return render_template('register.html')


# Download Attendance Report
@app.route('/download_report')
def download_report():
    if 'admin' not in session:
        return redirect('/login')

    conn = sqlite3.connect("database.db")
    df = pd.read_sql_query("SELECT * FROM attendance", conn)
    conn.close()

    file_name = "attendance_report.csv"
    df.to_csv(file_name, index=False)

    return send_file(file_name, as_attachment=True)


# Logout
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/')


# Run App
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
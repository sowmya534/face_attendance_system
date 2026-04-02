from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import pandas as pd

app = Flask(__name__)
app.secret_key = "attendance_secret"

USERNAME = "admin"
PASSWORD = "admin123"

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == USERNAME and request.form['password'] == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    conn = sqlite3.connect("attendance.db")

    if request.method == 'POST':
        date = request.form['date']
        query = "SELECT * FROM attendance WHERE date=?"
        df = pd.read_sql_query(query, conn, params=(date,))
    else:
        df = pd.read_sql_query("SELECT * FROM attendance", conn)

    conn.close()
    return render_template('index.html', tables=[df.to_html(classes='data')], titles=df.columns.values)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/download')
def download():
    conn = sqlite3.connect("attendance.db")
    df = pd.read_sql_query("SELECT * FROM attendance", conn)
    conn.close()
    df.to_csv("reports/attendance.csv", index=False)
    return "Report Downloaded! Check reports folder."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
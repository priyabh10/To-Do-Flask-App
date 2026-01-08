from flask import Flask, render_template, request, redirect, url_for
import datetime
import sqlite3

app = Flask(__name__)
DATABASE = "todo.db"

# Database connection
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Create table
def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            created_at TEXT,
            updated_at TEXT,
            reminder_time TEXT,
            is_important INTEGER DEFAULT 0,
            location TEXT
        )
    """)
    conn.commit()
    conn.close()

@app.route("/add", methods=["POST"])
def add_task():
    title = request.form["title"]
    reminder_time = request.form.get("reminder_time")
    location = request.form.get("location")
    is_important = 1 if request.form.get("important") else 0

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db_connection()
    conn.execute("""
        INSERT INTO tasks 
        (title, created_at, updated_at, reminder_time, is_important, location)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (title, now, now, reminder_time, is_important, location))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/important")
def important_tasks():
    conn = get_db_connection()
    tasks = conn.execute("SELECT * FROM tasks WHERE is_important = 1").fetchall()
    conn.close()
    return render_template("index.html", tasks=tasks)

@app.route("/completed")
def completed_tasks():
    conn = get_db_connection()
    tasks = conn.execute("SELECT * FROM tasks WHERE completed = 1").fetchall()
    conn.close()
    return render_template("index.html", tasks=tasks)

@app.route("/today")
def today_tasks():
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_db_connection()
    tasks = conn.execute("""
        SELECT * FROM tasks WHERE date(created_at) = ?
    """, (today,)).fetchall()
    conn.close()
    return render_template("index.html", tasks=tasks)

@app.route("/stats")
def stats():
    conn = get_db_connection()
    total = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    completed = conn.execute("SELECT COUNT(*) FROM tasks WHERE completed = 1").fetchone()[0]
    important = conn.execute("SELECT COUNT(*) FROM tasks WHERE is_important = 1").fetchone()[0]
    pending = total - completed
    conn.close()

    return render_template(
        "stats.html",
        total=total,
        completed=completed,
        pending=pending,
        important=important
    )



if __name__ == "__main__":
    init_db()
    app.run(debug=True)    #app.run(host="0.0.0.0", port=10000)


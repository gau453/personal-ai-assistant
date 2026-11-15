

import sqlite3
from contextlib import closing

DB_NAME = "personal_assistant.db"


def connect_db():
    return sqlite3.connect(DB_NAME)


# =====================================
# CREATE TASK TABLE
# =====================================

def create_task_table():
    with closing(connect_db()) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                completed INTEGER DEFAULT 0
            )
        """)

        conn.commit()


# =====================================
# ADD A TASK
# =====================================

def add_task(task):
    task = task.strip()

    if not task:
        return "Task cannot be empty."

    with closing(connect_db()) as conn:
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO tasks (task) VALUES (?)",
            (task,)
        )

        conn.commit()

    return f"Task added successfully: {task}"


# =====================================
# GET ALL TASKS
# =====================================

def get_tasks():
    with closing(connect_db()) as conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM tasks ORDER BY id"
        )

        tasks = cursor.fetchall()

    if not tasks:
        return "No tasks found."

    return tasks


# =====================================
# COMPLETE A TASK
# =====================================

def complete_task(task_id):
    with closing(connect_db()) as conn:
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE tasks SET completed = 1 WHERE id = ?",
            (task_id,)
        )

        updated = cursor.rowcount
        conn.commit()

    if updated:
        return "Task marked as completed."

    return "Task not found."

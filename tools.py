
import sqlite3
from contextlib import closing

DB_NAME = "personal_assistant.db"


def connect_db():
    return sqlite3.connect(DB_NAME)


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


def add_task(task):
    if not isinstance(task, str) or not task.strip():
        return "Task cannot be empty."

    task = task.strip()

    with closing(connect_db()) as conn:
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO tasks (task) VALUES (?)",
            (task,)
        )

        conn.commit()

    return f"Task added successfully: {task}"


def get_tasks():
    with closing(connect_db()) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, task, completed
            FROM tasks
            ORDER BY id
        """)

        return cursor.fetchall()


def complete_task(task_id):
    if not isinstance(task_id, int) or task_id <= 0:
        return "Invalid task ID."

    with closing(connect_db()) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE tasks
            SET completed = 1
            WHERE id = ?
        """, (task_id,))

        updated = cursor.rowcount
        conn.commit()

    if updated:
        return "Task marked as completed."

    return "Task not found."

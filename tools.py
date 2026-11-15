
import os
import sqlite3
from contextlib import contextmanager


# ==========================================
# 1. DATABASE CONFIGURATION
# ==========================================

DB_NAME = os.getenv(
    "DATABASE_PATH",
    "personal_assistant.db"
)


# ==========================================
# 2. DATABASE CONNECTION
# ==========================================

@contextmanager
def connect_db():
    """Create and safely manage database connections."""

    directory = os.path.dirname(DB_NAME)

    if directory:
        os.makedirs(directory, exist_ok=True)

    conn = sqlite3.connect(
        DB_NAME,
        timeout=10
    )

    conn.execute("PRAGMA busy_timeout = 10000")

    try:
        yield conn
        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


# ==========================================
# 3. CREATE TASK TABLE
# ==========================================

def create_task_table():

    with connect_db() as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                completed INTEGER DEFAULT 0
            )
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_completed
            ON tasks(completed)
        """)


# ==========================================
# 4. ADD NEW TASK
# ==========================================

def add_task(task):

    if not isinstance(task, str):
        return "Task must be text."

    task = task.strip()

    if not task:
        return "Task cannot be empty."

    if len(task) > 500:
        return "Task cannot exceed 500 characters."

    try:

        with connect_db() as conn:

            conn.execute("""
                INSERT INTO tasks (task, completed)
                VALUES (?, 0)
            """, (task,))

        return f"Task added successfully: {task}"

    except sqlite3.Error as error:

        print("Task creation error:", type(error).__name__)

        return "Unable to add task. Please try again."


# ==========================================
# 5. GET ALL TASKS
# ==========================================

def get_tasks():

    with connect_db() as conn:

        cursor = conn.execute("""
            SELECT id, task, completed
            FROM tasks
            ORDER BY id ASC
        """)

        return cursor.fetchall()


# ==========================================
# 6. GET PENDING TASKS
# ==========================================

def get_pending_tasks():

    with connect_db() as conn:

        cursor = conn.execute("""
            SELECT id, task, completed
            FROM tasks
            WHERE completed = 0
            ORDER BY id ASC
        """)

        return cursor.fetchall()


# ==========================================
# 7. GET COMPLETED TASKS
# ==========================================

def get_completed_tasks():

    with connect_db() as conn:

        cursor = conn.execute("""
            SELECT id, task, completed
            FROM tasks
            WHERE completed = 1
            ORDER BY id ASC
        """)

        return cursor.fetchall()


# ==========================================
# 8. COMPLETE TASK
# ==========================================

def complete_task(task_id):

    if (
        not isinstance(task_id, int)
        or isinstance(task_id, bool)
        or task_id <= 0
    ):
        return "Invalid task ID."

    try:

        with connect_db() as conn:

            cursor = conn.execute("""
                UPDATE tasks
                SET completed = 1
                WHERE id = ?
                  AND completed = 0
            """, (task_id,))

            updated = cursor.rowcount

            if updated:
                return "Task marked as completed."

            # Check whether the task already exists.

            cursor = conn.execute("""
                SELECT completed
                FROM tasks
                WHERE id = ?
            """, (task_id,))

            task = cursor.fetchone()

        if task is None:
            return "Task not found."

        return "This task is already completed."

    except sqlite3.Error as error:

        print("Task completion error:", type(error).__name__)

        return "Unable to complete task. Please try again."


# ==========================================
# 9. DELETE TASK
# ==========================================

def delete_task(task_id):

    if (
        not isinstance(task_id, int)
        or isinstance(task_id, bool)
        or task_id <= 0
    ):
        return "Invalid task ID."

    try:

        with connect_db() as conn:

            cursor = conn.execute("""
                DELETE FROM tasks
                WHERE id = ?
            """, (task_id,))

            deleted = cursor.rowcount

        if deleted:
            return "Task deleted successfully."

        return "Task not found."

    except sqlite3.Error as error:

        print("Task deletion error:", type(error).__name__)

        return "Unable to delete task. Please try again."

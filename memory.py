import sqlite3
from contextlib import closing

DB_NAME = "personal_assistant.db"


def connect_db():
    return sqlite3.connect(DB_NAME)


def create_memory_table():
    with closing(connect_db()) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_key TEXT UNIQUE NOT NULL,
                memory_value TEXT NOT NULL
            )
        """)

        conn.commit()


def save_memory(key, value):
    if not isinstance(key, str) or not isinstance(value, str):
        return "Memory key and value must be text."

    key = key.strip().lower().replace(" ", "_")
    value = value.strip()

    if not key or not value:
        return "Memory key and value cannot be empty."

    with closing(connect_db()) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO memories (memory_key, memory_value)
            VALUES (?, ?)
            ON CONFLICT(memory_key)
            DO UPDATE SET memory_value = excluded.memory_value
        """, (key, value))

        conn.commit()

    return f"I'll remember: {key} = {value}"


def get_memory(key):
    if not isinstance(key, str):
        return None

    key = key.strip().lower().replace(" ", "_")

    with closing(connect_db()) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, memory_key, memory_value
            FROM memories
            WHERE memory_key = ?
        """, (key,))

        return cursor.fetchone()


def get_all_memories():
    with closing(connect_db()) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, memory_key, memory_value
            FROM memories
            ORDER BY id
        """)

        return cursor.fetchall()


def delete_memory(key):
    if not isinstance(key, str):
        return "Invalid memory key."

    key = key.strip().lower().replace(" ", "_")

    with closing(connect_db()) as conn:
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM memories WHERE memory_key = ?",
            (key,)
        )

        deleted = cursor.rowcount
        conn.commit()

    if deleted:
        return "Memory deleted successfully."

    return "Memory not found."

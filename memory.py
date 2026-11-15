

import sqlite3
from contextlib import closing

DB_NAME = "personal_assistant.db"


def connect_db():
    return sqlite3.connect(DB_NAME)


# =====================================
# CREATE MEMORY TABLE
# =====================================

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


# =====================================
# SAVE OR UPDATE A MEMORY
# =====================================

def save_memory(key, value):
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


# =====================================
# RETRIEVE A MEMORY
# =====================================

def get_memory(key):
    key = key.strip().lower().replace(" ", "_")

    with closing(connect_db()) as conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT memory_value FROM memories WHERE memory_key = ?",
            (key,)
        )

        result = cursor.fetchone()

    if result:
        return result[0]

    return "I don't have that information."


# =====================================
# VIEW ALL MEMORIES
# =====================================

def get_all_memories():
    with closing(connect_db()) as conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM memories ORDER BY id"
        )

        memories = cursor.fetchall()

    return memories


# =====================================
# DELETE A MEMORY
# =====================================

def delete_memory(key):
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


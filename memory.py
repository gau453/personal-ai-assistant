
import os
import re
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
    """Create and safely manage a database connection."""

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
# 3. NORMALIZE MEMORY KEYS
# ==========================================

def normalize_key(key):
    """Normalize memory keys for consistent storage."""

    if not isinstance(key, str):
        raise ValueError("Memory key must be text.")

    key = key.strip().lower()

    key = re.sub(r"\s+", "_", key)

    if not key:
        raise ValueError("Memory key cannot be empty.")

    return key


# ==========================================
# 4. CREATE MEMORY TABLE
# ==========================================

def create_memory_table():

    with connect_db() as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_key TEXT UNIQUE NOT NULL,
                memory_value TEXT NOT NULL
            )
        """)


# ==========================================
# 5. SAVE MEMORY
# ==========================================

def save_memory(key, value):

    if not isinstance(value, str):
        return "Memory value must be text."

    try:
        key = normalize_key(key)
        value = value.strip()

        if not value:
            return "Memory value cannot be empty."

        with connect_db() as conn:

            conn.execute("""
                INSERT INTO memories (
                    memory_key,
                    memory_value
                )
                VALUES (?, ?)

                ON CONFLICT(memory_key)
                DO UPDATE SET
                    memory_value = excluded.memory_value
            """, (key, value))

        return f"I'll remember: {key} = {value}"

    except ValueError as error:
        return str(error)

    except sqlite3.Error as error:
        print("Memory save error:", type(error).__name__)
        return "Unable to save memory. Please try again."


# ==========================================
# 6. GET MEMORY BY KEY
# ==========================================

def get_memory(key):

    try:
        key = normalize_key(key)

        with connect_db() as conn:

            cursor = conn.execute("""
                SELECT
                    id,
                    memory_key,
                    memory_value
                FROM memories
                WHERE memory_key = ?
            """, (key,))

            return cursor.fetchone()

    except ValueError:
        return None

    except sqlite3.Error as error:
        print("Memory retrieval error:", type(error).__name__)
        return None


# ==========================================
# 7. GET ALL MEMORIES
# ==========================================

def get_all_memories():

    try:
        with connect_db() as conn:

            cursor = conn.execute("""
                SELECT
                    id,
                    memory_key,
                    memory_value
                FROM memories
                ORDER BY id ASC
            """)

            return cursor.fetchall()

    except sqlite3.Error as error:
        print("Memory database error:", type(error).__name__)
        return []


# ==========================================
# 8. SEARCH MEMORIES
# ==========================================

def search_memory(keyword):

    if not isinstance(keyword, str):
        return []

    keyword = keyword.strip().lower()

    if not keyword:
        return []

    try:
        with connect_db() as conn:

            cursor = conn.execute("""
                SELECT
                    id,
                    memory_key,
                    memory_value
                FROM memories
                WHERE LOWER(memory_key) LIKE ?
                   OR LOWER(memory_value) LIKE ?
                ORDER BY id ASC
            """, (
                f"%{keyword}%",
                f"%{keyword}%"
            ))

            return cursor.fetchall()

    except sqlite3.Error as error:
        print("Memory search error:", type(error).__name__)
        return []


# ==========================================
# 9. DELETE MEMORY
# ==========================================

def delete_memory(key):

    try:
        key = normalize_key(key)

        with connect_db() as conn:

            cursor = conn.execute("""
                DELETE FROM memories
                WHERE memory_key = ?
            """, (key,))

            deleted = cursor.rowcount

        if deleted:
            return "Memory deleted successfully."

        return "Memory not found."

    except ValueError as error:
        return str(error)

    except sqlite3.Error as error:
        print("Memory deletion error:", type(error).__name__)
        return "Unable to delete memory. Please try again."

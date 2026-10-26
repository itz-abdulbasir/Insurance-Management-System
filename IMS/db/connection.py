"""
IMS — Database Connection & Query Abstraction Layer

Provides:
  - get_connection()  → live SQLite connection
  - execute_query()   → universal query executor (SELECT / INSERT / UPDATE / DELETE)
  - init_db()         → creates database + runs schema.sql at first launch
"""

import os
import sys
import sqlite3

# Handle both normal execution and PyInstaller bundled execution
if getattr(sys, 'frozen', False):
    # Running as compiled .exe
    BASE_DIR = sys._MEIPASS
else:
    # Running as script
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Import config — use parent package
sys.path.insert(0, os.path.dirname(BASE_DIR) if getattr(sys, 'frozen', False) else BASE_DIR)
from config import DB_CONFIG


def get_connection():
    """Returns a live SQLite connection to IMS_DB."""
    try:
        # Determine database path. For PyInstaller, it's better to store DB outside MEIPASS
        # but for simplicity, we just use the name from DB_CONFIG in the current working directory.
        db_path = DB_CONFIG.get("database", "ims_db.sqlite3")
        conn = sqlite3.connect(db_path, timeout=20.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        return conn
    except sqlite3.Error as e:
        raise ConnectionError(f"Database connection failed: {e}")


def execute_query(query, params=(), fetch=False):
    """
    Universal query executor.

    Args:
        query:  SQL string with %s placeholders
        params: tuple of parameters (prevents SQL injection)
        fetch:  True  → returns list of dict rows  (SELECT)
                False → commits the change          (INSERT/UPDATE/DELETE)

    Returns:
        fetch=True  → list[dict]
        fetch=False → lastrowid (int) for INSERT, or 0 for UPDATE/DELETE
    """
    # Replace MySQL syntax with SQLite syntax
    query = query.replace("%s", "?")
    query = query.replace("NOW()", "CURRENT_TIMESTAMP")
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        if fetch:
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def init_db():
    """
    Creates the IMS_DB database and all tables from schema.sql.
    Safe to call multiple times — uses CREATE TABLE IF NOT EXISTS.
    """
    try:
        # Locate schema.sql (works for both script and .exe)
        schema_path = os.path.join(BASE_DIR, "db", "schema.sql")
        if not os.path.exists(schema_path):
            # Fallback: look relative to this file
            schema_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "schema.sql"
            )

        with open(schema_path, "r", encoding="utf-8") as f:
            sql_content = f.read()

        conn = get_connection()
        cursor = conn.cursor()
        
        # SQLite executescript can handle multiple statements separated by semicolons
        cursor.executescript(sql_content)
        
        conn.commit()
        print("[IMS] Database initialized successfully.")

    except sqlite3.Error as e:
        print(f"[IMS] Database initialization failed: {e}")
        raise e
    except Exception as e:
        print(f"[IMS] Initialization failed: {e}")
        raise e
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

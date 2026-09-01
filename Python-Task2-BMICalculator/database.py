"""
database.py
-----------
SQLite persistence layer for the BMI Tracker application.

Handles:
- Automatic database/directory creation on first run.
- CRUD-style operations for BMI records.
- Graceful handling of read/write failures (never lets a DB error crash the app).
"""

import os
import sqlite3
from datetime import datetime


class DatabaseError(Exception):
    """Raised when a database operation fails, wrapping the underlying error."""
    pass


def _get_data_dir() -> str:
    """
    Return the path to the 'data' directory next to this file.
    Using __file__ (not the CWD) ensures the DB path works
    regardless of where the project is extracted or run from.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    return data_dir


def get_db_path() -> str:
    """Return the full path to the SQLite database file, creating the folder if needed."""
    data_dir = _get_data_dir()
    try:
        os.makedirs(data_dir, exist_ok=True)
    except OSError as exc:
        raise DatabaseError(f"Could not create data directory: {exc}")
    return os.path.join(data_dir, "bmi_tracker.db")


class BMIDatabase:
    """Wraps all SQLite interactions for BMI records."""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or get_db_path()
        self._init_db()

    def _connect(self):
        """Create a new SQLite connection. Raises DatabaseError on failure."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=5)
            conn.execute("PRAGMA foreign_keys = ON;")
            return conn
        except sqlite3.Error as exc:
            raise DatabaseError(f"Could not connect to database: {exc}")

    def _init_db(self):
        """Create the bmi_records table if it does not already exist."""
        create_sql = """
        CREATE TABLE IF NOT EXISTS bmi_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            weight REAL NOT NULL,
            height REAL NOT NULL,
            bmi REAL NOT NULL,
            category TEXT NOT NULL,
            timestamp TEXT NOT NULL
        );
        """
        try:
            conn = self._connect()
            with conn:
                conn.execute(create_sql)
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_username ON bmi_records(username);"
                )
        except sqlite3.Error as exc:
            raise DatabaseError(f"Could not initialize database: {exc}")
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def add_record(self, username: str, weight: float, height: float,
                    bmi: float, category: str) -> int:
        """Insert a new BMI record. Returns the new row id, or raises DatabaseError."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        insert_sql = """
        INSERT INTO bmi_records (username, weight, height, bmi, category, timestamp)
        VALUES (?, ?, ?, ?, ?, ?);
        """
        try:
            conn = self._connect()
            with conn:
                cursor = conn.execute(
                    insert_sql, (username, weight, height, bmi, category, timestamp)
                )
                return cursor.lastrowid
        except sqlite3.Error as exc:
            raise DatabaseError(f"Failed to save BMI record: {exc}")
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def get_records_for_user(self, username: str) -> list:
        """Return all records for a given user, most recent first."""
        select_sql = """
        SELECT id, username, weight, height, bmi, category, timestamp
        FROM bmi_records
        WHERE username = ?
        ORDER BY timestamp ASC, id ASC;
        """
        try:
            conn = self._connect()
            with conn:
                cursor = conn.execute(select_sql, (username,))
                rows = cursor.fetchall()
            return [
                {
                    "id": r[0],
                    "username": r[1],
                    "weight": r[2],
                    "height": r[3],
                    "bmi": r[4],
                    "category": r[5],
                    "timestamp": r[6],
                }
                for r in rows
            ]
        except sqlite3.Error as exc:
            raise DatabaseError(f"Failed to retrieve history: {exc}")
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def get_all_usernames(self) -> list:
        """Return a sorted list of distinct usernames that have records."""
        select_sql = "SELECT DISTINCT username FROM bmi_records ORDER BY username COLLATE NOCASE ASC;"
        try:
            conn = self._connect()
            with conn:
                cursor = conn.execute(select_sql)
                rows = cursor.fetchall()
            return [r[0] for r in rows]
        except sqlite3.Error as exc:
            raise DatabaseError(f"Failed to retrieve user list: {exc}")
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def delete_records_for_user(self, username: str) -> int:
        """Delete all records for a user. Returns number of rows deleted."""
        delete_sql = "DELETE FROM bmi_records WHERE username = ?;"
        try:
            conn = self._connect()
            with conn:
                cursor = conn.execute(delete_sql, (username,))
                return cursor.rowcount
        except sqlite3.Error as exc:
            raise DatabaseError(f"Failed to delete records: {exc}")
        finally:
            try:
                conn.close()
            except Exception:
                pass

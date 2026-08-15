"""
init_db.py
----------
Run this script once to create drugfree_campus.db and all required tables.

Usage:
    python init_db.py

Uses CREATE TABLE IF NOT EXISTS so running it again never destroys data.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "drugfree_campus.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ------------------------------------------------------------------
    # TABLE: users
    # ------------------------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id            INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name          TEXT    NOT NULL,
            email              TEXT    NOT NULL UNIQUE,
            username           TEXT    NOT NULL UNIQUE,
            password           TEXT    NOT NULL,
            college_department TEXT    NOT NULL,
            created_at         TEXT    DEFAULT (datetime('now', 'localtime'))
        )
    """)

    # ------------------------------------------------------------------
    # TABLE: quiz_results
    # ------------------------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_results (
            result_id        INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id          INTEGER NOT NULL,
            total_questions  INTEGER NOT NULL,
            correct_answers  INTEGER NOT NULL,
            wrong_answers    INTEGER NOT NULL,
            score            INTEGER NOT NULL,
            percentage       REAL    NOT NULL,
            attempted_at     TEXT    DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    # ------------------------------------------------------------------
    # TABLE: pledge
    # ------------------------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pledge (
            pledge_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id       INTEGER NOT NULL UNIQUE,
            pledge_status TEXT    NOT NULL DEFAULT 'completed',
            pledged_at    TEXT    DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    # ------------------------------------------------------------------
    # TABLE: decision_results
    # ------------------------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS decision_results (
            decision_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id          INTEGER NOT NULL,
            total_scenarios  INTEGER NOT NULL,
            healthy_choices  INTEGER NOT NULL,
            score_percentage REAL    NOT NULL,
            completed_at     TEXT    DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    conn.commit()
    conn.close()
    print("=" * 55)
    print("  DrugFree Campus – Database Initialised Successfully")
    print("=" * 55)
    print(f"  Database file : {DB_PATH}")
    print("  Tables created:")
    print("    • users")
    print("    • quiz_results")
    print("    • pledge")
    print("    • decision_results")
    print("=" * 55)
    print("  Run  'python app.py'  to start the application.")
    print("=" * 55)


if __name__ == "__main__":
    init_db()

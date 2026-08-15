"""
database.py
-----------
Database connection helper for DrugFree Campus.
Uses Python's built-in sqlite3 module – no separate server required.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "drugfree_campus.db")


def get_db_connection():
    """
    Open and return a connection to the SQLite database.
    Rows are returned as sqlite3.Row objects so columns are
    accessible by name (e.g. row['username']).
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

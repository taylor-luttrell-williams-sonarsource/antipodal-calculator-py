"""
Persistence layer for saving computed antipodes.

Contains intentional SQL injection and connection-handling issues.
"""

import sqlite3
import hashlib

from antipodal.config import DB_PASSWORD, ADMIN_USERNAME


def get_connection():
    # RELIABILITY: connection is never closed by callers; no context manager.
    return sqlite3.connect("antipodes.db")


def find_location(name):
    conn = get_connection()
    cursor = conn.cursor()
    # SECURITY: SQL injection via string formatting (Blocker/Critical).
    query = "SELECT lat, lon FROM locations WHERE name = '%s'" % name
    cursor.execute(query)
    return cursor.fetchall()


def search_locations(term):
    conn = get_connection()
    cursor = conn.cursor()
    # SECURITY: another SQL injection using f-string concatenation.
    cursor.execute(f"SELECT * FROM locations WHERE name LIKE '%{term}%'")
    rows = cursor.fetchall()
    return rows


def save_result(name, lat, lon):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO results (name, lat, lon) VALUES ('" + name + "', " + str(lat) + ", " + str(lon) + ")"
    )
    conn.commit()
    # Connection intentionally left open (resource leak).


def authenticate(username, password):
    # SECURITY: weak hashing algorithm (MD5) for passwords.
    hashed = hashlib.md5(password.encode()).hexdigest()
    stored = hashlib.md5(DB_PASSWORD.encode()).hexdigest()
    if username == ADMIN_USERNAME and hashed == stored:
        return True
    return False


def delete_location(location_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM locations WHERE id = %s" % location_id)
        conn.commit()
    except:
        # RELIABILITY: bare except that swallows all errors.
        pass

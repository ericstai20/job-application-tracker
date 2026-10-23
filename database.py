# database.py
# Responsible for everything related to storing data in SQLite:
# creating the database and tables, and adding, reading, updating,
# and deleting job applications. Other files call functions from here
# instead of talking to the database directly.

import sqlite3

# The database is a single file in the project folder.
# It's listed in .gitignore (*.db) so personal data never goes to GitHub.
DB_PATH = "applications.db"

# The allowed statuses. Must match the CHECK rule in init_db().
STATUSES = ["Applied", "Interviewing", "Offer", "Rejected"]


def get_connection():
    """Open a connection to the database file (creates the file if missing)."""
    return sqlite3.connect(DB_PATH)


def init_db():
    """Create the applications table if it doesn't exist yet."""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            company      TEXT NOT NULL,
            role         TEXT NOT NULL,
            status       TEXT NOT NULL
                         CHECK (status IN ('Applied', 'Interviewing', 'Offer', 'Rejected')),
            date_applied TEXT NOT NULL,
            location     TEXT,
            job_link     TEXT,
            notes        TEXT
        )
    """)
    conn.commit()
    conn.close()


def add_application(company, role, status, date_applied,
                    location=None, job_link=None, notes=None):
    """Save a new job application as a row in the table."""
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO applications
            (company, role, status, date_applied, location, job_link, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (company, role, status, date_applied, location, job_link, notes),
    )
    conn.commit()
    conn.close()


def get_applications():
    """Return all applications as a list of dictionaries, newest first."""
    conn = get_connection()
    # Return rows that can be looked up by column name, not just position.
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM applications ORDER BY date_applied DESC"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

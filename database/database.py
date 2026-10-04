import sqlite3
from datetime import datetime
from pathlib import Path


# Database file location
DATABASE_PATH = Path(__file__).parent / "feedback.db"


def get_connection():
    """Create and return a connection to the SQLite database."""
    return sqlite3.connect(DATABASE_PATH)


def initialize_database():
    """Create the feedback table if it does not already exist."""
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            model_prediction TEXT NOT NULL,
            correct_label TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def save_feedback(message, model_prediction, correct_label):
    """Save user feedback to the database."""

    connection = get_connection()
    cursor = connection.cursor()

    timestamp = datetime.now().isoformat()

    cursor.execute("""
        INSERT INTO feedback
        (message, model_prediction, correct_label, timestamp)
        VALUES (?, ?, ?, ?)
    """, (
        message,
        model_prediction,
        correct_label,
        timestamp
    ))

    connection.commit()

    feedback_id = cursor.lastrowid

    connection.close()

    return feedback_id


def get_feedback():
    """Return all stored feedback."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, message, model_prediction, correct_label, timestamp
        FROM feedback
        ORDER BY id ASC
    """)

    rows = cursor.fetchall()

    connection.close()

    return rows
def get_corrected_feedback():
    """Return feedback where the user's label differs from the model prediction."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT message, correct_label
        FROM feedback
        WHERE model_prediction != correct_label
        ORDER BY id ASC
    """)

    rows = cursor.fetchall()

    connection.close()

    return rows

def get_feedback_count():
    """Return the number of feedback records stored."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM feedback")

    count = cursor.fetchone()[0]

    connection.close()

    return count


if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully.")
    print(f"Database location: {DATABASE_PATH}")
import sqlite3
from datetime import datetime
from pathlib import Path


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DATABASE_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "feedback.db"
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    """Create and return a connection to the SQLite database."""

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    return sqlite3.connect(DATABASE_PATH)


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def initialize_database():
    """
    Create the feedback table if it does not exist.

    Also upgrades an existing database by adding the
    used_for_retraining column if necessary.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            model_prediction TEXT NOT NULL,
            correct_label TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            used_for_retraining INTEGER NOT NULL DEFAULT 0
        )
    """)

    # Check existing columns
    cursor.execute("PRAGMA table_info(feedback)")

    columns = [
        row[1]
        for row in cursor.fetchall()
    ]

    # Upgrade old database if necessary
    if "used_for_retraining" not in columns:

        cursor.execute("""
            ALTER TABLE feedback
            ADD COLUMN used_for_retraining
            INTEGER NOT NULL DEFAULT 0
        """)

    connection.commit()
    connection.close()


# ============================================================
# SAVE FEEDBACK
# ============================================================

def save_feedback(message, model_prediction, correct_label):
    """
    Save user feedback to the database.

    Returns:
        int: ID of the newly inserted feedback record.
    """

    message = message.strip()

    model_prediction = (
        model_prediction
        .strip()
        .lower()
    )

    correct_label = (
        correct_label
        .strip()
        .lower()
    )

    if not message:
        raise ValueError(
            "message cannot be empty"
        )

    if model_prediction not in ("spam", "ham"):
        raise ValueError(
            "model_prediction must be 'spam' or 'ham'"
        )

    if correct_label not in ("spam", "ham"):
        raise ValueError(
            "correct_label must be 'spam' or 'ham'"
        )

    connection = get_connection()
    cursor = connection.cursor()

    timestamp = datetime.now().isoformat()

    cursor.execute("""
        INSERT INTO feedback
        (
            message,
            model_prediction,
            correct_label,
            timestamp,
            used_for_retraining
        )
        VALUES (?, ?, ?, ?, 0)
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


# ============================================================
# GET ALL FEEDBACK
# ============================================================

def get_feedback():
    """Return all stored feedback."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            message,
            model_prediction,
            correct_label,
            timestamp,
            used_for_retraining
        FROM feedback
        ORDER BY id ASC
    """)

    rows = cursor.fetchall()

    connection.close()

    return rows


# ============================================================
# GET CORRECTED FEEDBACK
# ============================================================

def get_corrected_feedback():
    """
    Return feedback where the user's label differs
    from the model's prediction.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            message,
            correct_label
        FROM feedback
        WHERE LOWER(TRIM(model_prediction))
              != LOWER(TRIM(correct_label))
        ORDER BY id ASC
    """)

    rows = cursor.fetchall()

    connection.close()

    return rows


# ============================================================
# GET FEEDBACK COUNT
# ============================================================

def get_feedback_count():
    """Return the total number of feedback records."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM feedback
    """)

    count = cursor.fetchone()[0]

    connection.close()

    return count


# ============================================================
# GET RETRAINING CANDIDATES
# ============================================================

def get_retraining_candidates(min_reports=5):
    """
    Find messages where the same label has been reported
    at least min_reports times.

    Only unused feedback is considered.

    Returns:

        [
            (message, correct_label, report_count),
            ...
        ]
    """

    if min_reports < 1:
        raise ValueError(
            "min_reports must be at least 1"
        )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            MIN(TRIM(message)) AS message,
            LOWER(TRIM(correct_label)) AS correct_label,
            COUNT(*) AS report_count
        FROM feedback
        WHERE used_for_retraining = 0
        GROUP BY
            LOWER(TRIM(message)),
            LOWER(TRIM(correct_label))
        HAVING COUNT(*) >= ?
        ORDER BY
            message ASC,
            correct_label ASC
    """, (min_reports,))

    rows = cursor.fetchall()

    connection.close()

    return rows


# ============================================================
# MARK RETRAINING CANDIDATES AS USED
# ============================================================

def mark_retraining_candidates_as_used(candidates):
    """
    Mark feedback records as used after successful retraining.

    Parameters:
        candidates:
            List returned by get_retraining_candidates().
    """

    if not candidates:
        return

    connection = get_connection()
    cursor = connection.cursor()

    for message, correct_label, _ in candidates:

        cursor.execute("""
            UPDATE feedback
            SET used_for_retraining = 1
            WHERE LOWER(TRIM(message))
                  = LOWER(TRIM(?))
              AND LOWER(TRIM(correct_label))
                  = LOWER(TRIM(?))
              AND used_for_retraining = 0
        """, (
            message,
            correct_label
        ))

    connection.commit()
    connection.close()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    initialize_database()

    print(
        "Database initialized successfully."
    )

    print(
        f"Database location: {DATABASE_PATH}"
    )
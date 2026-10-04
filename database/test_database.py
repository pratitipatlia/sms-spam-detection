from database.database import (
    initialize_database,
    save_feedback,
    get_feedback,
    get_feedback_count,
    get_corrected_feedback,
    get_retraining_candidates,
    get_connection
)


# ============================================================
# INITIALIZE DATABASE
# ============================================================

initialize_database()

print("Database initialized successfully.")


# ============================================================
# TEST 1: SAVE FEEDBACK
# ============================================================

message = "Your account has been credited with $1000"
prediction = "spam"
correct_label = "ham"

feedback_id = save_feedback(
    message,
    prediction,
    correct_label
)

print("\nFeedback saved successfully!")
print("Feedback ID:", feedback_id)


# ============================================================
# TEST 2: FEEDBACK COUNT
# ============================================================

count = get_feedback_count()

print("\nTotal feedback records:", count)


# ============================================================
# TEST 3: DISPLAY ALL FEEDBACK
# ============================================================

print("\nStored feedback:")

for row in get_feedback():
    print(row)


# ============================================================
# TEST 4: DISPLAY CORRECTED FEEDBACK
# ============================================================

print("\nCorrected feedback:")

for row in get_corrected_feedback():
    print(row)


# ============================================================
# REMOVE OLD TEST RECORDS
# ============================================================

connection = get_connection()
cursor = connection.cursor()

cursor.execute("""
    DELETE FROM feedback
    WHERE message LIKE 'TEST_CONSENSUS_%'
""")

connection.commit()
connection.close()


# ============================================================
# TEST 5: SAME MESSAGE + SPAM × 5
# ============================================================

for _ in range(5):
    save_feedback(
        "TEST_CONSENSUS_A",
        "ham",
        "spam"
    )


# ============================================================
# TEST 6: SAME MESSAGE + MIXED LABELS
# ============================================================

# Spam × 3
for _ in range(3):
    save_feedback(
        "TEST_CONSENSUS_B",
        "ham",
        "spam"
    )

# Ham × 2
for _ in range(2):
    save_feedback(
        "TEST_CONSENSUS_B",
        "spam",
        "ham"
    )


# ============================================================
# TEST 7: SAME MESSAGE + HAM × 5
# ============================================================

for _ in range(5):
    save_feedback(
        "TEST_CONSENSUS_C",
        "spam",
        "ham"
    )


# ============================================================
# TEST 8: GET RETRAINING CANDIDATES
# ============================================================

candidates = get_retraining_candidates()

print("\n========================================")
print("RETRAINING CANDIDATES")
print("========================================")

for message, label, report_count in candidates:
    print(
        f"Message: {message} | "
        f"Label: {label} | "
        f"Reports: {report_count}"
    )


# ============================================================
# TEST 9: VERIFY EXPECTED RESULTS
# ============================================================

candidate_dict = {
    (message, label): report_count
    for message, label, report_count in candidates
}


# A should qualify:
# spam × 5
assert candidate_dict.get(
    ("TEST_CONSENSUS_A", "spam")
) == 5


# C should qualify:
# ham × 5
assert candidate_dict.get(
    ("TEST_CONSENSUS_C", "ham")
) == 5


# B should NOT qualify:
# spam × 3
assert (
    ("TEST_CONSENSUS_B", "spam")
    not in candidate_dict
)


# B should NOT qualify:
# ham × 2
assert (
    ("TEST_CONSENSUS_B", "ham")
    not in candidate_dict
)


# ============================================================
# FINAL RESULT
# ============================================================

print("\n========================================")
print("ALL DATABASE TESTS PASSED!")
print("========================================")


# ============================================================
# CLEAN UP TEST RECORDS
# ============================================================

connection = get_connection()
cursor = connection.cursor()

cursor.execute("""
    DELETE FROM feedback
    WHERE message LIKE 'TEST_CONSENSUS_%'
""")

connection.commit()
connection.close()

print("\nTest feedback records removed.")
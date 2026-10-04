from database import (
    initialize_database,
    save_feedback,
    get_feedback,
    get_feedback_count,
    get_corrected_feedback
)


# Initialize database
initialize_database()

# Test feedback
message = "Your account has been credited with $1000"
prediction = "spam"
correct_label = "ham"
# Save feedback
feedback_id = save_feedback(
    message,
    prediction,
    correct_label
)

print("Feedback saved successfully!")
print("Feedback ID:", feedback_id)

# Show total feedback
count = get_feedback_count()
print("Total feedback records:", count)

# Display all feedback
print("\nStored feedback:")

for row in get_feedback():
    print(row)

print("\nCorrected feedback for ML retraining:")

for row in get_corrected_feedback():
    print(row)
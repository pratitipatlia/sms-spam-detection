import csv
from pathlib import Path
from datetime import datetime


FEEDBACK_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "feedback.csv"
)


def save_feedback(message, model_prediction, correct_label):
    """
    Save a user's corrected prediction.

    Parameters:
        message (str): Original SMS
        model_prediction (str): Prediction made by the model
        correct_label (str): Correct label provided by the user
    """

    FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)

    file_exists = FEEDBACK_FILE.exists()

    with open(FEEDBACK_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "message",
                "model_prediction",
                "correct_label",
                "timestamp"
            ])

        writer.writerow([
            message,
            model_prediction,
            correct_label,
            datetime.now().isoformat()
        ])

    print("Feedback saved successfully.")
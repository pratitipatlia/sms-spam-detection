import pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC

from .model_utils import save_model


# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET_PATH = PROJECT_ROOT / "data" / "processed" / "english_hindi.csv"
FEEDBACK_PATH = PROJECT_ROOT / "data" / "feedback.csv"


def retrain_model(min_feedback=20):
    # Load original training data
    data = pd.read_csv(DATASET_PATH)

    training_data = data[["labels", "clean_text"]].dropna()

    # Load user feedback
    try:
        feedback = pd.read_csv(FEEDBACK_PATH)

        feedback_data = feedback[
            ["correct_label", "message"]
        ].rename(
            columns={
                "correct_label": "labels",
                "message": "clean_text"
            }
        )

        # Check whether enough feedback is available
        if len(feedback_data) < min_feedback:
            print(
                f"Only {len(feedback_data)} feedback examples available."
            )
            print(
                f"At least {min_feedback} are required for retraining."
            )
            return

        # Add corrected feedback to training data
        training_data = pd.concat(
            [training_data, feedback_data],
            ignore_index=True
        )

        print("Feedback examples added:", len(feedback_data))

    except FileNotFoundError:
        print("No feedback file found. Using original dataset only.")
        return

    # Remove duplicate messages
    training_data = training_data.drop_duplicates(
        subset=["clean_text"]
    )

    X = training_data["clean_text"]
    y = training_data["labels"]

    # Create character TF-IDF
    vectorizer = TfidfVectorizer(
        analyzer="char",
        ngram_range=(2, 5),
        min_df=2,
        max_features=100000
    )

    X_tfidf = vectorizer.fit_transform(X)

    # Train updated SVM
    model = LinearSVC(random_state=42)
    model.fit(X_tfidf, y)

    # Save updated model
    save_model(model, vectorizer)

    print("Model retrained successfully.")
    print("Total training examples:", len(training_data))


if __name__ == "__main__":
    retrain_model()
import pandas as pd
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

from .model_utils import save_model, load_model

from database.database import (
    initialize_database,
    get_retraining_candidates,
    mark_retraining_candidates_as_used
)


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "english_hindi.csv"
)


# ============================================================
# CONFIGURATION
# ============================================================

MIN_FEEDBACK_REPORTS = 5

TEST_SIZE = 0.20

RANDOM_STATE = 42


# ============================================================
# LOAD ORIGINAL DATASET
# ============================================================

def load_training_data():
    """
    Load the original SMS dataset.

    Returns:
        pandas.DataFrame
    """

    data = pd.read_csv(DATASET_PATH)

    required_columns = ["labels", "clean_text"]

    for column in required_columns:
        if column not in data.columns:
            raise ValueError(
                f"Required column '{column}' "
                f"not found in dataset."
            )

    data = data[required_columns].dropna()

    data["labels"] = (
        data["labels"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    data["clean_text"] = (
        data["clean_text"]
        .astype(str)
        .str.strip()
    )

    # Keep only valid labels
    data = data[
        data["labels"].isin(["spam", "ham"])
    ]

    # Remove empty messages
    data = data[
        data["clean_text"] != ""
    ]

    return data


# ============================================================
# CREATE VECTORIZER
# ============================================================

def create_vectorizer():
    """
    Create the same character-level TF-IDF configuration
    used by the original model.
    """

    return TfidfVectorizer(
        analyzer="char",
        ngram_range=(2, 5),
        min_df=2,
        max_features=100000
    )


# ============================================================
# TRAIN MODEL
# ============================================================

def train_model(training_data):
    """
    Train a Linear SVM using the supplied training data.

    Returns:
        model
        vectorizer
    """

    X = training_data["clean_text"]
    y = training_data["labels"]

    vectorizer = create_vectorizer()

    X_tfidf = vectorizer.fit_transform(X)

    model = LinearSVC(
        random_state=RANDOM_STATE
    )

    model.fit(X_tfidf, y)

    return model, vectorizer


# ============================================================
# EVALUATE MODEL
# ============================================================

def evaluate_model(model, vectorizer, test_data):
    """
    Evaluate a model on the same test dataset.
    """

    X_test = test_data["clean_text"]
    y_test = test_data["labels"]

    X_test_tfidf = vectorizer.transform(X_test)

    predictions = model.predict(X_test_tfidf)

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    precision = precision_score(
        y_test,
        predictions,
        pos_label="spam",
        zero_division=0
    )

    recall = recall_score(
        y_test,
        predictions,
        pos_label="spam",
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        predictions,
        pos_label="spam",
        zero_division=0
    )

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1
    }


# ============================================================
# RETRAIN MODEL
# ============================================================

def retrain_model(min_feedback=MIN_FEEDBACK_REPORTS):
    """
    Retrain the SMS spam classifier using feedback that has
    reached the required consensus threshold.

    The currently saved production model is used as the
    baseline. A new candidate model is trained using the
    original training portion plus eligible feedback.

    Both models are evaluated on the same 20% test set.

    The candidate model replaces the production model only
    when its F1 score is at least as good as the current
    production model.
    """

    print("\n========================================")
    print("STARTING MODEL RETRAINING")
    print("========================================")

    # --------------------------------------------------------
    # Initialize database
    # --------------------------------------------------------

    initialize_database()

    # --------------------------------------------------------
    # Get eligible feedback
    # --------------------------------------------------------

    candidates = get_retraining_candidates(
        min_reports=min_feedback
    )

    if not candidates:

        print("\nNo feedback has reached the")
        print(f"{min_feedback}-report consensus threshold.")

        print("\nNo retraining performed.")

        return

    print("\nRetraining candidates:")

    for message, label, count in candidates:

        print(
            f"- {message} | "
            f"{label} | "
            f"{count} reports"
        )

    # --------------------------------------------------------
    # Load original dataset
    # --------------------------------------------------------

    original_data = load_training_data()

    print(
        "\nOriginal training examples:",
        len(original_data)
    )

    # --------------------------------------------------------
    # Create deterministic 80/20 split
    # --------------------------------------------------------

    train_data, test_data = train_test_split(
        original_data,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=original_data["labels"]
    )

    print(
        "Training split:",
        len(train_data)
    )

    print(
        "Test split:",
        len(test_data)
    )

    # --------------------------------------------------------
    # Load CURRENT production model
    # --------------------------------------------------------

    print(
        "\nLoading current production model..."
    )

    baseline_model, baseline_vectorizer = load_model()

    # --------------------------------------------------------
    # Evaluate CURRENT production model
    # --------------------------------------------------------

    print(
        "\nEvaluating current production model..."
    )

    baseline_metrics = evaluate_model(
        baseline_model,
        baseline_vectorizer,
        test_data
    )

    print(
        "\nCurrent production model performance:"
    )

    print(
        f"Accuracy : {baseline_metrics['accuracy']:.4f}"
    )

    print(
        f"Precision: {baseline_metrics['precision']:.4f}"
    )

    print(
        f"Recall   : {baseline_metrics['recall']:.4f}"
    )

    print(
        f"F1 Score : {baseline_metrics['f1']:.4f}"
    )

    # --------------------------------------------------------
    # Convert feedback candidates into training data
    # --------------------------------------------------------

    feedback_rows = []

    for message, label, count in candidates:

        feedback_rows.append({
            "labels": label,
            "clean_text": message
        })

    feedback_data = pd.DataFrame(
        feedback_rows
    )

    print(
        "\nEligible feedback examples:",
        len(feedback_data)
    )

    # --------------------------------------------------------
    # Add feedback to training data
    # --------------------------------------------------------

    updated_training_data = pd.concat(
        [
            train_data,
            feedback_data
        ],
        ignore_index=True
    )

    # --------------------------------------------------------
    # Remove duplicate messages
    #
    # If feedback contains a corrected label for an existing
    # training message, keep the feedback version.
    # --------------------------------------------------------

    updated_training_data = (
        updated_training_data
        .drop_duplicates(
            subset=["clean_text"],
            keep="last"
        )
    )

    print(
        "Updated training examples:",
        len(updated_training_data)
    )

    # --------------------------------------------------------
    # Train candidate model
    # --------------------------------------------------------

    print(
        "\nTraining candidate model..."
    )

    candidate_model, candidate_vectorizer = train_model(
        updated_training_data
    )

    # --------------------------------------------------------
    # Evaluate candidate model
    # --------------------------------------------------------

    candidate_metrics = evaluate_model(
        candidate_model,
        candidate_vectorizer,
        test_data
    )

    print(
        "\nCandidate model performance:"
    )

    print(
        f"Accuracy : {candidate_metrics['accuracy']:.4f}"
    )

    print(
        f"Precision: {candidate_metrics['precision']:.4f}"
    )

    print(
        f"Recall   : {candidate_metrics['recall']:.4f}"
    )

    print(
        f"F1 Score : {candidate_metrics['f1']:.4f}"
    )

    # --------------------------------------------------------
    # Compare models
    # --------------------------------------------------------

    print(
        "\n========================================"
    )

    print(
        "MODEL COMPARISON"
    )

    print(
        "========================================"
    )

    print(
        f"Current Model F1 : "
        f"{baseline_metrics['f1']:.4f}"
    )

    print(
        f"Candidate F1     : "
        f"{candidate_metrics['f1']:.4f}"
    )

    # --------------------------------------------------------
    # Save candidate only if it is at least as good
    # --------------------------------------------------------

    if candidate_metrics["f1"] >= baseline_metrics["f1"]:

        print(
            "\nCandidate model passed evaluation."
        )

        save_model(
            candidate_model,
            candidate_vectorizer
        )

        # Mark feedback as used only after the candidate
        # model has successfully been saved.
        mark_retraining_candidates_as_used(
            candidates
        )

        print(
            "\nNew model saved successfully."
        )

        print(
            "Feedback marked as used for retraining."
        )

    else:

        print(
            "\nCandidate model did not improve F1 score."
        )

        print(
            "Existing production model was NOT replaced."
        )

        print(
            "Feedback remains available for future "
            "retraining."
        )

    print(
        "\n========================================"
    )

    print(
        "RETRAINING COMPLETE"
    )

    print(
        "========================================"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    retrain_model()
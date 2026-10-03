import joblib
from pathlib import Path


MODEL_DIR = Path(__file__).resolve().parent.parent / "models"

MODEL_PATH = MODEL_DIR / "spam_classifier.pkl"
VECTORIZER_PATH = MODEL_DIR / "tfidf_vectorizer.pkl"


def save_model(model, vectorizer):
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)

    print("Model and vectorizer saved successfully.")


def load_model():
    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)

    return model, vectorizer
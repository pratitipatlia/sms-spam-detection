from .model_utils import load_model

# Load the trained model and TF-IDF vectorizer
model, vectorizer = load_model()


def reload_model():
    """Reload the model and vectorizer from disk after retraining."""
    global model, vectorizer
    model, vectorizer = load_model()


def predict_sms(message):
    """
    Predict whether an SMS is spam or ham.

    Parameters:
        message (str): SMS message to classify

    Returns:
        str: 'spam' or 'ham'
    """
    message_features = vectorizer.transform([message])
    prediction = model.predict(message_features)[0]

    return prediction
from flask import Flask, request, jsonify
from flask_cors import CORS

from src.spam_classifier import predict_sms
from src.feedback_manager import save_feedback
from database.database import initialize_database, get_retraining_candidates
from src.model_training import retrain_model
from src.spam_classifier import predict_sms, reload_model
app = Flask(__name__)
CORS(app)
initialize_database()

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "SMS Spam Detection API is running"
    })


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({
            "error": "Message is required"
        }), 400

    message = data["message"]

    if not isinstance(message, str) or not message.strip():
        return jsonify({
            "error": "Message must be a non-empty string"
        }), 400

    try:
        prediction = predict_sms(message)

        return jsonify({
            "prediction": prediction
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500



@app.route("/feedback", methods=["POST"])
def feedback():
    data = request.get_json()

    required_fields = [
        "message",
        "prediction",
        "correct_label"
    ]

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    for field in required_fields:
        if field not in data:
            return jsonify({
                "error": f"{field} is required"
            }), 400

    try:
        save_feedback(
            data["message"],
            data["prediction"],
            data["correct_label"]
        )

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

    # Feedback has been saved. Check for consensus.
    try:
        candidates = get_retraining_candidates(min_reports=5)

        if candidates:
            print("Eligible feedback found. Starting automatic retraining...")

            retrain_model()

            print("Automatic retraining finished.")
            reload_model()

    except Exception as e:
        # Feedback is already saved, so do not report the submission
        # as failed just because retraining encountered an error.
        app.logger.exception("Automatic retraining failed: %s", e)

    return jsonify({
        "message": "Feedback recorded successfully"
    }), 200



if __name__ == "__main__":
    app.run(debug=True)
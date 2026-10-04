from flask import Flask, request, jsonify
from flask_cors import CORS

from src.spam_classifier import predict_sms
from src.feedback_manager import save_feedback

app = Flask(__name__)
CORS(app)


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

        return jsonify({
            "message": "Feedback recorded successfully"
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
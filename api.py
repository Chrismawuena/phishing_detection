from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import re

app = Flask(__name__)

# Allow requests from the Chrome extension (content.js / background.js run
# on mail.google.com, not on your Flask domain, so CORS must be open here)
CORS(app)

# ---------------------------------------------------------------------
# Load model + vectorizer once at startup (not per-request)
# ---------------------------------------------------------------------
with open("models/email_model.pkl", "rb") as f:
    model = pickle.load(f)

with open("models/email_vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

# Secondary heuristic signal — NOT used for the classification itself,
# just surfaced to the user as "why this was flagged" context.
SUSPICIOUS_WORDS = [
    "verify",
    "urgent",
    "password",
    "login",
    "click here",
    "account suspended",
    "bank",
    "security alert",
]


def find_suspicious_words(text):
    """Return which suspicious words appear in the email, for display only."""
    text_lower = text.lower()
    return [w for w in SUSPICIOUS_WORDS if w in text_lower]


def get_phishing_confidence(model, vector):
    """
    Try to get a confidence score from the model.
    Falls back to a plain label if the model doesn't support predict_proba
    (e.g. some SVMs without probability=True).
    Returns (is_phishing: bool, confidence: float 0-1)
    """
    label = model.predict(vector)[0]
    is_phishing = bool(label == 1 or label == "phishing")

    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(vector)[0]
        # Assume class index 1 = phishing. If your model's classes_ are
        # labeled differently, adjust this index.
        classes = list(model.classes_)
        try:
            phishing_idx = classes.index(1)
        except ValueError:
            try:
                phishing_idx = classes.index("phishing")
            except ValueError:
                phishing_idx = 1 if len(classes) > 1 else 0
        confidence = float(proba[phishing_idx])
    else:
        # No probability support — just report full confidence in the label
        confidence = 1.0 if is_phishing else 0.0

    return is_phishing, confidence


@app.route("/scan", methods=["POST"])
def scan():
    data = request.get_json(silent=True)

    if not data or "text" not in data:
        return jsonify({"error": "Missing 'text' field in request body"}), 400

    email_text = data["text"]

    if not isinstance(email_text, str) or not email_text.strip():
        return jsonify({"error": "'text' must be a non-empty string"}), 400

    try:
        vector = vectorizer.transform([email_text])
        is_phishing, confidence = get_phishing_confidence(model, vector)
        flagged_words = find_suspicious_words(email_text)
    except Exception as e:
        # Don't leak internals to the client, but log server-side
        app.logger.error(f"Scan failed: {e}")
        return jsonify({"error": "Failed to analyze email"}), 500

    return jsonify({
        "is_phishing": is_phishing,
        "confidence": round(confidence, 4),
        "suspicious_words_found": flagged_words,
    })


@app.route("/health", methods=["GET"])
def health():
    """Simple endpoint so the extension can check if the API is up."""
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
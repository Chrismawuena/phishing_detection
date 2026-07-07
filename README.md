# AI Phishing Detector - Gmail Chrome Extension

A Chrome extension that uses machine learning to detect phishing emails in Gmail and alerts you with a browser notification in real time.

## How It Works

1. When you open an email in Gmail, the extension automatically extracts the email text
2. It sends the text to a Flask API hosted on Render
3. The API runs the text through a trained Logistic Regression model
4. You receive a browser notification telling you whether the email is safe or suspicious, along with a confidence percentage

## Project Structure

```
phishing_detector/
├── api.py                        # Flask API
├── train_email_model.py          # Model training script
├── requirements.txt              # Python dependencies
├── datasets/
│   └── Email scam.csv            # Training dataset
├── models/                       # Generated on deploy (not in repo)
│   ├── email_model.pkl
│   └── email_vectorizer.pkl
└── gmail_phishing_extension/
    ├── manifest.json
    ├── background.js             # Calls API, fires notifications
    ├── content.js                # Extracts email text from Gmail
    ├── popup.html                # Extension popup UI
    ├── popup.js                  # Popup logic
    └── icon.png
```

## Installation (For Testers)

### Step 1 — Download the extension
- Download and unzip the `gmail_phishing_extension` folder

### Step 2 — Load in Chrome
1. Open Chrome and go to `chrome://extensions`
2. Enable **Developer mode** (top right toggle)
3. Click **Load unpacked**
4. Select the `gmail_phishing_extension` folder

### Step 3 — Use it
- Open Gmail in Chrome
- Click any email
- A notification will appear telling you if the email is safe or suspicious

No setup required — the API is already hosted online.

## API

The Flask API is hosted on Render:

- **Base URL:** `https://phishing-detection-1-8y6z.onrender.com`
- **Endpoint:** `POST /scan`
- **Request body:** `{ "text": "email body text here" }`
- **Response:** `{ "is_phishing": true/false, "confidence": 0.75, "suspicious_words_found": ["urgent", "verify"] }`

> Note: The free Render tier spins down after inactivity. The first scan after a period of no use may take 30-60 seconds while the server wakes up.

## Model Details

- **Algorithm:** Logistic Regression with `class_weight="balanced"`
- **Features:** TF-IDF with bigrams, 10,000 features
- **Training data:** 5,572 emails (4,825 ham, 747 spam/phishing)
- **Accuracy:** 98% on test set
- **Phishing precision:** 96%

## Tech Stack

- Python, Flask, scikit-learn, pandas
- Chrome Extension (Manifest V3)
- Deployed on Render.com

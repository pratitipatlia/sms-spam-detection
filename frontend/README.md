# SpamShield AI — SMS Spam Detection Frontend

A modern, responsive, accessible web application for an AI-powered SMS Spam Detection System. Built with **React**, **Vite**, **Vanilla CSS (Design Tokens)**, and **Lucide React**.

---

## Overview

SpamShield AI is the frontend interface for analyzing SMS text messages, predicting whether they are **SPAM** or legitimate (**HAM**), and collecting user feedback to help improve the detection system over time.

### Key Features
- **Modern SaaS Aesthetics**: Minimalist light theme with crisp typography, subtle shadows, and plenty of whitespace.
- **Snapshot Isolation**: The analyzed message is saved as a frozen snapshot. Editing the textarea after prediction does not compromise the displayed result or feedback submission.
- **Accessible Indicators**: Results are communicated through icons, text badges, and color indicators (never color alone).
- **Keyboard Shortcuts**: Quickly analyze messages using `Ctrl+Enter` (Windows/Linux) or `Cmd+Enter` (macOS).
- **Live Character Counter & Clear Action**: Helpful input helpers without imposing artificial character restrictions.
- **Two-Stage Feedback Loop**:
  - Direct confirmation for correct predictions ("Yes, correct").
  - Correction panel with guardrails for incorrect predictions ("No, incorrect").
  - Prevention of duplicate submissions while keeping retry controls active if an API request fails.
- **Zero Mock Predictions**: If the backend is unreachable or returns an error, helpful error states are displayed instead of fake predictions.

---

## Project Structure

```text
frontend/
├── public/                 # Static assets
├── src/
│   ├── components/
│   │   ├── Navbar.jsx           # Brand header, Home link, and AI-Powered badge
│   │   ├── Hero.jsx             # Hero title, subtitle, and protection badge
│   │   ├── DetectionForm.jsx    # Textarea, live counter, submit & clear buttons
│   │   ├── PredictionResult.jsx # SPAM/HAM badge, explanation, snapshot & reset button
│   │   └── FeedbackSection.jsx  # Accuracy feedback, correction selector & confirmation
│   ├── services/
│   │   └── api.js               # Centralized API service with timeout & error handling
│   ├── App.jsx                  # Main orchestrator & state management
│   ├── main.jsx                 # Application entry point
│   └── index.css                # CSS custom properties, responsive layout, animations
├── .env                         # Local environment variables
├── .env.example                 # Example environment configuration
├── .gitignore                   # Git ignore patterns
├── index.html                   # HTML template with accessible viewport & meta tags
├── package.json                 # Project dependencies & scripts
├── vite.config.js               # Vite build and dev server configuration
└── README.md                    # Documentation & setup guide
```

---

## Prerequisites

- [Node.js](https://nodejs.org/) (v18.0.0 or higher recommended)
- `npm` (v9.0.0 or higher)

---

## Installation & Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure Environment Variables:**
   A `.env` file is already pre-configured for local development. To customize the backend URL, refer to `.env.example`:
   ```env
   VITE_API_BASE_URL=http://localhost:5000
   ```

4. **Start the development server:**
   ```bash
   npm run dev
   ```
   The application will be accessible at: `http://localhost:5173`

5. **Build for production:**
   ```bash
   npm run build
   ```
   The compiled assets will be placed in the `dist/` directory.

---

## Backend API Specification & Integration

The frontend expects a Flask backend running on `http://localhost:5000` exposing two JSON endpoints:

### 1. Predict SMS
- **Endpoint:** `POST /predict`
- **Headers:** `Content-Type: application/json`
- **Request Body:**
  ```json
  {
    "message": "Congratulations! You won a free prize."
  }
  ```
- **Response Body:**
  ```json
  {
    "prediction": "spam"
  }
  ```
  *(Expected values: `"spam"` or `"ham"`, case-insensitive)*

### 2. Submit Feedback
- **Endpoint:** `POST /feedback`
- **Headers:** `Content-Type: application/json`
- **Request Body:**
  ```json
  {
    "message": "Congratulations! You won a free prize.",
    "prediction": "spam",
    "correct_label": "ham"
  }
  ```
- **Response Body:** Any HTTP `2xx` status code.

---

## IMPORTANT: Backend CORS Configuration (For the Flask Developer)

Because Vite runs on `http://localhost:5173` and Flask typically runs on `http://localhost:5000`, the browser treats requests between them as Cross-Origin Resource Sharing (CORS).

To allow the frontend to communicate with your Flask backend, the Flask developer **must enable CORS**.

### In Flask (`app.py`):
```python
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)

# Allow requests from the Vite frontend
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}})
```

Install `flask-cors` in your Python environment:
```bash
pip install flask-cors
```

/**
 * Centralized API Service for SpamShield AI
 * Handles communication with the Flask backend for SMS prediction and feedback.
 */

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000').replace(/\/+$/, '');
const REQUEST_TIMEOUT_MS = 15000;

/**
 * Helper to perform fetch requests with an automatic timeout using AbortController.
 *
 * @param {string} endpoint - API path (e.g. '/predict')
 * @param {object} options - Fetch options
 * @returns {Promise<Response>}
 */
async function fetchWithTimeout(endpoint, options = {}) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const url = `${API_BASE_URL}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    return response;
  } finally {
    clearTimeout(timeoutId);
  }
}

/**
 * Parse an error response gracefully, extracting server-provided message if present.
 *
 * @param {Response} response
 * @returns {Promise<string>}
 */
async function extractErrorMessage(response) {
  try {
    const text = await response.text();
    if (!text) {
      return `Server returned status ${response.status} (${response.statusText || 'Error'}).`;
    }
    try {
      const data = JSON.parse(text);
      if (data && typeof data === 'object') {
        if (data.error && typeof data.error === 'string') return data.error;
        if (data.message && typeof data.message === 'string') return data.message;
      }
    } catch {
      // Not JSON, fall back to plain text if concise
      if (text.length <= 150) {
        return text;
      }
    }
    return `Server returned status ${response.status}.`;
  } catch {
    return `Request failed with status ${response.status}.`;
  }
}

/**
 * Check if an HTTP response is considered successful.
 * Centralized in one place so it can be adapted easily if the backend team changes specs.
 *
 * @param {Response} response
 * @returns {boolean}
 */
export function isSuccessResponse(response) {
  return response.ok; // True for any HTTP 2xx status code
}

/**
 * Predict whether an SMS message is spam or legitimate (ham).
 *
 * @param {string} message - The SMS message text
 * @returns {Promise<{ prediction: 'spam' | 'ham' }>}
 */
export async function predictSMS(message) {
  if (typeof message !== 'string' || !message.trim()) {
    throw new Error('Please enter a valid SMS message to analyze.');
  }

  try {
    const response = await fetchWithTimeout('/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    });

    if (!isSuccessResponse(response)) {
      const errMsg = await extractErrorMessage(response);
      throw new Error(errMsg);
    }

    let data;
    try {
      data = await response.json();
    } catch {
      throw new Error('Invalid response received from detection service. Expected JSON format.');
    }

    if (!data || typeof data.prediction !== 'string') {
      throw new Error('The detection response is missing a prediction result.');
    }

    const normalizedPrediction = data.prediction.trim().toLowerCase();

    if (normalizedPrediction !== 'spam' && normalizedPrediction !== 'ham') {
      throw new Error(`Unexpected prediction received from model: "${data.prediction}". Expected "spam" or "ham".`);
    }

    return {
      prediction: normalizedPrediction,
    };
  } catch (err) {
    if (err.name === 'AbortError') {
      throw new Error('Request timed out after 15 seconds. The server took too long to respond. Please try again.');
    }

    // Network failures, CORS issues, or connection refused
    if (err instanceof TypeError && err.message.includes('fetch')) {
      throw new Error('Unable to connect to the detection service. Please ensure the backend is running and try again.');
    }

    // Re-throw handled errors
    throw err;
  }
}

/**
 * Submit user feedback on model accuracy to the backend.
 *
 * @param {object} payload
 * @param {string} payload.message - Original analyzed SMS message
 * @param {'spam'|'ham'} payload.prediction - The model's prediction
 * @param {'spam'|'ham'} payload.correct_label - The user's confirmed correct label
 * @returns {Promise<{ success: boolean }>}
 */
export async function submitFeedback({ message, prediction, correct_label }) {
  if (!message || !prediction || !correct_label) {
    throw new Error('Missing required feedback parameters.');
  }

  try {
    const response = await fetchWithTimeout('/feedback', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        prediction,
        correct_label,
      }),
    });

    if (!isSuccessResponse(response)) {
      const errMsg = await extractErrorMessage(response);
      throw new Error(errMsg);
    }

    return { success: true };
  } catch (err) {
    if (err.name === 'AbortError') {
      throw new Error('Feedback submission timed out after 15 seconds. Please try again.');
    }

    if (err instanceof TypeError && err.message.includes('fetch')) {
      throw new Error('Unable to connect to the feedback service. Please ensure the backend is running and try again.');
    }

    throw err;
  }
}

import React from 'react';
import { AlertTriangle, CheckCircle2, RotateCcw } from 'lucide-react';

/**
 * PredictionResult Component
 * Displays the model's classification outcome, visual indicators, explanation,
 * snapshot of the analyzed message, and an action to analyze another message.
 */
export default function PredictionResult({
  prediction,
  analyzedMessage,
  onReset,
  resultRef,
}) {
  if (!prediction) {
    return null;
  }

  const isSpam = prediction === 'spam';

  return (
    <section
      ref={resultRef}
      className={`card result-card ${isSpam ? 'is-spam' : 'is-ham'}`}
      aria-labelledby="result-heading"
      tabIndex={-1}
    >
      <div className="card-header">
        <h2 id="result-heading" className="card-title">
          Analysis Result
        </h2>
      </div>

      <div className="result-badge-container">
        <div
          className={`result-badge ${isSpam ? 'badge-spam' : 'badge-ham'}`}
          role="status"
          aria-label={`Classification result: ${isSpam ? 'Spam' : 'Legitimate Ham'}`}
        >
          {isSpam ? (
            <>
              <AlertTriangle size={22} aria-hidden="true" />
              <span>SPAM</span>
            </>
          ) : (
            <>
              <CheckCircle2 size={22} aria-hidden="true" />
              <span>HAM</span>
            </>
          )}
        </div>
      </div>

      <p className="result-explanation">
        {isSpam
          ? 'The model classified this message as spam.'
          : 'The model classified this message as legitimate (ham).'}
      </p>

      <div className="analyzed-message-box">
        <div className="analyzed-label">Analyzed Message Snapshot</div>
        <div className="analyzed-text">{analyzedMessage}</div>
      </div>

      <div className="result-actions">
        <button
          type="button"
          onClick={onReset}
          className="btn-secondary"
          aria-label="Analyze another message and reset current result"
        >
          <RotateCcw size={15} aria-hidden="true" />
          <span>Analyze another message</span>
        </button>
      </div>
    </section>
  );
}

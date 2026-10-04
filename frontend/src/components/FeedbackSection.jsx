import React from 'react';
import { Check, X, ThumbsUp, ThumbsDown, Loader2, AlertCircle, CheckCircle } from 'lucide-react';

/**
 * FeedbackSection Component
 * Allows user to validate model accuracy or submit corrected classifications.
 * Prevents duplicates, handles loading, retries, and resets cleanly.
 */
export default function FeedbackSection({
  prediction,
  feedbackState,
  onSelectYes,
  onSelectNo,
  onSelectCorrectionOption,
  onSubmitCorrection,
}) {
  const {
    status,
    error,
    showCorrectionChoice,
    selectedCorrection,
    validationMessage,
  } = feedbackState;

  const isSubmitting = status === 'submitting';
  const isSubmitted = status === 'submitted';

  return (
    <section className="feedback-card" aria-labelledby="feedback-heading">
      <h3 id="feedback-heading" className="feedback-question">
        Was this prediction correct?
      </h3>

      {isSubmitted ? (
        <div className="alert alert-success" role="status" aria-live="polite">
          <CheckCircle size={18} className="alert-icon" aria-hidden="true" />
          <div>
            <strong>Feedback received: </strong>
            <span>Thank you. Your feedback has been recorded.</span>
          </div>
        </div>
      ) : (
        <>
          <div className="feedback-binary-buttons">
            <button
              type="button"
              className="btn-feedback"
              onClick={onSelectYes}
              disabled={isSubmitting || isSubmitted}
              aria-label="Confirm prediction is correct"
            >
              <ThumbsUp size={16} aria-hidden="true" />
              <span>Yes, correct</span>
            </button>

            <button
              type="button"
              className="btn-feedback"
              onClick={onSelectNo}
              disabled={isSubmitting || isSubmitted}
              aria-label="Mark prediction as incorrect"
              aria-expanded={showCorrectionChoice}
            >
              <ThumbsDown size={16} aria-hidden="true" />
              <span>No, incorrect</span>
            </button>
          </div>

          {showCorrectionChoice && (
            <div className="correction-panel">
              <p className="correction-title" id="correction-label">
                What is the correct classification?
              </p>

              <div
                className="correction-options"
                role="radiogroup"
                aria-labelledby="correction-label"
              >
                <button
                  type="button"
                  role="radio"
                  aria-checked={selectedCorrection === 'spam'}
                  className={`correction-option-btn ${selectedCorrection === 'spam' ? 'selected' : ''}`}
                  onClick={() => onSelectCorrectionOption('spam')}
                  disabled={isSubmitting}
                >
                  <span>SPAM</span>
                </button>

                <button
                  type="button"
                  role="radio"
                  aria-checked={selectedCorrection === 'ham'}
                  className={`correction-option-btn ${selectedCorrection === 'ham' ? 'selected' : ''}`}
                  onClick={() => onSelectCorrectionOption('ham')}
                  disabled={isSubmitting}
                >
                  <span>HAM</span>
                </button>
              </div>

              {validationMessage && (
                <div className="alert alert-error" role="alert" style={{ marginBlockEnd: '1rem' }}>
                  <AlertCircle size={16} className="alert-icon" aria-hidden="true" />
                  <span>{validationMessage}</span>
                </div>
              )}

              <div className="correction-actions">
                <button
                  type="button"
                  className="btn-primary"
                  onClick={onSubmitCorrection}
                  disabled={!selectedCorrection || isSubmitting}
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 size={16} className="spinner" aria-hidden="true" />
                      <span>Submitting feedback...</span>
                    </>
                  ) : (
                    <span>Submit correction</span>
                  )}
                </button>
              </div>
            </div>
          )}

          {error && (
            <div className="alert alert-error" role="alert">
              <AlertCircle size={18} className="alert-icon" aria-hidden="true" />
              <div>
                <strong>Error submitting feedback: </strong>
                <span>{error}</span>
              </div>
            </div>
          )}
        </>
      )}
    </section>
  );
}

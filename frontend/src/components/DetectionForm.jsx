import React, { useRef, useEffect } from 'react';
import { Loader2, Trash2, Send, Lock, AlertCircle } from 'lucide-react';

/**
 * DetectionForm Component
 * Renders the SMS input card, live character counter, clear action, submit button, and error state.
 */
export default function DetectionForm({
  message,
  onMessageChange,
  onAnalyze,
  isLoading,
  error,
  textareaRef,
}) {
  const isInputEmpty = !message || !message.trim();

  const handleKeyDown = (e) => {
    // Submit on Ctrl+Enter (Windows/Linux) or Cmd+Enter (macOS)
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter' && !e.nativeEvent.isComposing) {
      e.preventDefault();
      if (!isInputEmpty && !isLoading) {
        onAnalyze();
      }
    }
  };

  const handleClear = () => {
    onMessageChange('');
    if (textareaRef?.current) {
      textareaRef.current.focus();
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!isInputEmpty && !isLoading) {
      onAnalyze();
    }
  };

  return (
    <section className="card" aria-labelledby="analyze-card-title">
      <div className="card-header">
        <h2 id="analyze-card-title" className="card-title">
          Analyze an SMS
        </h2>
        <p className="card-description">
          Paste a message below to check whether it's spam or legitimate.
        </p>
      </div>

      <form onSubmit={handleSubmit} noValidate>
        <div className="form-group">
          <label htmlFor="sms-input" className="visually-hidden">
            SMS Message Content
          </label>
          <div className="textarea-wrapper">
            <textarea
              id="sms-input"
              ref={textareaRef}
              className="detection-textarea"
              rows={5}
              placeholder="Paste your SMS message here..."
              value={message}
              onChange={(e) => onMessageChange(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isLoading}
              aria-describedby="char-counter privacy-note-text"
              aria-invalid={Boolean(error)}
              required
            />

            <div className="textarea-toolbar">
              <span id="char-counter" className="char-counter" aria-live="polite">
                {message.length} {message.length === 1 ? 'character' : 'characters'}
              </span>

              <button
                type="button"
                onClick={handleClear}
                className="clear-btn"
                disabled={isLoading || message.length === 0}
                aria-label="Clear message text"
              >
                <Trash2 size={13} aria-hidden="true" />
                <span>Clear</span>
              </button>
            </div>
          </div>
        </div>

        {error && (
          <div className="alert alert-error" role="alert" aria-live="assertive">
            <AlertCircle size={18} className="alert-icon" aria-hidden="true" />
            <div>
              <strong>Error: </strong>
              <span>{error}</span>
            </div>
          </div>
        )}

        <div className="form-actions">
          <div className="privacy-note" id="privacy-note-text">
            
            
          </div>

          <button
            type="submit"
            className="btn-primary"
            disabled={isInputEmpty || isLoading}
            aria-busy={isLoading}
          >
            {isLoading ? (
              <>
                <Loader2 size={16} className="spinner" aria-hidden="true" />
                <span>Analyzing message...</span>
              </>
            ) : (
              <>
                <Send size={15} aria-hidden="true" />
                <span>Analyze Message</span>
                <span className="kbd-shortcut" title="Press Ctrl+Enter or Cmd+Enter to analyze">
                  Ctrl+↵
                </span>
              </>
            )}
          </button>
        </div>
      </form>
    </section>
  );
}

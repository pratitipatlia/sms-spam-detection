import React, { useState, useRef } from 'react';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import DetectionForm from './components/DetectionForm';
import PredictionResult from './components/PredictionResult';
import FeedbackSection from './components/FeedbackSection';
import { predictSMS, submitFeedback } from './services/api';

const INITIAL_FEEDBACK_STATE = {
  status: 'idle', // 'idle' | 'submitting' | 'submitted' | 'error'
  error: null,
  showCorrectionChoice: false,
  selectedCorrection: null,
  validationMessage: null,
};

export default function App() {
  // Input state
  const [inputText, setInputText] = useState('');
  // Frozen snapshot of the message that was actually submitted and analyzed
  const [analyzedSnapshot, setAnalyzedSnapshot] = useState('');
  
  // Prediction states
  const [prediction, setPrediction] = useState(null); // 'spam' | 'ham' | null
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisError, setAnalysisError] = useState(null);

  // User Feedback state
  const [feedbackState, setFeedbackState] = useState(INITIAL_FEEDBACK_STATE);

  // Refs for accessibility focus & smooth scrolling
  const textareaRef = useRef(null);
  const resultRef = useRef(null);

  /**
   * Handle text changes in the detection textarea.
   * If an analysis error exists, clear it when the user starts typing again.
   */
  const handleMessageChange = (newText) => {
    setInputText(newText);
    if (analysisError) {
      setAnalysisError(null);
    }
  };

  /**
   * Submit SMS message for classification.
   */
  const handleAnalyze = async () => {
    const trimmedMessage = inputText.trim();
    if (!trimmedMessage) {
      setAnalysisError('Please enter an SMS message to analyze.');
      return;
    }

    setIsAnalyzing(true);
    setAnalysisError(null);

    try {
      const result = await predictSMS(trimmedMessage);
      
      // Save prediction and freeze the analyzed message snapshot
      setPrediction(result.prediction);
      setAnalyzedSnapshot(trimmedMessage);

      // Reset feedback state for the new prediction
      setFeedbackState(INITIAL_FEEDBACK_STATE);

      // Smooth scroll to the result after DOM renders
      setTimeout(() => {
        if (resultRef.current) {
          resultRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
          resultRef.current.focus?.();
        }
      }, 100);
    } catch (err) {
      setAnalysisError(err.message || 'An unexpected error occurred while analyzing the message.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  /**
   * Reset analysis state, clear input, and return focus to textarea.
   */
  const handleReset = () => {
    setInputText('');
    setAnalyzedSnapshot('');
    setPrediction(null);
    setAnalysisError(null);
    setFeedbackState(INITIAL_FEEDBACK_STATE);

    if (textareaRef.current) {
      textareaRef.current.focus();
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  /**
   * User confirms prediction is correct ("Yes, correct").
   */
  const handleFeedbackYes = async () => {
    if (!analyzedSnapshot || !prediction || feedbackState.status === 'submitting') {
      return;
    }

    setFeedbackState((prev) => ({
      ...prev,
      status: 'submitting',
      error: null,
      validationMessage: null,
    }));

    try {
      await submitFeedback({
        message: analyzedSnapshot,
        prediction,
        correct_label: prediction,
      });

      setFeedbackState({
        status: 'submitted',
        error: null,
        showCorrectionChoice: false,
        selectedCorrection: null,
        validationMessage: null,
      });
    } catch (err) {
      setFeedbackState((prev) => ({
        ...prev,
        status: 'error',
        error: err.message || 'Failed to submit feedback. Please try again.',
      }));
    }
  };

  /**
   * User indicates prediction is incorrect ("No, incorrect").
   */
  const handleFeedbackNo = () => {
    setFeedbackState((prev) => ({
      ...prev,
      showCorrectionChoice: true,
      error: null,
      validationMessage: null,
    }));
  };

  /**
   * User selects the corrected label (SPAM or HAM).
   */
  const handleSelectCorrectionOption = (label) => {
    setFeedbackState((prev) => ({
      ...prev,
      selectedCorrection: label,
      validationMessage: null,
    }));
  };

  /**
   * Submit correction choice.
   */
  const handleSubmitCorrection = async () => {
    const { selectedCorrection } = feedbackState;
    if (!selectedCorrection || feedbackState.status === 'submitting') {
      return;
    }

    // Guard: If user selected the same label as the model's prediction
    if (selectedCorrection === prediction) {
      setFeedbackState((prev) => ({
        ...prev,
        validationMessage: `The selected label "${selectedCorrection.toUpperCase()}" matches the model's prediction. Please choose the alternative label or select "Yes, correct".`,
      }));
      return;
    }

    setFeedbackState((prev) => ({
      ...prev,
      status: 'submitting',
      error: null,
      validationMessage: null,
    }));

    try {
      await submitFeedback({
        message: analyzedSnapshot,
        prediction,
        correct_label: selectedCorrection,
      });

      setFeedbackState({
        status: 'submitted',
        error: null,
        showCorrectionChoice: false,
        selectedCorrection: null,
        validationMessage: null,
      });
    } catch (err) {
      setFeedbackState((prev) => ({
        ...prev,
        status: 'error',
        error: err.message || 'Failed to submit feedback. Please try again.',
      }));
    }
  };

  return (
    <>
      <Navbar />

      <main id="top" className="app-container">
        <Hero />

        <DetectionForm
          message={inputText}
          onMessageChange={handleMessageChange}
          onAnalyze={handleAnalyze}
          isLoading={isAnalyzing}
          error={analysisError}
          textareaRef={textareaRef}
        />

        {prediction && (
          <>
            <PredictionResult
              prediction={prediction}
              analyzedMessage={analyzedSnapshot}
              onReset={handleReset}
              resultRef={resultRef}
            />

            <FeedbackSection
              prediction={prediction}
              feedbackState={feedbackState}
              onSelectYes={handleFeedbackYes}
              onSelectNo={handleFeedbackNo}
              onSelectCorrectionOption={handleSelectCorrectionOption}
              onSubmitCorrection={handleSubmitCorrection}
            />
          </>
        )}
      </main>

      <footer className="app-footer" role="contentinfo">
        <p>SpamShield AI — Intelligent SMS Spam Detection System</p>
        <p>Designed for integration with machine learning inference backends.</p>
      </footer>
    </>
  );
}

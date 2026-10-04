import React from 'react';

/**
 * Hero Component
 * Displays product headline and value proposition.
 */
export default function Hero() {
  return (
    <section className="hero-section" aria-labelledby="hero-heading">
      
      <h1 id="hero-heading" className="hero-headline">
        Know what's hiding in your messages.
      </h1>
      <p className="hero-subtitle">
        Analyze suspicious SMS messages with machine learning and identify potential spam before you trust the message.
      </p>
    </section>
  );
}

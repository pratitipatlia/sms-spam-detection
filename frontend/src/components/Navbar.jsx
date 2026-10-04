import React from 'react';
import { ShieldCheck, Sparkles } from 'lucide-react';

/**
 * Navbar Component
 * Renders the top navigation bar with brand, icon, Home link, and AI badge.
 */
export default function Navbar() {
  const handleScrollToTop = (e) => {
    e.preventDefault();
    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    });
  };

  return (
    <header className="navbar" role="banner">
      <div className="navbar-inner">
        <button
          type="button"
          onClick={handleScrollToTop}
          className="navbar-brand"
          aria-label="SpamShield AI Home"
        >
          <span className="brand-icon-wrapper" aria-hidden="true">
            <ShieldCheck size={20} strokeWidth={2.5} />
          </span>
          <span>SpamShield AI</span>
        </button>

        <div className="navbar-links">
          <nav aria-label="Main Navigation">
            <a
              href="#top"
              onClick={handleScrollToTop}
              className="nav-link"
            >
              Home
            </a>
          </nav>
        </div>
      </div>
    </header>
  );
}

import React from 'react';
import './LandingPage.css';

const LandingPage = () => {
  return (
    <div className="landing-page">
      {/* Hero Section */}
      <section className="hero">
        <h1>Your Mental Health Companion</h1>
        <p>Connect with our AI-powered chatbot for support and guidance.</p>
        <button className="btn btn-primary">Get Started</button>
      </section>

      {/* Features Section */}
      <section className="features">
        <h2>Features</h2>
        <div className="feature-cards">
          <div className="feature-card">
            <h3>24/7 Chat Support</h3>
            <p>Get round-the-clock assistance for your mental well-being.</p>
          </div>
          <div className="feature-card">
            <h3>Confidential & Secure</h3>
            <p>Your chats are private and encrypted for complete safety.</p>
          </div>
          <div className="feature-card">
            <h3>Professional Insights</h3>
            <p>Receive advice backed by mental health experts.</p>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="testimonials">
        <h2>What Our Users Say</h2>
        <div className="testimonial">
          <p>"This chatbot has been a lifesaver. I feel heard and supported."</p>
          <p>- John Doe</p>
        </div>
        <div className="testimonial">
          <p>"A great tool for managing stress and anxiety. Highly recommended!"</p>
          <p>- Jane Smith</p>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
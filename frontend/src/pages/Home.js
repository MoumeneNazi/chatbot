import React, { useState } from 'react';
import '../styles/HomeUnified.css';  // NEW unified CSS file
import { Link } from 'react-router-dom';

export default function Home() {
  const [faqOpen, setFaqOpen] = useState(null);
  const faqs = [
    {
      q: "Is MindCompanion a replacement for therapy?",
      a: "No, MindCompanion is a supportive tool designed to assist, not replace, professional therapy. It's best used alongside human guidance."
    },
    {
      q: "Can I access my history?",
      a: "Yes, all chats, journals, and progress reports are saved securely. You can view and download them at any time."
    },
    {
      q: "How does AI understand my feelings?",
      a: "We use emotional NLP and knowledge graphs trained on real psychological data to understand and respond to your input in an empathetic way."
    }
  ];

  return (
    <div className="home-container">
      {/* HERO */}
      <section className="hero reveal">
        <h1>Welcome to MindCompanion 🧠</h1>
        <p>Your always-on mental wellness companion. Reflect. Understand. Grow.</p>
        <Link to="/register" className="cta-button glow">Start Your Journey</Link>
      </section>

      {/* WHY SECTION */}
      <section className="why reveal">
        <h2>Why Choose MindCompanion?</h2>
        <ul>
          <li><strong>Private & Secure</strong> — We prioritize your mental well-being and your data security.</li>
          <li><strong>AI-Powered Reflection</strong> — Real-time conversations that guide your thought process.</li>
          <li><strong>Therapist Connectivity</strong> — Invite a professional to support you with context.</li>
          <li><strong>Progress Insights</strong> — Track emotional patterns over time visually.</li>
        </ul>
      </section>

      {/* HOW IT WORKS */}
      <section className="how-it-works reveal">
        <h2>How It Works</h2>
        <div className="steps">
          <div className="step">
            <span>1</span>
            <h4>Sign Up</h4>
            <p>Create a free account. Your data is encrypted from the start.</p>
          </div>
          <div className="step">
            <span>2</span>
            <h4>Check In</h4>
            <p>Start chatting with the AI or writing in your journal.</p>
          </div>
          <div className="step">
            <span>3</span>
            <h4>Track Progress</h4>
            <p>View mood summaries, emotional trends, and past entries.</p>
          </div>
          <div className="step">
            <span>4</span>
            <h4>Invite Therapist</h4>
            <p>Share access to enable expert guidance based on your data.</p>
          </div>
        </div>
      </section>

      {/* FEATURES */}
      <section className="features reveal">
        <h2>Explore Key Features</h2>
        <div className="cards">
          <div className="card"><h3>AI-Powered Chat</h3><p>Therapy-like conversations that listen and support.</p></div>
          <div className="card"><h3>Smart Journaling</h3><p>Capture your mood and thoughts, with NLP sentiment tracking.</p></div>
          <div className="card"><h3>Mood Dashboard</h3><p>Visualize your feelings and daily well-being patterns.</p></div>
          <div className="card"><h3>Therapist Mode</h3><p>Enable a real therapist to review and advise you with full history.</p></div>
        </div>
      </section>

      {/* ADDITIONAL CONTENT */}

      {/* USER STORIES */}
      <section className="user-stories reveal">
        <h2>User Stories</h2>
        <p>Thousands of users have transformed their lives through mindful self-reflection and AI guidance.</p>
        <blockquote>
          “Before MindCompanion, I struggled to express my feelings. Now I have a trusted companion that understands me.” – Sarah, 28
        </blockquote>
        <blockquote>
          “The AI helps me see patterns I never noticed. It’s like having a therapist in my pocket.” – James, 34
        </blockquote>
      </section>

      {/* DAILY TOOLS */}
      <section className="daily-tools reveal">
        <h2>Daily Wellness Tools</h2>
        <ul>
          <li>Mindfulness prompts to keep you centered.</li>
          <li>Emotion tracking for deeper self-awareness.</li>
          <li>Personalized coping strategies based on your mood.</li>
          <li>Journaling made easy with sentiment analysis.</li>
        </ul>
      </section>

      {/* BACKED BY SCIENCE */}
      <section className="backed-by-science reveal">
        <h2>Backed by Science</h2>
        <p>Our system uses the latest in natural language processing and psychological research to deliver empathetic, accurate support.</p>
        <p>Developed in collaboration with mental health professionals and AI experts.</p>
      </section>

      {/* DAILY CHECKLIST */}
      <section className="daily-checklist reveal">
        <h2>Daily Self-Care Checklist</h2>
        <ol>
          <li>Take deep breaths for 5 minutes.</li>
          <li>Write down 3 things you’re grateful for.</li>
          <li>Check in with your mood using our AI chat.</li>
          <li>Reach out to a friend or therapist if needed.</li>
          <li>Practice mindful meditation or stretching.</li>
        </ol>
      </section>

      {/* QUOTES */}
      <section className="quotes reveal">
        <h2>Inspirational Quotes</h2>
        <p>“The greatest wealth is health.” — Virgil</p>
        <p>“Self-care is not selfish.” — Audrey Lorde</p>
        <p>“Healing takes time, and asking for help is a courageous step.” — Mariska Hargitay</p>
      </section>

      {/* FAQ */}
      <section className="faq reveal">
        <h2>Frequently Asked Questions</h2>
        {faqs.map((f, i) => (
          <div key={i} className="faq-item">
            <button onClick={() => setFaqOpen(faqOpen === i ? null : i)}>
              {f.q} <span>{faqOpen === i ? '-' : '+'}</span>
            </button>
            {faqOpen === i && <p className="answer">{f.a}</p>}
          </div>
        ))}
      </section>

      {/* CALL TO ACTION */}
      <section className="newsletter reveal">
        <h2>Ready to Begin?</h2>
        <p>Join thousands transforming their mental health through self-reflection and guided conversation.</p>
        <Link to="/register" className="cta-button glow">Create Your Free Account</Link>
      </section>

      {/* FOOTER */}
      <footer className="footer">
        <div className="footer-top">
          <div>
            <h4>MindCompanion</h4>
            <p>Empowering mental wellness through AI and human empathy.</p>
          </div>
          <div>
            <h5>Explore</h5>
            <ul>
              <li><Link to="/about">About Us</Link></li>
              <li><Link to="/contact">Contact</Link></li>
              <li><a href="#">Privacy Policy</a></li>
              <li><a href="#">Terms of Use</a></li>
            </ul>
          </div>
        </div>
        <div className="footer-bottom">
          <p>&copy; 2025 MindCompanion. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

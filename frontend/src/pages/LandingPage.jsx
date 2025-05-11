import React from 'react';
import { Link } from 'react-router-dom';

const LandingPage = () => {
  return (
    <div>
      <nav>
        <Link to="/login">Login</Link>
        <Link to="/register">Register</Link>
      </nav>
      <header>
        <h1>Welcome to the Mental Health Chatbot</h1>
        <p>Your companion for mental well-being.</p>
      </header>
    </div>
  );
};

export default LandingPage;
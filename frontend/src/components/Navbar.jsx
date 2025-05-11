import React from 'react';
import { Link } from 'react-router-dom';
import './Navbar.css'; // Add styles here or in your global CSS

const Navbar = () => {
  return (
    <div>
      {/* Navbar Section */}
      <nav className="navbar">
        {/* Logo */}
        <div className="navbar-logo">
          <h1>Mental Health Chatbot</h1>
        </div>

        {/* Navigation Links */}
        <div className="navbar-links">
          <Link to="/">Home</Link>
          <Link to="/about">About Us</Link>
          <Link to="/projects">Our Projects</Link>
          <Link to="/contact">Contact Us</Link>
        </div>
      </nav>

      {/* Buttons Section */}
      <div className="navbar-buttons">
        <Link to="/login">
          <button className="btn-login">Login</button>
        </Link>
        <Link to="/register">
          <button className="btn-register">Register</button>
        </Link>
      </div>
    </div>
  );
};

export default Navbar;
import React from 'react';
import { Link } from 'react-router-dom';
import './Navbar.css';

const Navbar = () => {
  return (
    <header className="navbar-container">
      <div className="navbar">
        {/* Logo */}
        <div className="navbar-logo">
          <h1>MentalHealth</h1>
        </div>

        {/* Navigation Links */}
        <nav className="navbar-links">
          <Link to="/">Home</Link>
          <Link to="/about">About Us</Link>
          <Link to="/projects">Our Projects</Link>
          <Link to="/contact">Contact Us</Link>
        </nav>
      </div>

      {/* Buttons Section */}
      <div className="navbar-buttons">
        <Link to="/login">
          <button className="btn btn-login">Login</button>
        </Link>
        <Link to="/register">
          <button className="btn btn-register">Register</button>
        </Link>
      </div>
    </header>
  );
};

export default Navbar;
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { getToken, logout } from '../auth';
import '../styles/navbar.css';

function Navbar() {
  const [open, setOpen] = useState(false);

  return (
    <nav className={`navbar ${open ? 'expanded' : ''}`}>
      <div className="nav-left">
        <Link to="/"><img src="/logo192.png" alt="MindCompanion" className="logo" /></Link>
        <Link to="/">Home</Link>
        <Link to="/about">About</Link>
        <Link to="/testimonials">Testimonials</Link>
        <Link to="/contact">Contact</Link>
      </div>

      <div className="hamburger" onClick={() => setOpen(!open)}>
        <div style={{ transform: open ? 'rotate(45deg) translate(5px,5px)' : '' }} />
        <div style={{ opacity: open ? 0 : 1 }} />
        <div style={{ transform: open ? 'rotate(-45deg) translate(6px,-6px)' : '' }} />
      </div>

      <div className="nav-right">
        {getToken() ? (
          <>
            <Link to="/chat">Chat</Link>
            <Link to="/journal">Journal</Link>
            <Link to="/progress">Progress</Link>
            <Link to="/therapist">Therapist</Link>
            <button className="glow" onClick={logout}>Logout</button>
          </>
        ) : (
          <>
            <Link to="/login">Login</Link>
            <Link to="/register">Register</Link>
          </>
        )}
      </div>
    </nav>
  );
}

export default Navbar;

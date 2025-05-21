import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import logo from '../assets/logo.png';
import '../styles/navbar.css';

function Navbar() {
  const navigate = useNavigate();
  const { token, role, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="nav-left">
        <Link to="/" className="logo-link">
          <img src={logo} alt="MindCompanion" className="logo" />
        </Link>
        <Link to="/">Home</Link>
        <Link to="/about">About</Link>
        <Link to="/contact">Contact</Link>
      </div>
      <div className="nav-right">
        {token ? (
          <>
            {role === 'user' && (
              <>
                <Link to="/chat">Chat</Link>
                <Link to="/journal">Journal</Link>
                <Link to="/progress">Progress</Link>
                <Link to="/review">Reviews</Link>
                <Link to="/apply-therapist" className="apply-therapist-btn">Become a Therapist</Link>
              </>
            )}
            {role === 'therapist' && (
              <>
                <Link to="/therapist/dashboard">Dashboard</Link>
                <Link to="/review">Reviews</Link>
                <Link to="/reviews/add">Add Review</Link>
              </>
            )}
            <button onClick={handleLogout} className="logout-btn">
              Logout
            </button>
          </>
        ) : (
          <>
            <Link to="/login" className="login-btn">Login</Link>
            <Link to="/register" className="register-btn">Register</Link>
          </>
        )}
      </div>
    </nav>
  );
}

export default Navbar;
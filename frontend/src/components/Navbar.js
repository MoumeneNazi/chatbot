import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { getToken, logout } from '../auth';
import logo from '../assets/logo.png';
import '../styles/navbar.css';

function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const [role, setRole] = useState(localStorage.getItem('role'));
  const [isAuthenticated, setIsAuthenticated] = useState(!!getToken());

  useEffect(() => {
    const token = getToken();
    const currentRole = localStorage.getItem('role');
    setIsAuthenticated(!!token);
    setRole(currentRole);
  }, [location]);

  const handleLogout = () => {
    logout();
    setIsAuthenticated(false);
    setRole(null);
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="nav-left">
        <Link to="/">
          <img src={logo} alt="MindCompanion" className="logo" />
        </Link>
        <Link to="/">Home</Link>
        <Link to="/about">About</Link>
        <Link to="/testimonials">Testimonials</Link>
        <Link to="/contact">Contact</Link>
      </div>
      <div className="nav-right">
        {isAuthenticated ? (
          <>
            {role === 'user' && (
              <>
                <Link to="/chat">Chat</Link>
                <Link to="/user/dashboard">Dashboard</Link>
              </>
            )}
            {role === 'therapist' && (
              <>
                <Link to="/therapist/dashboard">Dashboard</Link>
                <Link to="/therapist/progress">Progress</Link>
                <Link to="/therapist/journal">Journal</Link>
              </>
            )}
            <button className="glow" onClick={handleLogout}>Logout</button>
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
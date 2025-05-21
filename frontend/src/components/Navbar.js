import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import ReportProblemModal from './ReportProblemModal';
import logo from '../assets/logo.png';
import '../styles/navbar.css';

function Navbar() {
  const navigate = useNavigate();
  const { token, role, logout } = useAuth();
  const [isReportModalOpen, setIsReportModalOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const openReportModal = () => {
    setIsReportModalOpen(true);
  };

  const closeReportModal = () => {
    setIsReportModalOpen(false);
  };

  return (
    <>
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
                  <button onClick={openReportModal} className="report-problem-btn">Report Problem</button>
                </>
              )}
              {role === 'therapist' && (
                <>
                  <Link to="/therapist/dashboard">Dashboard</Link>
                  <Link to="/therapist/disorders">Manage Disorders</Link>
                  <Link to="/therapist/applications">Applications</Link>
                  <Link to="/review">Reviews</Link>
                  <Link to="/reviews/add">Add Review</Link>
                  <button onClick={openReportModal} className="report-problem-btn">Report Problem</button>
                </>
              )}
              {role === 'admin' && (
                <>
                  <Link to="/admin/dashboard">Admin Dashboard</Link>
                  <Link to="/admin/users">Users</Link>
                  <Link to="/admin/applications">Applications</Link>
                  <Link to="/therapist/disorders">Knowledge Base</Link>
                  <Link to="/admin/problems">Problem Reports</Link>
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
      <ReportProblemModal isOpen={isReportModalOpen} onClose={closeReportModal} />
    </>
  );
}

export default Navbar;
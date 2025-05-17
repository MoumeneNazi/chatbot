import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api';
import '../styles/auth.css';

function Register() {
  const [form, setForm] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { token } = useAuth();

  // Only redirect if already logged in AND trying to access register page
  useEffect(() => {
    if (token && window.location.pathname === '/register') {
      navigate('/');
    }
  }, [token, navigate]);

  const handleChange = e => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async e => {
    e.preventDefault();
    setError('');
    
    try {
      await api.post('/auth/register', form);
      // Show success message and redirect to login
      alert('Registration successful! Please login with your credentials.');
      navigate('/login');
    } catch (err) {
      console.error('Registration error:', err.response || err);
      if (err.response?.status === 400 && err.response?.data?.detail?.includes('already exists')) {
        setError('Username already exists. Please choose a different username.');
      } else {
        setError(err.response?.data?.detail || 'Registration failed. Please try again.');
      }
    }
  };

  return (
    <div className="auth-page">
      <h2>Register</h2>
      <form onSubmit={handleSubmit}>
        <input 
          name="username" 
          placeholder="Username"
          value={form.username}
          onChange={handleChange} 
          required 
          autoComplete="username"
          minLength="3"
          maxLength="20"
          pattern="[a-zA-Z0-9_-]+"
          title="Username can only contain letters, numbers, underscores and hyphens"
        />
        <input 
          name="password" 
          type="password" 
          placeholder="Password"
          value={form.password}
          onChange={handleChange} 
          required 
          autoComplete="new-password"
          minLength="6"
        />
        <button type="submit">Register</button>
        {error && (
          <p className="error">
            {typeof error === 'string' ? error : JSON.stringify(error)}
          </p>
        )}
      </form>
      <p>Already have an account? <Link to="/login">Login</Link></p>
    </div>
  );
}

export default Register;
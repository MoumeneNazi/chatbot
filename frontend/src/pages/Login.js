import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api';
import '../styles/auth.css';

function Login() {
  const [form, setForm] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { login, token } = useAuth();

  // Only redirect if already logged in AND trying to access login page
  useEffect(() => {
    if (token && window.location.pathname === '/login') {
      navigate('/');
    }
  }, [token, navigate]);

  const handleChange = e =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async e => {
    e.preventDefault();
    setError('');
    try {
      // Prepare data in x-www-form-urlencoded format
      const params = new URLSearchParams();
      params.append('username', form.username);
      params.append('password', form.password);
      params.append('grant_type', 'password');

      const response = await api.post('/auth/token', params, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });

      const data = response.data;
      
      // Store session info with username
      await login(data.access_token, data.role, data.username);
      
      // Redirect based on role
      if (data.role === 'therapist') {
        navigate('/therapist/dashboard');
      } else if (data.role === 'user') {
        navigate('/chat');
      } else {
        navigate('/');
      }
    } catch (err) {
      console.error('Login error:', err.response || err);
      if (err.response?.status === 401) {
        setError('Invalid username or password');
      } else {
        setError(err.response?.data?.detail || err.response?.data?.msg || 'Login failed. Please try again.');
      }
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-box">
        <h2>Login</h2>
        {error && <div className="error-message">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              name="username"
              value={form.username}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={form.password}
              onChange={handleChange}
              required
            />
          </div>
          <button type="submit" className="auth-button">Login</button>
        </form>
        <p className="auth-link">
          Don't have an account? <Link to="/register">Register</Link>
        </p>
      </div>
    </div>
  );
}

export default Login;
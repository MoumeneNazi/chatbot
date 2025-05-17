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
      
      // Store session info
      await login(data.access_token, data.role);
      
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
    <div className="auth-page">
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        <input
          name="username"
          placeholder="Username"
          value={form.username}
          onChange={handleChange}
          required
          autoComplete="username"
        />
        <input
          name="password"
          type="password"
          placeholder="Password"
          value={form.password}
          onChange={handleChange}
          required
          autoComplete="current-password"
        />
        <button type="submit">Login</button>
        {error && (
          <p className="error">
            {typeof error === 'string' ? error : JSON.stringify(error)}
          </p>
        )}
      </form>
      <p>
        Don't have an account? <Link to="/register">Register</Link>
      </p>
    </div>
  );
}

export default Login;
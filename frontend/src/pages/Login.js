import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/auth.css';

function Login() {
  const [form, setForm] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleChange = e => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async e => {
    e.preventDefault();
    setError('');
    try {
      // Create form-encoded data
      const params = new URLSearchParams();
      params.append('username', form.username);
      params.append('password', form.password);

      const res = await fetch('http://localhost:8000/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: params.toString(),
      });

      const data = await res.json();

      if (res.ok) {
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('role', data.role);

        if (data.role === 'therapist') {
          navigate('/therapist/dashboard');
        } else if (data.role === 'user') {
          navigate('/user/dashboard');
        } else {
          navigate('/');
        }
      } else {
        setError(data.detail || data.msg || data || 'Login failed');
      }
    } catch {
      setError('Server error');
    }
  };

  return (
    <div className="auth-page">
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        <input
          name="username"
          placeholder="Username"
          onChange={handleChange}
          required
          autoComplete="username"
        />
        <input
          name="password"
          type="password"
          placeholder="Password"
          onChange={handleChange}
          required
          autoComplete="current-password"
        />
        <button type="submit">Login</button>
        {Array.isArray(error) ? (
          error.map((err, idx) => (
            <p className="error" key={idx}>{err.msg}</p>
          ))
        ) : error ? (
          <p className="error">
            {typeof error === 'string'
              ? error
              : error.msg || error.detail || JSON.stringify(error)}
          </p>
        ) : null}
      </form>
      <p>
        Don't have an account? <a href="/register">Register</a>
      </p>
    </div>
  );
}

export default Login;
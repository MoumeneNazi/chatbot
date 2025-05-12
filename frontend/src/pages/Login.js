import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { saveToken } from '../auth';

function Login() {
  const [form, setForm] = useState({ username: '', password: '' });
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    const res = await fetch('http://localhost:8000/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form)
    });

    const data = await res.json();
    if (res.ok) {
      saveToken(data.access_token);
      navigate('/chat');
    } else {
      alert(data.detail || 'Login failed');
    }
  };

  return (
    <div className="form-box">
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        <input placeholder="Username" onChange={e => setForm({ ...form, username: e.target.value })} required />
        <input type="password" placeholder="Password" onChange={e => setForm({ ...form, password: e.target.value })} required />
        <button type="submit">Login</button>
      </form>
    </div>
  );
}

export default Login;

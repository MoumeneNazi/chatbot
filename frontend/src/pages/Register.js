import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { saveToken } from '../auth';

function Register() {
  const [form, setForm] = useState({ username: '', password: '' });
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    const res = await fetch('http://localhost:8000/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form)
    });

    const data = await res.json();
    if (res.ok) {
      saveToken(data.access_token);
      navigate('/chat');
    } else {
      alert(data.detail || 'Registration failed');
    }
  };

  return (
    <div className="form-box">
      <h2>Register</h2>
      <form onSubmit={handleSubmit}>
        <input placeholder="Username" onChange={e => setForm({ ...form, username: e.target.value })} required />
        <input type="password" placeholder="Password" onChange={e => setForm({ ...form, password: e.target.value })} required />
        <button type="submit">Register</button>
      </form>
    </div>
  );
}

export default Register;

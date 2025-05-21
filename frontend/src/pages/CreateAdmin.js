import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api';
import '../styles/pages.css';
import '../styles/admin.css';

function CreateAdmin() {
  const navigate = useNavigate();
  const { role } = useAuth();
  
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    if (role !== 'admin') {
      navigate('/login');
      return;
    }
  }, [role, navigate]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate form
    if (!formData.username.trim()) {
      setError('Username is required');
      return;
    }
    
    if (!formData.email.trim()) {
      setError('Email is required');
      return;
    }
    
    // Simple email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setError('Please enter a valid email address');
      return;
    }
    
    if (!formData.password) {
      setError('Password is required');
      return;
    }
    
    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }
    
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    
    try {
      setLoading(true);
      setError('');
      
      const response = await api.post('/api/admin/create-admin', {
        username: formData.username,
        email: formData.email,
        password: formData.password
      });
      
      setSuccess(`Admin account "${response.data.username}" created successfully`);
      
      // Reset form
      setFormData({
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
      });
      
    } catch (err) {
      console.error('Error creating admin account:', err);
      setError(err.response?.data?.detail || 'Failed to create admin account');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      <h1>Create Admin Account</h1>
      <p className="subtitle">Create a new administrator account</p>
      
      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}
      
      <div className="admin-section form-container">
        <form onSubmit={handleSubmit} className="admin-form">
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              disabled={loading}
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              disabled={loading}
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              disabled={loading}
              required
              minLength={8}
            />
            <small>Must be at least 8 characters</small>
          </div>
          
          <div className="form-group">
            <label htmlFor="confirmPassword">Confirm Password</label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              disabled={loading}
              required
            />
          </div>
          
          <div className="form-actions">
            <button 
              type="submit" 
              className="btn primary-btn" 
              disabled={loading}
            >
              {loading ? 'Creating...' : 'Create Admin Account'}
            </button>
            
            <button 
              type="button" 
              className="btn secondary-btn" 
              onClick={() => navigate('/admin/dashboard')}
              disabled={loading}
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CreateAdmin; 
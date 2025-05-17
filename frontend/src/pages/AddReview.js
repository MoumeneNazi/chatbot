import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import '../styles/pages.css';
import '../styles/review.css';

const AddReview = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { token } = useAuth();
  const [users, setUsers] = useState([]);
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    disorder: 'Anxiety',
    specialty: '',
    userId: location.state?.userId || '', // Get userId from location state if available
    username: location.state?.username || '', // Get username from location state if available
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredUsers, setFilteredUsers] = useState([]);

  useEffect(() => {
    // Verify therapist authentication
    if (!token) {
      navigate('/login');
      return;
    }

    // Fetch users if no specific user is selected
    if (!formData.userId) {
      fetchUsers();
    }
  }, [navigate, token, formData.userId]);

  const fetchUsers = async () => {
    try {
      const response = await axios.get('/api/admin/users', {
        headers: { Authorization: `Bearer ${token}` }
      });
      const filteredUsers = response.data.filter(user => user.role === 'user');
      setUsers(filteredUsers);
      setError(null);
    } catch (err) {
      console.error('Error fetching users:', err);
      setError('Failed to fetch users. Please try again later.');
    }
  };

  useEffect(() => {
    if (searchTerm.trim()) {
      setFilteredUsers(
        users.filter(user => 
          user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
          user.name?.toLowerCase().includes(searchTerm.toLowerCase())
        )
      );
    } else {
      setFilteredUsers([]);
    }
  }, [searchTerm, users]);

  const disorders = [
    'Anxiety',
    'Depression',
    'Generalized Anxiety Disorder',
    'Major Depressive Disorder',
    'Panic Disorder',
    'Bipolar Disorder',
    'Post-Traumatic Stress Disorder',
    'Obsessive-Compulsive Disorder',
    'Attention-Deficit/Hyperactivity Disorder (ADHD)',
    'Autism Spectrum Disorder'
  ];

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const selectUser = (user) => {
    setFormData(prev => ({
      ...prev,
      userId: user.id,
      username: user.username
    }));
    setSearchTerm('');
    setFilteredUsers([]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.userId) {
      setError('Please select a user to review');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await axios.post('/api/reviews', {
        title: formData.title,
        content: formData.content,
        disorder: formData.disorder,
        specialty: formData.specialty,
        user_id: formData.userId
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      navigate(`/reviews?userId=${formData.userId}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to publish review');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      <div className="add-review-container">
        <h1>Create Professional Review</h1>
        <p className="subtitle">Provide professional insights for specific users</p>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit} className="review-form">
          {!formData.userId ? (
            <div className="form-group user-search-group">
              <label htmlFor="userSearch">Search User</label>
              <input
                type="text"
                id="userSearch"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search by username..."
                className="search-input"
              />
              {filteredUsers.length > 0 && (
                <div className="user-search-results">
                  {filteredUsers.map(user => (
                    <div
                      key={user.id}
                      className="user-search-item"
                      onClick={() => selectUser(user)}
                    >
                      <span className="username">{user.username}</span>
                      {user.name && <span className="name">{user.name}</span>}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="selected-user">
              <h3>Review for: {formData.username}</h3>
              <button
                type="button"
                className="change-user-btn"
                onClick={() => setFormData(prev => ({ ...prev, userId: '', username: '' }))}
              >
                Change User
              </button>
            </div>
          )}

          <div className="form-group">
            <label htmlFor="title">Title</label>
            <input
              type="text"
              id="title"
              name="title"
              value={formData.title}
              onChange={handleChange}
              required
              placeholder="Enter a descriptive title"
            />
          </div>

          <div className="form-group">
            <label htmlFor="disorder">Disorder</label>
            <select
              id="disorder"
              name="disorder"
              value={formData.disorder}
              onChange={handleChange}
              required
            >
              {disorders.map(disorder => (
                <option key={disorder} value={disorder}>{disorder}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="specialty">Your Specialty</label>
            <input
              type="text"
              id="specialty"
              name="specialty"
              value={formData.specialty}
              onChange={handleChange}
              required
              placeholder="e.g., Clinical Psychologist, Psychiatrist"
            />
          </div>

          <div className="form-group">
            <label htmlFor="content">Review Content</label>
            <textarea
              id="content"
              name="content"
              value={formData.content}
              onChange={handleChange}
              required
              placeholder="Share your professional insights, treatment approaches, and recommendations specific to this user..."
              rows="10"
            />
          </div>

          <div className="form-actions">
            <button 
              type="button" 
              className="secondary-button"
              onClick={() => navigate('/reviews')}
            >
              Cancel
            </button>
            <button 
              type="submit" 
              className="primary-button"
              disabled={loading || !formData.userId}
            >
              {loading ? 'Publishing...' : 'Publish Review'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddReview; 
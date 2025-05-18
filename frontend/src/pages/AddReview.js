import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api';
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
    disorder: '',
    specialty: '',
    userId: location.state?.userId || '',
    username: location.state?.username || '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [disorderSearchTerm, setDisorderSearchTerm] = useState('');
  const [showDisorderResults, setShowDisorderResults] = useState(false);

  const disorders = [
    'Adjustment Disorder',
    'Anxiety',
    'Attention-Deficit/Hyperactivity Disorder (ADHD)',
    'Autism Spectrum Disorder',
    'Bipolar Disorder',
    'Borderline Personality Disorder',
    'Depression',
    'Dissociative Identity Disorder',
    'Eating Disorders',
    'Generalized Anxiety Disorder',
    'Major Depressive Disorder',
    'Obsessive-Compulsive Disorder',
    'Panic Disorder',
    'Post-Traumatic Stress Disorder',
    'Schizophrenia',
    'Social Anxiety Disorder',
    'Specific Phobias'
  ];

  const filteredDisorders = disorders.filter(disorder =>
    disorder.toLowerCase().includes(disorderSearchTerm.toLowerCase())
  );

  useEffect(() => {
    // Verify therapist authentication
    if (!token) {
      navigate('/login');
      return;
    }

    // Fetch users
    fetchUsers();
  }, [navigate, token]);

  const fetchUsers = async () => {
    try {
      const response = await api.get('/api/users');
      const filteredUsers = response.data.filter(user => user.role === 'user');
      setUsers(filteredUsers);
      setError(null);
    } catch (err) {
      console.error('Error fetching users:', err);
      // Extract error message safely
      const errorMessage = err.response?.data?.detail;
      if (Array.isArray(errorMessage)) {
        // Handle FastAPI validation errors
        setError(errorMessage.map(err => err.msg).join(', '));
      } else {
        setError(errorMessage || err.message || 'Failed to fetch users. Please try again later.');
      }
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    if (name === 'userId') {
      const selectedUser = users.find(u => u.id === parseInt(value));
      setFormData(prev => ({
        ...prev,
        userId: value,
        username: selectedUser ? selectedUser.username : ''
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  const selectDisorder = (disorder) => {
    setFormData(prev => ({
      ...prev,
      disorder
    }));
    setDisorderSearchTerm('');
    setShowDisorderResults(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.userId) {
      setError('Please select a user to review');
      return;
    }
    if (!formData.disorder) {
      setError('Please select a disorder');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await api.post('/api/reviews', {
        title: formData.title,
        content: formData.content,
        disorder: formData.disorder,
        specialty: formData.specialty,
        user_id: parseInt(formData.userId)
      });
      navigate(`/review?userId=${formData.userId}`);
    } catch (err) {
      console.error('Error creating review:', err);
      // Handle error message properly
      const errorMessage = err.response?.data?.detail;
      if (Array.isArray(errorMessage)) {
        // Handle FastAPI validation errors
        setError(errorMessage.map(err => err.msg).join(', '));
      } else {
        setError(errorMessage || err.message || 'Failed to publish review');
      }
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
          <div className="form-group">
            <label htmlFor="userId">Select User</label>
            <select
              id="userId"
              name="userId"
              value={formData.userId}
              onChange={handleChange}
              required
              className="user-select"
            >
              <option value="">Select a user...</option>
              {users.map(user => (
                <option key={user.id} value={user.id}>
                  {user.username}
                </option>
              ))}
            </select>
          </div>

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
            <div className="disorder-search">
              <input
                type="text"
                id="disorder-search"
                value={disorderSearchTerm}
                onChange={(e) => {
                  setDisorderSearchTerm(e.target.value);
                  setShowDisorderResults(true);
                }}
                onFocus={() => setShowDisorderResults(true)}
                placeholder="Search for a disorder..."
                className="search-input"
              />
              {formData.disorder && (
                <div className="selected-disorder">
                  Selected: {formData.disorder}
                </div>
              )}
              {showDisorderResults && disorderSearchTerm && (
                <div className="search-results">
                  {filteredDisorders.map(disorder => (
                    <div
                      key={disorder}
                      className="search-item"
                      onClick={() => selectDisorder(disorder)}
                    >
                      {disorder}
                    </div>
                  ))}
                  {filteredDisorders.length === 0 && (
                    <div className="no-results">No matching disorders found</div>
                  )}
                </div>
              )}
            </div>
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
              disabled={loading || !formData.userId || !formData.disorder}
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
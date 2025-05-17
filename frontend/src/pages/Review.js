import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import '../styles/review.css';
import '../styles/pages.css';

const Review = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { token, role } = useAuth();
  const [reviews, setReviews] = useState([]);
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [symptoms, setSymptoms] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [userSearchTerm, setUserSearchTerm] = useState('');
  const [filteredUsers, setFilteredUsers] = useState([]);
  const [searchResults, setSearchResults] = useState({
    disorders: [],
    symptoms: [],
    reviews: []
  });

  useEffect(() => {
    if (role === 'therapist') {
      fetchUsers();
    }
    const urlParams = new URLSearchParams(location.search);
    const userId = urlParams.get('userId');
    if (userId) {
      fetchUserDetails(userId);
    }
  }, [role]);

  useEffect(() => {
    fetchReviews();
    fetchSymptoms();
  }, [selectedCategory, selectedUser]);

  useEffect(() => {
    handleSearch();
  }, [searchTerm, reviews, symptoms]);

  const fetchUsers = async () => {
    try {
      const response = await api.get('/api/admin/users', {
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

  const fetchUserDetails = async (userId) => {
    try {
      const response = await axios.get(`/api/users/${userId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSelectedUser(response.data);
    } catch (err) {
      console.error('Error fetching user details:', err);
      setError('Failed to fetch user details');
    }
  };

  const fetchReviews = async () => {
    try {
      setLoading(true);
      let url = '/api/reviews';
      const params = new URLSearchParams();
      
      if (selectedCategory !== 'all') {
        params.append('disorder', selectedCategory);
      }
      if (selectedUser) {
        params.append('user_id', selectedUser.id);
      }
      if (params.toString()) {
        url += `?${params.toString()}`;
      }

      const response = await axios.get(url, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setReviews(response.data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load reviews');
      console.error('Error fetching reviews:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchSymptoms = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`/api/symptoms${selectedCategory !== 'all' ? `?disorder=${selectedCategory}` : ''}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSymptoms(response.data);
    } catch (err) {
      console.error('Error fetching symptoms:', err);
    }
  };

  const handleSearch = () => {
    if (!searchTerm.trim()) {
      setSearchResults({
        disorders: [],
        symptoms: [],
        reviews: []
      });
      return;
    }

    const searchTermLower = searchTerm.toLowerCase();

    // Filter disorders
    const matchedDisorders = categories
      .filter(category => 
        category.id.toLowerCase().includes(searchTermLower) || 
        category.name.toLowerCase().includes(searchTermLower)
      )
      .slice(0, 5);

    // Filter symptoms
    const matchedSymptoms = symptoms
      .filter(symptom => 
        symptom.name.toLowerCase().includes(searchTermLower)
      )
      .slice(0, 5);

    // Filter reviews
    const matchedReviews = reviews
      .filter(review => 
        review.title.toLowerCase().includes(searchTermLower) ||
        review.content.toLowerCase().includes(searchTermLower) ||
        review.disorder.toLowerCase().includes(searchTermLower)
      )
      .slice(0, 5);

    setSearchResults({
      disorders: matchedDisorders,
      symptoms: matchedSymptoms,
      reviews: matchedReviews
    });
  };

  useEffect(() => {
    if (userSearchTerm.trim() && users.length > 0) {
      setFilteredUsers(
        users.filter(user =>
          user.username.toLowerCase().includes(userSearchTerm.toLowerCase()) ||
          user.name?.toLowerCase().includes(userSearchTerm.toLowerCase())
        ).slice(0, 5)
      );
    } else {
      setFilteredUsers([]);
    }
  }, [userSearchTerm, users]);

  const handleUserSelect = (user) => {
    setSelectedUser(user);
    setUserSearchTerm('');
    setFilteredUsers([]);
  };

  const addReview = () => {
    if (selectedUser) {
      navigate('/therapist/reviews/add', {
        state: { userId: selectedUser.id, username: selectedUser.username }
      });
    } else {
      navigate('/therapist/reviews/add');
    }
  };

  const categories = [
    { id: 'all', name: 'All Disorders' },
    { id: 'Anxiety', name: 'Anxiety' },
    { id: 'Depression', name: 'Depression' },
    { id: 'Generalized Anxiety Disorder', name: 'GAD' },
    { id: 'Major Depressive Disorder', name: 'MDD' },
    { id: 'Panic Disorder', name: 'Panic Disorder' },
    { id: 'Bipolar Disorder', name: 'Bipolar' },
    { id: 'Post-Traumatic Stress Disorder', name: 'PTSD' },
    { id: 'Obsessive-Compulsive Disorder', name: 'OCD' },
    { id: 'Attention-Deficit/Hyperactivity Disorder (ADHD)', name: 'ADHD' },
    { id: 'Autism Spectrum Disorder', name: 'ASD' }
  ];

  return (
    <div className="page-container">
      <div className="review-container">
        <div className="review-header">
          <h1>Mental Health Insights</h1>
          {role === 'therapist' && (
            <button onClick={addReview} className="add-review-button">
              Add New Review
            </button>
          )}
        </div>

        {role === 'therapist' && (
          <div className="user-selection-container">
            {selectedUser ? (
              <div className="selected-user-info">
                <h3>Reviews for: {selectedUser.username}</h3>
                <button
                  onClick={() => setSelectedUser(null)}
                  className="change-user-btn"
                >
                  View All Users
                </button>
              </div>
            ) : (
              <div className="user-search">
                <input
                  type="text"
                  placeholder="Search users..."
                  value={userSearchTerm}
                  onChange={(e) => setUserSearchTerm(e.target.value)}
                  className="search-input"
                />
                {filteredUsers.length > 0 && (
                  <div className="user-search-results">
                    {filteredUsers.map(user => (
                      <div
                        key={user.id}
                        className="user-search-item"
                        onClick={() => handleUserSelect(user)}
                      >
                        <span className="username">{user.username}</span>
                        {user.name && <span className="name">{user.name}</span>}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        <p className="review-description">
          {role === 'therapist' 
            ? "Manage and create professional insights for your patients. Select a user to view or add specific reviews."
            : "View professional insights about your mental health condition, including symptoms and treatment approaches."}
        </p>

        <div className="search-container">
          <input
            type="text"
            placeholder="Search disorders, symptoms, or insights..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          {searchTerm && (
            <div className="search-results">
              {searchResults.disorders.length > 0 && (
                <div className="search-section">
                  <h3>Disorders</h3>
                  {searchResults.disorders.map(disorder => (
                    <div 
                      key={disorder.id} 
                      className="search-item"
                      onClick={() => {
                        setSelectedCategory(disorder.id);
                        setSearchTerm('');
                      }}
                    >
                      {disorder.name}
                    </div>
                  ))}
                </div>
              )}
              {searchResults.symptoms.length > 0 && (
                <div className="search-section">
                  <h3>Symptoms</h3>
                  {searchResults.symptoms.map(symptom => (
                    <div key={symptom.name} className="search-item">
                      {symptom.name}
                    </div>
                  ))}
                </div>
              )}
              {searchResults.reviews.length > 0 && (
                <div className="search-section">
                  <h3>Related Insights</h3>
                  {searchResults.reviews.map(review => (
                    <div key={review.id} className="search-item">
                      {review.title}
                    </div>
                  ))}
                </div>
              )}
              {!searchResults.disorders.length && !searchResults.symptoms.length && !searchResults.reviews.length && (
                <div className="no-results">No results found</div>
              )}
            </div>
          )}
        </div>

        <div className="category-filters">
          {categories.map(category => (
            <button
              key={category.id}
              className={`category-button ${selectedCategory === category.id ? 'active' : ''}`}
              onClick={() => setSelectedCategory(category.id)}
            >
              {category.name}
            </button>
          ))}
        </div>

        {selectedCategory !== 'all' && symptoms.length > 0 && (
          <div className="symptoms-section">
            <h2>Common Symptoms</h2>
            <div className="symptoms-grid">
              {symptoms.map(symptom => (
                <div key={symptom.name} className="symptom-tag">
                  {symptom.name}
                </div>
              ))}
            </div>
          </div>
        )}

        {loading ? (
          <div className="loading">Loading insights...</div>
        ) : error ? (
          <div className="error">{error}</div>
        ) : (
          <div className="reviews-grid">
            {reviews.map(review => (
              <div key={review.id} className="review-card">
                <div className="review-header">
                  <h3>{review.title}</h3>
                  <span className="category-tag">{review.disorder}</span>
                </div>
                <div className="therapist-info">
                  <img src={review.therapistAvatar || '/default-avatar.png'} alt="Therapist" />
                  <div>
                    <p className="therapist-name">Dr. {review.therapistName}</p>
                    <p className="therapist-specialty">{review.specialty}</p>
                  </div>
                </div>
                <p className="review-content">{review.content}</p>
                <div className="review-footer">
                  <span className="date">{new Date(review.createdAt).toLocaleDateString()}</span>
                  {role === 'user' && (
                    <div className="review-actions">
                      <button className="action-button">Save</button>
                      <button className="action-button">Share</button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Review; 
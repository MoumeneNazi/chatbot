import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import '../styles/admin.css';
import '../styles/pages.css';
import { useAuth } from '../context/AuthContext';

function TherapistDashboard() {
  const [users, setUsers] = useState([]);
  const [disorders, setDisorders] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [treatments, setTreatments] = useState([]);
  const [showTreatmentForm, setShowTreatmentForm] = useState(false);
  const [treatmentData, setTreatmentData] = useState({
    disorder: '',
    treatment_plan: '',
    duration_weeks: 4
  });
  const [disorderSearch, setDisorderSearch] = useState('');
  const [filteredDisorders, setFilteredDisorders] = useState([]);
  const [showDisorderDropdown, setShowDisorderDropdown] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { token, role } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    // Only allow therapist role
    if (!token || role !== "therapist") {
      navigate("/login");
      return;
    }

    const fetchInitialData = async () => {
      setLoading(true);
      try {
        // Fetch users
        const usersResponse = await api.get('/api/therapist/users');
        if (usersResponse.data) {
          // Filter to only show patients (non-therapists)
          const patients = usersResponse.data.filter(user => user.role !== 'therapist');
          setUsers(patients);
          setError('');
        } else {
          setError('No users found');
        }

        // Fetch disorders
        const disordersResponse = await api.get('/api/therapist/disorders');
        if (disordersResponse.data) {
          setDisorders(disordersResponse.data);
        }
      } catch (err) {
        console.error('Error fetching data:', err);
        // Make sure to store error as a string
        setError(typeof err.response?.data?.detail === 'object' 
          ? JSON.stringify(err.response?.data?.detail) 
          : (err.response?.data?.detail || 'Failed to fetch data. Please try again later.'));
        
        if (err.response?.status === 401) {
          navigate('/login');
        }
      } finally {
        setLoading(false);
      }
    };
    fetchInitialData();
  }, [token, role, navigate]);

  useEffect(() => {
    // Fetch treatments when a user is selected
    if (selectedUser) {
      fetchUserTreatments(selectedUser.id);
    }
  }, [selectedUser]);

  useEffect(() => {
    // Filter disorders based on search term
    if (disorderSearch.trim() && disorders.length > 0) {
      const filtered = disorders.filter(disorder => 
        disorder.toLowerCase().includes(disorderSearch.toLowerCase())
      ).slice(0, 5); // Limit to 5 results
      setFilteredDisorders(filtered);
      setShowDisorderDropdown(filtered.length > 0);
    } else {
      setFilteredDisorders([]);
      setShowDisorderDropdown(false);
    }
  }, [disorderSearch, disorders]);

  const fetchUserTreatments = async (userId) => {
    console.log('Attempting to fetch treatments for user ID:', userId, 'Type:', typeof userId);
    try {
      // Ensure userId is a valid integer
      const id = parseInt(userId, 10);
      console.log('Parsed user ID:', id, 'Original ID:', userId, 'Is NaN?', isNaN(id));
      if (isNaN(id)) {
        setError('Invalid user ID: Please select a valid user');
        return;
      }
      
      const response = await api.get(`/api/therapist/treatment/${id}`);
      setTreatments(response.data || []);
      setError('');
    } catch (err) {
      console.error('Error fetching treatments:', err);
      setError(typeof err.response?.data?.detail === 'object'
        ? JSON.stringify(err.response?.data?.detail)
        : (err.response?.data?.detail || 'Failed to fetch treatments'));
    }
  };

  const promoteUser = async (username) => {
    try {
      const response = await api.put(`/api/therapist/promote/${username}`);
      if (response.data) {
        alert(response.data.msg);
        // Refresh user list
        setUsers(prev =>
          prev.map(u =>
            u.username === username ? { ...u, role: 'therapist' } : u
          )
        );
      } else {
        alert('Failed to promote user');
      }
    } catch (err) {
      console.error('Error promoting user:', err);
      alert(typeof err.response?.data?.detail === 'object'
        ? JSON.stringify(err.response?.data?.detail)
        : (err.response?.data?.detail || 'Server error'));
      
      if (err.response?.status === 401) {
        navigate('/login');
      }
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setTreatmentData({
      ...treatmentData,
      [name]: value
    });
  };

  const handleDisorderSearch = (e) => {
    setDisorderSearch(e.target.value);
    // When the search changes, update the treatmentData.disorder as well
    setTreatmentData({
      ...treatmentData,
      disorder: e.target.value
    });
    // Show dropdown when typing
    setShowDisorderDropdown(true);
  };

  const selectDisorder = (disorder) => {
    setTreatmentData({
      ...treatmentData,
      disorder: disorder
    });
    setDisorderSearch(disorder);
    setShowDisorderDropdown(false);
  };
  
  // Add a ref to handle clicking outside the dropdown
  const searchRef = React.useRef(null);
  
  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setShowDisorderDropdown(false);
      }
    }
    
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [searchRef]);

  const createTreatment = async (e) => {
    e.preventDefault();
    if (!selectedUser) {
      setError('Please select a user first');
      return;
    }

    try {
      // Ensure user ID is a valid integer
      const userId = parseInt(selectedUser.id, 10);
      if (isNaN(userId)) {
        setError('Invalid user ID: Please select a valid user');
        return;
      }
      
      await api.post(`/api/therapist/treatment/${userId}`, treatmentData);
      // Reset form and refresh treatments
      setTreatmentData({
        disorder: '',
        treatment_plan: '',
        duration_weeks: 4
      });
      setShowTreatmentForm(false);
      fetchUserTreatments(userId);
      alert('Treatment plan created successfully');
      setError('');
    } catch (err) {
      console.error('Error creating treatment:', err);
      setError(typeof err.response?.data?.detail === 'object'
        ? JSON.stringify(err.response?.data?.detail)
        : (err.response?.data?.detail || 'Failed to create treatment'));
    }
  };

  const updateTreatmentStatus = async (treatmentId, status) => {
    try {
      await api.put(`/api/therapist/treatment/${treatmentId}/status`, { status });
      // Refresh treatments
      if (selectedUser) {
        fetchUserTreatments(selectedUser.id);
      }
      setError('');
    } catch (err) {
      console.error('Error updating treatment:', err);
      // Make sure to store error as a string
      setError(typeof err.response?.data?.detail === 'object'
        ? JSON.stringify(err.response?.data?.detail)
        : (err.response?.data?.detail || 'Failed to update treatment status'));
    }
  };

  const viewJournal = (username) => navigate(`/therapist/journal/${username}`);
  const viewChat = (username) => navigate(`/therapist/chat/${username}`);

  const selectUser = (user) => {
    console.log('Selected user object:', user);
    setSelectedUser(user);
    setShowTreatmentForm(false);
  };

  const getStatusClass = (status) => {
    switch (status) {
      case 'Active': return 'status-active';
      case 'Completed': return 'status-completed';
      case 'Canceled': return 'status-canceled';
      default: return '';
    }
  };

  return (
    <div className="page-container">
      <div className="admin-dashboard">
        <div className="dashboard-header">
          <h2>Therapist Dashboard</h2>
          <div className="dashboard-actions">
            <button 
              className="primary-button"
              onClick={() => navigate('/reviews/add')}
            >
              Create New Review
            </button>
          </div>
        </div>

        {loading ? (
          <div className="loading">Loading...</div>
        ) : (
          <div className="dashboard-content">
            {error && <p className="error">{error}</p>}
            
            <div className="dashboard-grid">
              <div className="patients-list">
                <h3>Patients</h3>
                {users.length > 0 ? (
                  <div className="user-list">
                    {users.map((u, i) => (
                      <div 
                        key={i} 
                        className={`user-card ${selectedUser?.username === u.username ? 'selected' : ''}`}
                        onClick={() => selectUser(u)}
                      >
                        <h4>{u.username}</h4>
                        <div className="user-actions">
                          <button onClick={(e) => { e.stopPropagation(); viewJournal(u.username); }}>Journal</button>
                          <button onClick={(e) => { e.stopPropagation(); viewChat(u.username); }}>Chat</button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p>No patients found</p>
                )}
              </div>
              
              {selectedUser && (
                <div className="treatment-section">
                  <div className="treatment-header">
                    <h3>Treatment Plans for {selectedUser.username}</h3>
                    <button 
                      className="add-treatment-btn"
                      onClick={() => setShowTreatmentForm(!showTreatmentForm)}
                    >
                      {showTreatmentForm ? 'Cancel' : 'Add Treatment Plan'}
                    </button>
                  </div>
                  
                  {showTreatmentForm && (
                    <form className="treatment-form" onSubmit={createTreatment}>
                      <div className="form-group" ref={searchRef}>
                        <label>Disorder:</label>
                        <input
                          type="text"
                          name="disorder"
                          value={disorderSearch}
                          onChange={handleDisorderSearch}
                          onFocus={() => setShowDisorderDropdown(true)}
                          placeholder="Type to search for a disorder..."
                          required
                        />
                        {showDisorderDropdown && (
                          <div className="disorder-dropdown">
                            {filteredDisorders.length > 0 ? (
                              filteredDisorders.map((disorder, idx) => (
                                <div
                                  key={idx}
                                  className="disorder-option"
                                  onClick={() => selectDisorder(disorder)}
                                >
                                  {disorder}
                                </div>
                              ))
                            ) : (
                              <div className="disorder-option no-results">
                                {disorderSearch.trim() ? "No matching disorders found" : "Type to search disorders"}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                      
                      <div className="form-group">
                        <label>Treatment Plan:</label>
                        <textarea
                          name="treatment_plan"
                          value={treatmentData.treatment_plan}
                          onChange={handleInputChange}
                          rows="4"
                          required
                          placeholder="Describe the treatment plan..."
                        />
                      </div>
                      
                      <div className="form-group">
                        <label>Duration (weeks):</label>
                        <input
                          type="number"
                          name="duration_weeks"
                          value={treatmentData.duration_weeks}
                          onChange={handleInputChange}
                          min="1"
                          max="52"
                          required
                        />
                      </div>
                      
                      <button type="submit" className="submit-btn">Create Treatment Plan</button>
                    </form>
                  )}
                  
                  <div className="treatments-list">
                    {treatments.length > 0 ? (
                      treatments.map((treatment, idx) => (
                        <div key={idx} className="treatment-card">
                          <div className="treatment-header">
                            <h4>{treatment.disorder}</h4>
                            <span className={`treatment-status ${getStatusClass(treatment.status)}`}>
                              {treatment.status}
                            </span>
                          </div>
                          <p className="treatment-plan">{treatment.treatment_plan}</p>
                          <div className="treatment-details">
                            <span>Duration: {treatment.duration_weeks} weeks</span>
                            <span>Started: {new Date(treatment.created_at).toLocaleDateString()}</span>
                          </div>
                          {treatment.status === 'Active' && (
                            <div className="treatment-actions">
                              <button 
                                className="complete-btn"
                                onClick={() => updateTreatmentStatus(treatment.id, 'Completed')}
                              >
                                Mark Completed
                              </button>
                              <button 
                                className="cancel-btn"
                                onClick={() => updateTreatmentStatus(treatment.id, 'Canceled')}
                              >
                                Cancel Treatment
                              </button>
                            </div>
                          )}
                        </div>
                      ))
                    ) : (
                      <p>No treatments found for this patient</p>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default TherapistDashboard;
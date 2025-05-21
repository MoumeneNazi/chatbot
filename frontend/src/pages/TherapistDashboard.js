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
  const [applications, setApplications] = useState([]);
  const [showApplications, setShowApplications] = useState(false);
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
        
        // Fetch therapist applications
        const applicationsResponse = await api.get('/api/therapist/applications');
        if (applicationsResponse.data) {
          setApplications(applicationsResponse.data);
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

  const handleApplicationStatus = async (applicationId, status) => {
    try {
      await api.put(`/api/therapist/applications/${applicationId}/status`, { status });
      // Update applications list
      setApplications(prev => 
        prev.map(app => 
          app.id === applicationId ? { ...app, status } : app
        )
      );
      alert(`Application status updated to ${status}`);
    } catch (err) {
      console.error('Error updating application status:', err);
      alert(err.response?.data?.detail || 'Failed to update application status');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="admin-container">
      <div className="admin-sidebar">
        <h2>Therapist Dashboard</h2>
        <div className="admin-menu">
          <button 
            className={!showApplications ? "active" : ""} 
            onClick={() => setShowApplications(false)}
          >
            Patient Management
          </button>
          <button 
            className={showApplications ? "active" : ""} 
            onClick={() => setShowApplications(true)}
          >
            Therapist Applications
            {applications.filter(app => app.status === 'pending').length > 0 && (
              <span className="badge">{applications.filter(app => app.status === 'pending').length}</span>
            )}
          </button>
        </div>
      </div>

      <div className="admin-content">
        {error && <div className="error-message">{error}</div>}
        
        {!showApplications ? (
          // Patient Management Section
          <div className="admin-section">
            <h3>Patient Management</h3>
            <div className="admin-grid">
              <div className="users-list">
                <h4>Patients</h4>
                {users.length > 0 ? (
                  <ul>
                    {users.map(user => (
                      <li 
                        key={user.id} 
                        className={selectedUser?.id === user.id ? 'selected' : ''}
                        onClick={() => selectUser(user)}
                      >
                        {user.username}
                        <div className="user-actions">
                          <button onClick={() => viewChat(user.username)}>Chat</button>
                          <button onClick={() => viewJournal(user.username)}>Journal</button>
                        </div>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p>No patients found</p>
                )}
              </div>

              <div className="user-details">
                {selectedUser ? (
                  <div>
                    <h4>Patient: {selectedUser.username}</h4>
                    
                    <div className="treatment-section">
                      <h5>Treatment Plans</h5>
                      {treatments.length > 0 ? (
                        <ul className="treatments-list">
                          {treatments.map(treatment => (
                            <li key={treatment.id} className={`treatment-item ${getStatusClass(treatment.status)}`}>
                              <div className="treatment-header">
                                <h6>{treatment.disorder}</h6>
                                <span className={`status ${treatment.status.toLowerCase()}`}>
                                  {treatment.status}
                                </span>
                              </div>
                              <p className="treatment-plan">{treatment.treatment_plan}</p>
                              <div className="treatment-meta">
                                <span>Duration: {treatment.duration_weeks} weeks</span>
                                <span>Created: {new Date(treatment.created_at).toLocaleDateString()}</span>
                              </div>
                              <div className="treatment-actions">
                                <button 
                                  onClick={() => updateTreatmentStatus(treatment.id, 'Active')}
                                  disabled={treatment.status === 'Active'}
                                >
                                  Set Active
                                </button>
                                <button 
                                  onClick={() => updateTreatmentStatus(treatment.id, 'Completed')}
                                  disabled={treatment.status === 'Completed'}
                                >
                                  Mark Complete
                                </button>
                              </div>
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p>No treatment plans found</p>
                      )}
                      
                      <button 
                        className="add-treatment-btn"
                        onClick={() => setShowTreatmentForm(!showTreatmentForm)}
                      >
                        {showTreatmentForm ? 'Cancel' : 'Add Treatment Plan'}
                      </button>
                      
                      {showTreatmentForm && (
                        <form onSubmit={createTreatment} className="treatment-form">
                          <div className="form-group" ref={searchRef}>
                            <label>Disorder</label>
                            <input
                              type="text"
                              name="disorder"
                              value={disorderSearch}
                              onChange={handleDisorderSearch}
                              placeholder="Search disorders..."
                              required
                            />
                            {showDisorderDropdown && filteredDisorders.length > 0 && (
                              <ul className="disorder-dropdown">
                                {filteredDisorders.map((disorder, index) => (
                                  <li key={index} onClick={() => selectDisorder(disorder)}>
                                    {disorder}
                                  </li>
                                ))}
                              </ul>
                            )}
                          </div>
                          <div className="form-group">
                            <label>Treatment Plan</label>
                            <textarea
                              name="treatment_plan"
                              value={treatmentData.treatment_plan}
                              onChange={handleInputChange}
                              placeholder="Describe the treatment plan..."
                              required
                              rows={4}
                            ></textarea>
                          </div>
                          <div className="form-group">
                            <label>Duration (weeks)</label>
                            <input
                              type="number"
                              name="duration_weeks"
                              value={treatmentData.duration_weeks}
                              onChange={handleInputChange}
                              min={1}
                              max={52}
                              required
                            />
                          </div>
                          <button type="submit" className="submit-btn">Create Treatment Plan</button>
                        </form>
                      )}
                    </div>
                  </div>
                ) : (
                  <p>Select a patient to view details</p>
                )}
              </div>
            </div>
          </div>
        ) : (
          // Therapist Applications Section
          <div className="admin-section">
            <h3>Therapist Applications</h3>
            {applications.length > 0 ? (
              <div className="applications-list">
                {applications.map(app => (
                  <div key={app.id} className={`application-card ${app.status.toLowerCase()}`}>
                    <div className="application-header">
                      <h4>{app.full_name}</h4>
                      <span className={`status-badge ${app.status}`}>
                        {app.status.toUpperCase()}
                      </span>
                    </div>
                    <div className="application-details">
                      <p><strong>Email:</strong> {app.email}</p>
                      <p><strong>Specialty:</strong> {app.specialty}</p>
                      <p><strong>License #:</strong> {app.license_number}</p>
                      <p><strong>Certification:</strong> {app.certification}</p>
                      <p><strong>Experience:</strong> {app.experience_years} years</p>
                      <p><strong>Applied:</strong> {formatDate(app.created_at)}</p>
                      {app.document_path && (
                        <p>
                          <strong>Document:</strong> 
                          <a href={`/uploads/${app.document_path}`} target="_blank" rel="noopener noreferrer">
                            View Document
                          </a>
                        </p>
                      )}
                    </div>
                    {app.status === 'pending' && (
                      <div className="application-actions">
                        <button 
                          className="approve-btn"
                          onClick={() => handleApplicationStatus(app.id, 'approved')}
                        >
                          Approve
                        </button>
                        <button 
                          className="reject-btn"
                          onClick={() => handleApplicationStatus(app.id, 'rejected')}
                        >
                          Reject
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p>No therapist applications found</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default TherapistDashboard;
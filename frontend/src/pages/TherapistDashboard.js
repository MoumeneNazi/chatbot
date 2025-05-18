import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import '../styles/admin.css';
import '../styles/pages.css';
import { useAuth } from '../context/AuthContext';

function TherapistDashboard() {
  const [users, setUsers] = useState([]);
  const [error, setError] = useState('');
  const { token, role } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    // Only allow therapist role
    if (!token || role !== "therapist") {
      navigate("/login");
      return;
    }

    const fetchUsers = async () => {
      try {
        const response = await api.get('/api/therapist/users');
        if (response.data) {
          setUsers(response.data);
          setError(null);
        } else {
          setError('No users found');
        }
      } catch (err) {
        console.error('Error fetching users:', err);
        setError(err.response?.data?.detail || 'Failed to fetch users. Please try again later.');
        if (err.response?.status === 401) {
          navigate('/login');
        }
      }
    };
    fetchUsers();
  }, [token, role, navigate]);

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
      alert(err.response?.data?.detail || 'Server error');
      if (err.response?.status === 401) {
        navigate('/login');
      }
    }
  };

  const viewJournal = (username) => navigate(`/therapist/journal/${username}`);
  const viewChat = (username) => navigate(`/therapist/chat/${username}`);

  return (
    <div className="page-container">
      <div className="admin-dashboard">
        <div className="dashboard-header">
          <h2>Therapist Dashboard</h2>
          <button 
            className="primary-button"
            onClick={() => navigate('/reviews/add')}
          >
            Create New Review
          </button>
        </div>
        {error && <p className="error">{error}</p>}
        <div className="user-list">
          {users.map((u, i) => (
            <div key={i} className="user-card">
              <h4>{u.username}</h4>
              <p>Role: {u.role}</p>
              <button onClick={() => viewJournal(u.username)}>View Journal</button>
              <button onClick={() => viewChat(u.username)}>View Chat</button>
              {u.role !== "therapist" && (
                <button onClick={() => promoteUser(u.username)}>Promote</button>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default TherapistDashboard;
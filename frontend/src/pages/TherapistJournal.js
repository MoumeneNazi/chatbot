import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api';
import '../styles/pages.css';
import '../styles/journal.css';

const TherapistJournal = () => {
  const navigate = useNavigate();
  const { token, role } = useAuth();
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [userSearchTerm, setUserSearchTerm] = useState('');
  const [filteredUsers, setFilteredUsers] = useState([]);
  const [moodFilter, setMoodFilter] = useState('all');
  const [dateFilter, setDateFilter] = useState('all');

  const moods = [
    'all', 'happy', 'excited', 'peaceful', 'neutral',
    'anxious', 'sad', 'angry', 'stressed'
  ];

  const dateRanges = [
    { value: 'all', label: 'All Time' },
    { value: 'today', label: 'Today' },
    { value: 'week', label: 'This Week' },
    { value: 'month', label: 'This Month' },
    { value: 'year', label: 'This Year' }
  ];

  useEffect(() => {
    if (role !== 'therapist') {
      navigate('/login');
      return;
    }
    fetchUsers();
  }, [role, navigate]);

  useEffect(() => {
    if (selectedUser) {
      fetchJournalEntries();
    }
  }, [selectedUser, moodFilter, dateFilter]);

  useEffect(() => {
    if (userSearchTerm.trim() && users.length > 0) {
      setFilteredUsers(
        users.filter(user =>
          user.username.toLowerCase().includes(userSearchTerm.toLowerCase())
        ).slice(0, 5)
      );
    } else {
      setFilteredUsers([]);
    }
  }, [userSearchTerm, users]);

  const fetchUsers = async () => {
    try {
      const response = await api.get('/api/users');
      console.log('API Response - User objects:', response.data);
      const filteredUsers = response.data.filter(user => user.role === 'user');
      setUsers(filteredUsers);
    } catch (err) {
      console.error('Error fetching users:', err);
      setError('Failed to fetch users. Please try again later.');
    }
  };

  const fetchJournalEntries = async () => {
    if (!selectedUser) {
      setError('Please select a user first');
      return;
    }
    
    console.log('Attempting to fetch journal entries for user:', selectedUser);
    setLoading(true);
    try {
      // Ensure user ID is a valid integer
      const userId = parseInt(selectedUser.id, 10);
      console.log('Parsed user ID:', userId, 'Original ID:', selectedUser.id, 'Type:', typeof selectedUser.id);
      if (isNaN(userId)) {
        setError('Invalid user ID: Please select a valid user');
        setLoading(false);
        return;
      }
      
      let url = `/api/journal/${userId}`;
      const params = new URLSearchParams();
      
      if (moodFilter !== 'all') {
        params.append('mood', moodFilter);
      }
      if (dateFilter !== 'all') {
        params.append('date_range', dateFilter);
      }
      if (params.toString()) {
        url += `?${params.toString()}`;
      }

      const response = await api.get(url);
      setEntries(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching journal entries:', err);
      setError(typeof err.response?.data?.detail === 'object'
        ? JSON.stringify(err.response?.data?.detail)
        : (err.response?.data?.detail || 'Failed to fetch journal entries'));
    } finally {
      setLoading(false);
    }
  };

  const handleUserSelect = (user) => {
    console.log('Selected user object:', user);
    setSelectedUser(user);
    setUserSearchTerm('');
    setFilteredUsers([]);
  };

  const getMoodStats = () => {
    if (!entries.length) return null;

    const moodCounts = entries.reduce((acc, entry) => {
      acc[entry.mood] = (acc[entry.mood] || 0) + 1;
      return acc;
    }, {});

    const totalEntries = entries.length;
    return Object.entries(moodCounts).map(([mood, count]) => ({
      mood,
      count,
      percentage: ((count / totalEntries) * 100).toFixed(1)
    }));
  };

  const getActivityStats = () => {
    if (!entries.length) return null;

    const activityCounts = entries.reduce((acc, entry) => {
      if (entry.activities && Array.isArray(entry.activities)) {
        entry.activities.forEach(activity => {
          acc[activity] = (acc[activity] || 0) + 1;
        });
      }
      return acc;
    }, {});

    if (Object.keys(activityCounts).length === 0) {
      return [];
    }

    return Object.entries(activityCounts)
      .map(([activity, count]) => ({ activity, count }))
      .sort((a, b) => b.count - a.count);
  };

  return (
    <div className="page-container">
      <div className="journal-container">
        <div className="journal-header">
          <h1>Patient Journal Entries</h1>
          <p className="subtitle">Review and analyze your patients' emotional journey</p>
        </div>

        <div className="user-selection-container">
          {selectedUser ? (
            <div className="selected-user-info">
              <h3>Journal Entries for: {selectedUser.username}</h3>
              <button
                onClick={() => setSelectedUser(null)}
                className="change-user-btn"
              >
                Change Patient
              </button>
            </div>
          ) : (
            <div className="user-search">
              <input
                type="text"
                placeholder="Search patients..."
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
                      {user.username}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {error && <div className="error-message">{error}</div>}

        {selectedUser && (
          <div className="filters-container">
            <div className="filter-group">
              <label>Filter by Mood:</label>
              <select
                value={moodFilter}
                onChange={(e) => setMoodFilter(e.target.value)}
                className="filter-select"
              >
                {moods.map(mood => (
                  <option key={mood} value={mood}>
                    {mood.charAt(0).toUpperCase() + mood.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            <div className="filter-group">
              <label>Filter by Date:</label>
              <select
                value={dateFilter}
                onChange={(e) => setDateFilter(e.target.value)}
                className="filter-select"
              >
                {dateRanges.map(range => (
                  <option key={range.value} value={range.value}>
                    {range.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        )}

        {loading ? (
          <div className="loading">Loading journal entries...</div>
        ) : selectedUser ? (
          <>
            {entries.length > 0 ? (
              <div className="journal-analysis">
                <div className="stats-container">
                  <div className="stats-section">
                    <h3>Mood Analysis</h3>
                    <div className="mood-stats">
                      {getMoodStats()?.map(stat => (
                        <div key={stat.mood} className="mood-stat">
                          <span className={`mood-indicator ${stat.mood}`}>
                            {stat.mood.charAt(0).toUpperCase() + stat.mood.slice(1)}
                          </span>
                          <span className="stat-count">{stat.count} entries</span>
                          <span className="stat-percentage">({stat.percentage}%)</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {getActivityStats()?.length > 0 && (
                    <div className="stats-section">
                      <h3>Common Activities</h3>
                      <div className="activity-stats">
                        {getActivityStats()?.map(stat => (
                          <div key={stat.activity} className="activity-stat">
                            <span className="activity-name">{stat.activity}</span>
                            <span className="stat-count">{stat.count} times</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                <div className="entries-list">
                  {entries.map(entry => (
                    <div key={entry.id} className="journal-entry">
                      <div className="entry-header">
                        <h3>{entry.title}</h3>
                        <span className="entry-date">
                          {new Date(entry.timestamp).toLocaleDateString()}
                        </span>
                      </div>
                      <div className="entry-mood">
                        Mood: <span className={`mood-indicator ${entry.mood}`}>
                          {entry.mood.charAt(0).toUpperCase() + entry.mood.slice(1)}
                        </span>
                      </div>
                      {entry.activities && Array.isArray(entry.activities) && entry.activities.length > 0 && (
                        <div className="entry-activities">
                          {entry.activities.map(activity => (
                            <span key={activity} className="activity-tag">
                              {activity}
                            </span>
                          ))}
                        </div>
                      )}
                      <p className="entry-content">{entry.content}</p>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="no-entries">
                No journal entries found for this patient.
              </div>
            )}
          </>
        ) : (
          <div className="select-user-prompt">
            Please select a patient to view their journal entries
          </div>
        )}
      </div>
    </div>
  );
};

export default TherapistJournal; 
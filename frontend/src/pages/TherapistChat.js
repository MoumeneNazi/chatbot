import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api';
import '../styles/pages.css';
import '../styles/chat.css';

const TherapistChat = () => {
  const navigate = useNavigate();
  const { username } = useParams();
  const { token, role } = useAuth();
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [userSearchTerm, setUserSearchTerm] = useState('');
  const [filteredUsers, setFilteredUsers] = useState([]);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    if (role !== 'therapist') {
      navigate('/login');
      return;
    }
    fetchUsers();
  }, [role, navigate]);

  useEffect(() => {
    // If username is provided in URL, find and select that user
    if (username && users.length > 0) {
      const user = users.find(u => u.username === username);
      if (user) {
        setSelectedUser(user);
      }
    }
  }, [username, users]);

  useEffect(() => {
    if (selectedUser) {
      fetchChatHistory();
    }
  }, [selectedUser]);

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
      const filteredUsers = response.data.filter(user => user.role === 'user');
      setUsers(filteredUsers);
    } catch (err) {
      console.error('Error fetching users:', err);
      setError('Failed to fetch users. Please try again later.');
    }
  };

  const fetchChatHistory = async () => {
    if (!selectedUser) return;
    
    setLoading(true);
    try {
      const response = await api.get(`/api/chat/history/${selectedUser.id}`);
      setChatHistory(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching chat history:', err);
      setError('Failed to fetch chat history');
    } finally {
      setLoading(false);
    }
  };

  const handleUserSelect = (user) => {
    setSelectedUser(user);
    setUserSearchTerm('');
    setFilteredUsers([]);
  };

  const exportChat = async () => {
    if (!selectedUser) return;
    
    try {
      setExporting(true);
      // Open the export URL in a new tab
      window.open(`/api/chat/export/${selectedUser.id}`, '_blank');
    } catch (error) {
      console.error('Error exporting chat:', error);
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="page-container">
      <div className="chat-container">
        <div className="chat-header">
          <h1>User Chat Histories</h1>
          <p className="subtitle">View and analyze user conversations with the chatbot</p>
        </div>

        <div className="user-selection-container">
          {selectedUser ? (
            <div className="selected-user-info">
              <h3>Chat History for: {selectedUser.username}</h3>
              <div className="user-actions">
                <button
                  onClick={() => setSelectedUser(null)}
                  className="change-user-btn"
                >
                  Change User
                </button>
                <button
                  onClick={exportChat}
                  disabled={exporting || chatHistory.length === 0}
                  className="export-button"
                  title="Export chat as HTML"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="7 10 12 15 17 10"></polyline>
                    <line x1="12" y1="15" x2="12" y2="3"></line>
                  </svg>
                  {exporting ? 'Exporting...' : 'Share'}
                </button>
              </div>
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
                      {user.username}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {error && <div className="error-message">{error}</div>}

        {loading ? (
          <div className="loading">Loading chat history...</div>
        ) : selectedUser ? (
          <div className="chat-history">
            {chatHistory.length > 0 ? (
              chatHistory.map((message, index) => (
                <div
                  key={index}
                  className={`chat-message ${message.role === 'user' ? 'user-message' : 'bot-message'}`}
                >
                  <div className="message-header">
                    <span className="message-role">{message.role === 'user' ? 'User' : 'Bot'}</span>
                    <span className="message-time">
                      {new Date(message.timestamp).toLocaleString()}
                    </span>
                  </div>
                  <div className="message-content">{message.content}</div>
                </div>
              ))
            ) : (
              <div className="no-messages">No chat history available</div>
            )}
          </div>
        ) : (
          <div className="select-user-prompt">
            Please select a user to view their chat history
          </div>
        )}
      </div>
    </div>
  );
};

export default TherapistChat; 
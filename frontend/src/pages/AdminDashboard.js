import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api';
import '../styles/pages.css';
import '../styles/admin.css';

function AdminDashboard() {
  const navigate = useNavigate();
  const { role } = useAuth();
  
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    // Redirect if not admin
    if (role !== 'admin') {
      navigate('/login');
      return;
    }
    
    fetchStats();
  }, [role, navigate]);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/admin/stats');
      setStats(response.data);
      setError('');
    } catch (err) {
      console.error('Error fetching admin stats:', err);
      setError('Failed to load dashboard statistics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading-container">Loading dashboard...</div>;
  }

  return (
    <div className="page-container">
      <h1>Admin Dashboard</h1>
      <p className="subtitle">System overview and management</p>
      
      {error && <div className="error-message">{error}</div>}
      
      <div className="admin-dashboard">
        {/* Stats Overview Section */}
        <div className="admin-section">
          <h2>System Statistics</h2>
          {stats && (
            <div className="stats-grid">
              <div className="stat-card">
                <h3>Users</h3>
                <div className="stat-value">{stats.users.total}</div>
                <div className="stat-details">
                  <div>{stats.users.users} regular users</div>
                  <div>{stats.users.therapists} therapists</div>
                  <div>{stats.users.admins} admins</div>
                </div>
              </div>
              
              <div className="stat-card">
                <h3>Therapist Applications</h3>
                <div className="stat-value">{stats.applications.pending}</div>
                <div className="stat-details">
                  <div>Pending applications</div>
                </div>
              </div>
              
              <div className="stat-card">
                <h3>Activity</h3>
                <div className="stat-details">
                  <div>{stats.activity.total_messages} chat messages</div>
                  <div>{stats.activity.total_journal_entries} journal entries</div>
                </div>
              </div>
              
              <div className="stat-card">
                <h3>Knowledge Base</h3>
                <div className="stat-details">
                  <div>{stats.knowledge_base.disorders} disorders</div>
                  <div>{stats.knowledge_base.symptoms} symptoms</div>
                  <div>{stats.knowledge_base.relationships} relationships</div>
                </div>
              </div>
            </div>
          )}
        </div>
        
        {/* Quick Access Management Links */}
        <div className="admin-section">
          <h2>Management</h2>
          <div className="admin-links">
            <Link to="/admin/users" className="admin-link">
              <div className="admin-link-icon">👥</div>
              <div className="admin-link-text">
                <h3>User Management</h3>
                <p>Manage users, roles, and permissions</p>
              </div>
            </Link>
            
            <Link to="/admin/applications" className="admin-link">
              <div className="admin-link-icon">📝</div>
              <div className="admin-link-text">
                <h3>Therapist Applications</h3>
                <p>Review and approve therapist applications</p>
              </div>
            </Link>
            
            <Link to="/therapist/disorders" className="admin-link">
              <div className="admin-link-icon">🧠</div>
              <div className="admin-link-text">
                <h3>Knowledge Management</h3>
                <p>Manage disorders and symptoms database</p>
              </div>
            </Link>
            
            <Link to="/admin/create-admin" className="admin-link">
              <div className="admin-link-icon">👤</div>
              <div className="admin-link-text">
                <h3>Create Admin</h3>
                <p>Create additional admin accounts</p>
              </div>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AdminDashboard;
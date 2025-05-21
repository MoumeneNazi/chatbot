import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api';
import '../styles/pages.css';
import '../styles/admin.css';

function UserManagement() {
  const navigate = useNavigate();
  const { role } = useAuth();
  
  const [users, setUsers] = useState([]);
  const [totalUsers, setTotalUsers] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Search and filter state
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  
  // Pagination state
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(10);

  useEffect(() => {
    if (role !== 'admin') {
      navigate('/login');
      return;
    }
    
    fetchUsers();
  }, [role, navigate, page, limit, searchTerm, roleFilter]);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      
      // Calculate offset for pagination
      const skip = (page - 1) * limit;
      
      // Build query parameters
      const params = new URLSearchParams();
      params.append('skip', skip);
      params.append('limit', limit);
      
      if (searchTerm) {
        params.append('search', searchTerm);
      }
      
      if (roleFilter) {
        params.append('role', roleFilter);
      }
      
      const response = await api.get(`/api/admin/users?${params.toString()}`);
      setUsers(response.data.users);
      setTotalUsers(response.data.total);
      setError('');
    } catch (err) {
      console.error('Error fetching users:', err);
      setError('Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1); // Reset to first page when searching
    fetchUsers();
  };

  const clearFilters = () => {
    setSearchTerm('');
    setRoleFilter('');
    setPage(1);
  };

  const updateUserRole = async (userId, newRole) => {
    try {
      setLoading(true);
      await api.put(`/api/admin/users/${userId}/role`, { role: newRole });
      
      // Update local state to reflect the change
      setUsers(prevUsers => 
        prevUsers.map(user => 
          user.id === userId ? { ...user, role: newRole } : user
        )
      );
      
      setSuccess(`User role updated to ${newRole}`);
      
      // Clear success message after a delay
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      console.error('Error updating user role:', err);
      setError(err.response?.data?.detail || 'Failed to update user role');
    } finally {
      setLoading(false);
    }
  };

  const toggleAccountStatus = async (userId, username, currentStatus) => {
    const newStatus = !currentStatus;
    const action = newStatus ? 'activate' : 'deactivate';
    
    if (!window.confirm(`Are you sure you want to ${action} the account for "${username}"?`)) {
      return;
    }
    
    try {
      setLoading(true);
      await api.put(`/api/admin/users/${userId}/status`, { is_active: newStatus });
      
      // Update local state to reflect the change
      setUsers(prevUsers => 
        prevUsers.map(user => 
          user.id === userId ? { ...user, is_active: newStatus } : user
        )
      );
      
      setSuccess(`User account ${newStatus ? 'activated' : 'deactivated'} successfully`);
      
      // Clear success message after a delay
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      console.error('Error updating account status:', err);
      setError(err.response?.data?.detail || `Failed to ${action} account`);
    } finally {
      setLoading(false);
    }
  };

  const deleteUser = async (userId, username) => {
    if (!window.confirm(`Are you sure you want to delete user "${username}"? This action cannot be undone.`)) {
      return;
    }
    
    try {
      setLoading(true);
      await api.delete(`/api/admin/users/${userId}`);
      
      // Remove user from local state
      setUsers(prevUsers => prevUsers.filter(user => user.id !== userId));
      setTotalUsers(prev => prev - 1);
      
      setSuccess(`User "${username}" deleted successfully`);
      
      // Clear success message after a delay
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      console.error('Error deleting user:', err);
      setError(err.response?.data?.detail || 'Failed to delete user');
    } finally {
      setLoading(false);
    }
  };

  const totalPages = Math.ceil(totalUsers / limit);

  return (
    <div className="page-container">
      <h1>User Management</h1>
      <p className="subtitle">View and manage user accounts</p>
      
      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}
      
      <div className="admin-section">
        <div className="filter-bar">
          <form onSubmit={handleSearch} className="search-form">
            <input
              type="text"
              placeholder="Search by username or email"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <select 
              value={roleFilter} 
              onChange={(e) => setRoleFilter(e.target.value)}
            >
              <option value="">All Roles</option>
              <option value="user">Users</option>
              <option value="therapist">Therapists</option>
              <option value="admin">Admins</option>
            </select>
            <button type="submit" className="btn primary-btn">Search</button>
            <button type="button" className="btn secondary-btn" onClick={clearFilters}>Clear</button>
          </form>
          
          <div className="records-info">
            Showing {users.length} of {totalUsers} users
          </div>
        </div>
        
        <div className="table-container">
          {loading && <div className="loading-overlay">Loading...</div>}
          
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Username</th>
                <th>Email</th>
                <th>Role</th>
                <th>Created At</th>
                <th>Last Login</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map(user => (
                <tr key={user.id} className={!user.is_active ? 'inactive-user' : ''}>
                  <td>{user.id}</td>
                  <td>{user.username}</td>
                  <td>{user.email}</td>
                  <td>
                    <select
                      value={user.role}
                      onChange={(e) => updateUserRole(user.id, e.target.value)}
                      disabled={loading}
                    >
                      <option value="user">User</option>
                      <option value="therapist">Therapist</option>
                      <option value="admin">Admin</option>
                    </select>
                  </td>
                  <td>{new Date(user.created_at).toLocaleString()}</td>
                  <td>
                    {user.last_login 
                      ? new Date(user.last_login).toLocaleString() 
                      : 'Never'
                    }
                  </td>
                  <td>
                    <span className={`status-badge ${user.is_active ? 'active' : 'inactive'}`}>
                      {user.is_active ? 'Active' : 'Deactivated'}
                    </span>
                  </td>
                  <td className="actions-cell">
                    <button 
                      className={`btn ${user.is_active ? 'warning-btn' : 'success-btn'} small-btn`}
                      onClick={() => toggleAccountStatus(user.id, user.username, user.is_active)}
                      disabled={loading}
                    >
                      {user.is_active ? 'Deactivate' : 'Activate'}
                    </button>
                    <button 
                      className="btn danger-btn small-btn"
                      onClick={() => deleteUser(user.id, user.username)}
                      disabled={loading}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
              
              {users.length === 0 && !loading && (
                <tr>
                  <td colSpan="8" className="empty-table-message">
                    No users found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        
        <div className="pagination">
          <button 
            className="btn secondary-btn small-btn"
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1 || loading}
          >
            Previous
          </button>
          
          <span className="page-info">
            Page {page} of {totalPages || 1}
          </span>
          
          <button 
            className="btn secondary-btn small-btn"
            onClick={() => setPage(p => p + 1)}
            disabled={page >= totalPages || loading}
          >
            Next
          </button>
          
          <select 
            value={limit}
            onChange={(e) => {
              setLimit(Number(e.target.value));
              setPage(1);
            }}
            disabled={loading}
          >
            <option value="5">5 per page</option>
            <option value="10">10 per page</option>
            <option value="25">25 per page</option>
            <option value="50">50 per page</option>
          </select>
        </div>
      </div>
    </div>
  );
}

export default UserManagement; 
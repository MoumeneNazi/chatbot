import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api';
import '../styles/pages.css';
import '../styles/admin.css';

function ApplicationManagement() {
  const navigate = useNavigate();
  const { role } = useAuth();
  
  const [applications, setApplications] = useState([]);
  const [totalApplications, setTotalApplications] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Filter state
  const [statusFilter, setStatusFilter] = useState('');
  
  // Pagination state
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(10);

  useEffect(() => {
    if (role !== 'admin') {
      navigate('/login');
      return;
    }
    
    fetchApplications();
  }, [role, navigate, page, limit, statusFilter]);

  const fetchApplications = async () => {
    try {
      setLoading(true);
      
      // Calculate offset for pagination
      const skip = (page - 1) * limit;
      
      // Build query parameters
      const params = new URLSearchParams();
      params.append('skip', skip);
      params.append('limit', limit);
      
      if (statusFilter) {
        params.append('status', statusFilter);
      }
      
      const response = await api.get(`/api/admin/applications?${params.toString()}`);
      setApplications(response.data.applications);
      setTotalApplications(response.data.total);
      setError('');
    } catch (err) {
      console.error('Error fetching applications:', err);
      setError('Failed to load applications');
    } finally {
      setLoading(false);
    }
  };

  const updateApplicationStatus = async (applicationId, newStatus) => {
    try {
      setLoading(true);
      await api.put(`/api/admin/applications/${applicationId}/status`, { status: newStatus });
      
      // Update local state to reflect the change
      setApplications(prevApps => 
        prevApps.map(app => 
          app.id === applicationId ? { ...app, status: newStatus } : app
        )
      );
      
      setSuccess(`Application status updated to ${newStatus}`);
      
      // Clear success message after a delay
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      console.error('Error updating application status:', err);
      setError(err.response?.data?.detail || 'Failed to update application status');
    } finally {
      setLoading(false);
    }
  };

  const clearFilters = () => {
    setStatusFilter('');
    setPage(1);
  };

  const viewDocument = (documentPath) => {
    if (!documentPath) {
      alert('No document available');
      return;
    }
    
    window.open(`/uploads/${documentPath}`, '_blank');
  };

  const totalPages = Math.ceil(totalApplications / limit);

  return (
    <div className="page-container">
      <h1>Therapist Applications</h1>
      <p className="subtitle">Review and manage therapist applications</p>
      
      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}
      
      <div className="admin-section">
        <div className="filter-bar">
          <div className="filter-controls">
            <select 
              value={statusFilter} 
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setPage(1);
              }}
            >
              <option value="">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
            </select>
            <button type="button" className="btn secondary-btn" onClick={clearFilters}>Clear Filters</button>
          </div>
          
          <div className="records-info">
            Showing {applications.length} of {totalApplications} applications
          </div>
        </div>
        
        <div className="table-container">
          {loading && <div className="loading-overlay">Loading...</div>}
          
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Full Name</th>
                <th>Email</th>
                <th>Specialty</th>
                <th>License #</th>
                <th>Experience</th>
                <th>Document</th>
                <th>Status</th>
                <th>Applied On</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {applications.map(app => (
                <tr key={app.id} className={`status-${app.status}`}>
                  <td>{app.id}</td>
                  <td>{app.full_name}</td>
                  <td>{app.email}</td>
                  <td>{app.specialty}</td>
                  <td>{app.license_number}</td>
                  <td>{app.experience_years} years</td>
                  <td>
                    {app.document_path ? (
                      <button
                        className="btn secondary-btn small-btn"
                        onClick={() => viewDocument(app.document_path)}
                      >
                        View
                      </button>
                    ) : (
                      <span>None</span>
                    )}
                  </td>
                  <td>
                    <span className={`status-badge ${app.status}`}>
                      {app.status.charAt(0).toUpperCase() + app.status.slice(1)}
                    </span>
                  </td>
                  <td>{new Date(app.created_at).toLocaleDateString()}</td>
                  <td className="actions-cell">
                    {app.status === 'pending' && (
                      <>
                        <button 
                          className="btn success-btn small-btn"
                          onClick={() => updateApplicationStatus(app.id, 'approved')}
                          disabled={loading}
                        >
                          Approve
                        </button>
                        <button 
                          className="btn danger-btn small-btn"
                          onClick={() => updateApplicationStatus(app.id, 'rejected')}
                          disabled={loading}
                        >
                          Reject
                        </button>
                      </>
                    )}
                    {app.status !== 'pending' && (
                      <button 
                        className="btn warning-btn small-btn"
                        onClick={() => updateApplicationStatus(app.id, 'pending')}
                        disabled={loading}
                      >
                        Reset
                      </button>
                    )}
                  </td>
                </tr>
              ))}
              
              {applications.length === 0 && !loading && (
                <tr>
                  <td colSpan="10" className="empty-table-message">
                    No applications found
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

export default ApplicationManagement; 
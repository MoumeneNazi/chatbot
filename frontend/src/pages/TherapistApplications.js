import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api';
import '../styles/pages.css';
import '../styles/admin.css';

function TherapistApplications() {
  const navigate = useNavigate();
  const { role } = useAuth();
  
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Filter state
  const [statusFilter, setStatusFilter] = useState('');

  useEffect(() => {
    if (role !== 'therapist') {
      navigate('/login');
      return;
    }
    
    fetchApplications();
  }, [role, navigate, statusFilter]);

  const fetchApplications = async () => {
    try {
      setLoading(true);
      
      // Build query parameters
      const params = new URLSearchParams();
      
      if (statusFilter) {
        params.append('status', statusFilter);
      }
      
      const response = await api.get(`/api/therapist/applications${params.toString() ? `?${params.toString()}` : ''}`);
      setApplications(response.data);
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
      await api.put(`/api/therapist/applications/${applicationId}/status`, { status: newStatus });
      
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
  };

  const viewDocument = (documentPath) => {
    if (!documentPath) {
      alert('No document available');
      return;
    }
    
    window.open(`/uploads/${documentPath}`, '_blank');
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

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
            Showing {applications.length} applications
          </div>
        </div>
        
        {loading ? (
          <div className="loading-message">Loading applications...</div>
        ) : applications.length > 0 ? (
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
                      <button className="link-btn" onClick={() => viewDocument(app.document_path)}>
                        View Document
                      </button>
                    </p>
                  )}
                </div>
                {app.status === 'pending' && (
                  <div className="application-actions">
                    <button 
                      className="approve-btn"
                      onClick={() => updateApplicationStatus(app.id, 'approved')}
                    >
                      Approve
                    </button>
                    <button 
                      className="reject-btn"
                      onClick={() => updateApplicationStatus(app.id, 'rejected')}
                    >
                      Reject
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="no-data-message">No applications found</div>
        )}
      </div>
    </div>
  );
}

export default TherapistApplications; 
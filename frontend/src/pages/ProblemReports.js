import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api';
import '../styles/pages.css';

function ProblemReports() {
  const navigate = useNavigate();
  const { role } = useAuth();
  
  const [reports, setReports] = useState([]);
  const [statusFilter, setStatusFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    // Only allow access to therapists and admins
    if (role !== 'therapist' && role !== 'admin') {
      navigate('/login');
      return;
    }
    
    fetchReports();
  }, [role, navigate, statusFilter, categoryFilter]);

  const fetchReports = async () => {
    setLoading(true);
    try {
      let url = '/api/problems';
      const params = [];
      
      if (statusFilter) {
        params.push(`status=${statusFilter}`);
      }
      
      if (categoryFilter) {
        params.push(`category=${categoryFilter}`);
      }
      
      if (params.length > 0) {
        url += `?${params.join('&')}`;
      }
      
      const response = await api.get(url);
      setReports(response.data);
      setError('');
    } catch (err) {
      console.error('Error fetching problem reports:', err);
      setError('Failed to fetch problem reports');
    } finally {
      setLoading(false);
    }
  };

  const updateReportStatus = async (reportId, newStatus) => {
    setLoading(true);
    setError('');
    setSuccess('');
    
    try {
      await api.put(`/api/problems/${reportId}/status`, { status: newStatus });
      setSuccess(`Report status updated to ${newStatus}`);
      
      // Update the report status in the local state
      setReports(reports.map(report => 
        report.id === reportId ? { ...report, status: newStatus } : report
      ));
    } catch (err) {
      console.error('Error updating report status:', err);
      setError(err.response?.data?.detail || 'Failed to update report status');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  return (
    <div className="page-container">
      <h1>Problem Reports</h1>
      <p className="subtitle">
        Manage and address problem reports submitted by users and therapists
      </p>
      
      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}
      
      <div className="filter-container">
        <div className="filter-group">
          <label htmlFor="statusFilter">Status:</label>
          <select 
            id="statusFilter" 
            value={statusFilter} 
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="in_progress">In Progress</option>
            <option value="resolved">Resolved</option>
            <option value="closed">Closed</option>
          </select>
        </div>
        
        <div className="filter-group">
          <label htmlFor="categoryFilter">Category:</label>
          <select 
            id="categoryFilter" 
            value={categoryFilter} 
            onChange={(e) => setCategoryFilter(e.target.value)}
          >
            <option value="">All Categories</option>
            <option value="technical">Technical</option>
            <option value="content">Content</option>
            <option value="suggestion">Suggestion</option>
            <option value="other">Other</option>
          </select>
        </div>
        
        <button 
          className="btn refresh-btn" 
          onClick={fetchReports} 
          disabled={loading}
        >
          {loading ? 'Loading...' : 'Refresh'}
        </button>
      </div>
      
      <div className="reports-list">
        {reports.length === 0 ? (
          <p className="no-data-message">No problem reports found</p>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Title</th>
                <th>Category</th>
                <th>Status</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {reports.map(report => (
                <tr key={report.id} className={`status-${report.status}`}>
                  <td>{report.id}</td>
                  <td>{report.title}</td>
                  <td>{report.category}</td>
                  <td>
                    <span className={`status-badge ${report.status}`}>
                      {report.status.replace('_', ' ')}
                    </span>
                  </td>
                  <td>{formatDate(report.created_at)}</td>
                  <td>
                    <div className="action-buttons">
                      {report.status === 'pending' && (
                        <button 
                          className="btn action-btn"
                          onClick={() => updateReportStatus(report.id, 'in_progress')}
                          disabled={loading}
                        >
                          Start
                        </button>
                      )}
                      
                      {report.status === 'in_progress' && (
                        <button 
                          className="btn action-btn"
                          onClick={() => updateReportStatus(report.id, 'resolved')}
                          disabled={loading}
                        >
                          Resolve
                        </button>
                      )}
                      
                      {(report.status === 'pending' || report.status === 'in_progress') && (
                        <button 
                          className="btn action-btn close-btn"
                          onClick={() => updateReportStatus(report.id, 'closed')}
                          disabled={loading}
                        >
                          Close
                        </button>
                      )}
                      
                      {report.status === 'resolved' && (
                        <button 
                          className="btn action-btn"
                          onClick={() => updateReportStatus(report.id, 'closed')}
                          disabled={loading}
                        >
                          Close
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export default ProblemReports; 
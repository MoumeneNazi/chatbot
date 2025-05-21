import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import '../styles/components.css';

function ReportProblem({ onClose }) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: 'technical' // Default category
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');
    
    try {
      await api.post('/api/problems', formData);
      setSuccess('Your problem report has been submitted successfully!');
      setFormData({
        title: '',
        description: '',
        category: 'technical'
      });
      
      // Close the modal after 2 seconds if onClose prop exists
      if (onClose) {
        setTimeout(() => {
          onClose();
        }, 2000);
      }
    } catch (err) {
      console.error('Error submitting problem report:', err);
      setError(err.response?.data?.detail || 'Failed to submit problem report. Please try again.');
      
      if (err.response?.status === 401) {
        // Handle unauthorized error
      }
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="report-problem-container">
      <h2>Report a Problem</h2>
      
      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}
      
      <form onSubmit={handleSubmit} className="report-form">
        <div className="form-group">
          <label htmlFor="title">Title</label>
          <input
            type="text"
            id="title"
            name="title"
            placeholder="Brief description of the issue"
            value={formData.title}
            onChange={handleChange}
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="category">Category</label>
          <select
            id="category"
            name="category"
            value={formData.category}
            onChange={handleChange}
            required
          >
            <option value="technical">Technical Issue</option>
            <option value="content">Content Issue</option>
            <option value="suggestion">Suggestion</option>
            <option value="other">Other</option>
          </select>
        </div>
        
        <div className="form-group">
          <label htmlFor="description">Description</label>
          <textarea
            id="description"
            name="description"
            placeholder="Please provide details about the problem"
            value={formData.description}
            onChange={handleChange}
            rows={5}
            required
          />
        </div>
        
        <div className="form-actions">
          {onClose && (
            <button 
              type="button" 
              className="btn secondary-btn"
              onClick={onClose}
            >
              Cancel
            </button>
          )}
          <button 
            type="submit" 
            className="btn primary-btn"
            disabled={loading}
          >
            {loading ? 'Submitting...' : 'Submit Report'}
          </button>
        </div>
      </form>
    </div>
  );
}

export default ReportProblem; 
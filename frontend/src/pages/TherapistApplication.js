import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api';
import '../styles/therapist-application.css';

function TherapistApplication() {
  const [form, setForm] = useState({
    full_name: '',
    email: '',
    specialty: '',
    license_number: '',
    certification: '',
    experience_years: ''
  });
  const [document, setDocument] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [applicationStatus, setApplicationStatus] = useState(null);
  const { token } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    // Check if user already has an application
    const checkApplicationStatus = async () => {
      try {
        const response = await api.get('/api/therapist/application/status');
        setApplicationStatus(response.data);
      } catch (error) {
        console.error('Error fetching application status:', error);
      }
    };

    if (token) {
      checkApplicationStatus();
    } else {
      navigate('/login');
    }
  }, [token, navigate]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
  };

  const handleFileChange = (e) => {
    setDocument(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      // Create form data for file upload
      const formData = new FormData();
      Object.keys(form).forEach(key => {
        formData.append(key, form[key]);
      });
      
      if (document) {
        formData.append('document', document);
      }

      await api.post('/api/therapist/apply', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      setSuccess('Your application has been submitted successfully! We will review it and get back to you.');
      // Refresh application status
      const response = await api.get('/api/therapist/application/status');
      setApplicationStatus(response.data);
    } catch (err) {
      console.error('Application submission error:', err);
      setError(err.response?.data?.detail || 'Failed to submit application. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // If user already has a pending or processed application
  if (applicationStatus && applicationStatus.status !== 'not_applied') {
    return (
      <div className="therapist-application-container">
        <div className="application-status-box">
          <h2>Application Status</h2>
          <div className={`status-badge ${applicationStatus.status}`}>
            {applicationStatus.status.toUpperCase()}
          </div>
          <p>
            <strong>Applied:</strong> {new Date(applicationStatus.applied_at).toLocaleDateString()}
          </p>
          <p>
            <strong>Last Updated:</strong> {new Date(applicationStatus.updated_at).toLocaleDateString()}
          </p>
          {applicationStatus.status === 'pending' && (
            <p className="status-message">
              Your application is currently under review. We'll notify you once a decision has been made.
            </p>
          )}
          {applicationStatus.status === 'approved' && (
            <p className="status-message success">
              Congratulations! Your application has been approved. You now have therapist privileges.
            </p>
          )}
          {applicationStatus.status === 'rejected' && (
            <p className="status-message error">
              Unfortunately, your application has been rejected. Please contact support for more information.
            </p>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="therapist-application-container">
      <div className="application-form-box">
        <h2>Therapist Application</h2>
        <p className="form-description">
          Complete this form to apply for therapist privileges. Please provide accurate professional information.
          All applications are reviewed by our team.
        </p>
        
        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="full_name">Full Name *</label>
            <input
              type="text"
              id="full_name"
              name="full_name"
              value={form.full_name}
              onChange={handleChange}
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="email">Email Address *</label>
            <input
              type="email"
              id="email"
              name="email"
              value={form.email}
              onChange={handleChange}
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="specialty">Specialty/Field *</label>
            <input
              type="text"
              id="specialty"
              name="specialty"
              value={form.specialty}
              onChange={handleChange}
              required
              placeholder="e.g., Clinical Psychology, Psychiatry"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="license_number">License Number *</label>
            <input
              type="text"
              id="license_number"
              name="license_number"
              value={form.license_number}
              onChange={handleChange}
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="certification">Certification/Degree *</label>
            <input
              type="text"
              id="certification"
              name="certification"
              value={form.certification}
              onChange={handleChange}
              required
              placeholder="e.g., Ph.D. in Psychology, MD"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="experience_years">Years of Experience *</label>
            <input
              type="number"
              id="experience_years"
              name="experience_years"
              value={form.experience_years}
              onChange={handleChange}
              required
              min="0"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="document">Upload Credentials (PDF, JPG, PNG)</label>
            <input
              type="file"
              id="document"
              name="document"
              onChange={handleFileChange}
              accept=".pdf,.jpg,.jpeg,.png"
            />
            <small className="file-help">Upload your license, certification, or other relevant credentials.</small>
          </div>
          
          <button 
            type="submit" 
            className="submit-button" 
            disabled={loading}
          >
            {loading ? 'Submitting...' : 'Submit Application'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default TherapistApplication; 
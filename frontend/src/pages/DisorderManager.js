import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api';
import '../styles/pages.css';

function DisorderManager() {
  const navigate = useNavigate();
  const { role } = useAuth();
  
  const [disorders, setDisorders] = useState([]);
  const [selectedDisorder, setSelectedDisorder] = useState(null);
  const [symptoms, setSymptoms] = useState([]);
  const [disorderSymptoms, setDisorderSymptoms] = useState([]);
  
  const [newDisorderName, setNewDisorderName] = useState('');
  const [newSymptomName, setNewSymptomName] = useState('');
  const [linkSymptomName, setLinkSymptomName] = useState('');
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    if (role !== 'therapist' && role !== 'admin') {
      navigate('/login');
      return;
    }
    
    fetchDisorders();
    fetchAllSymptoms();
  }, [role, navigate]);

  useEffect(() => {
    if (selectedDisorder) {
      fetchDisorderSymptoms(selectedDisorder);
    } else {
      setDisorderSymptoms([]);
    }
  }, [selectedDisorder]);

  const fetchDisorders = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/therapist/disorders');
      setDisorders(response.data);
      setError('');
    } catch (err) {
      console.error('Error fetching disorders:', err);
      setError('Failed to fetch disorders');
    } finally {
      setLoading(false);
    }
  };

  const fetchAllSymptoms = async () => {
    try {
      const response = await api.get('/api/therapist/symptoms');
      setSymptoms(response.data);
    } catch (err) {
      console.error('Error fetching symptoms:', err);
    }
  };

  const fetchDisorderSymptoms = async (disorderName) => {
    try {
      const response = await api.get(`/api/therapist/symptoms?disorder=${disorderName}`);
      setDisorderSymptoms(response.data);
    } catch (err) {
      console.error('Error fetching disorder symptoms:', err);
    }
  };

  const addDisorder = async (e) => {
    e.preventDefault();
    if (!newDisorderName.trim()) return;
    
    setLoading(true);
    setError('');
    setSuccess('');
    
    try {
      await api.post('/api/therapist/disorders', { name: newDisorderName });
      setSuccess(`Disorder "${newDisorderName}" added successfully`);
      setNewDisorderName('');
      fetchDisorders();
    } catch (err) {
      console.error('Error adding disorder:', err);
      setError(err.response?.data?.detail || 'Failed to add disorder');
    } finally {
      setLoading(false);
    }
  };

  const addSymptom = async (e) => {
    e.preventDefault();
    if (!newSymptomName.trim()) return;
    
    setLoading(true);
    setError('');
    setSuccess('');
    
    try {
      await api.post('/api/therapist/symptoms', { name: newSymptomName });
      setSuccess(`Symptom "${newSymptomName}" added successfully`);
      setNewSymptomName('');
      fetchAllSymptoms();
    } catch (err) {
      console.error('Error adding symptom:', err);
      setError(err.response?.data?.detail || 'Failed to add symptom');
    } finally {
      setLoading(false);
    }
  };

  const linkSymptomToDisorder = async (e) => {
    e.preventDefault();
    if (!selectedDisorder || !linkSymptomName) return;
    
    setLoading(true);
    setError('');
    setSuccess('');
    
    try {
      await api.post(`/api/therapist/disorders/${selectedDisorder}/symptoms`, { name: linkSymptomName });
      setSuccess(`Symptom "${linkSymptomName}" linked to "${selectedDisorder}"`);
      setLinkSymptomName('');
      fetchDisorderSymptoms(selectedDisorder);
    } catch (err) {
      console.error('Error linking symptom:', err);
      setError(err.response?.data?.detail || 'Failed to link symptom');
    } finally {
      setLoading(false);
    }
  };

  const deleteDisorder = async (disorderName) => {
    if (!window.confirm(`Are you sure you want to delete the disorder "${disorderName}"?`)) {
      return;
    }
    
    setLoading(true);
    setError('');
    setSuccess('');
    
    try {
      await api.delete(`/api/therapist/disorders/${disorderName}`);
      setSuccess(`Disorder "${disorderName}" deleted successfully`);
      if (selectedDisorder === disorderName) {
        setSelectedDisorder(null);
      }
      fetchDisorders();
    } catch (err) {
      console.error('Error deleting disorder:', err);
      setError(err.response?.data?.detail || 'Failed to delete disorder');
    } finally {
      setLoading(false);
    }
  };

  const deleteSymptom = async (symptomName) => {
    if (!window.confirm(`Are you sure you want to delete the symptom "${symptomName}"?`)) {
      return;
    }
    
    setLoading(true);
    setError('');
    setSuccess('');
    
    try {
      await api.delete(`/api/therapist/symptoms/${symptomName}`);
      setSuccess(`Symptom "${symptomName}" deleted successfully`);
      fetchAllSymptoms();
      if (selectedDisorder) {
        fetchDisorderSymptoms(selectedDisorder);
      }
    } catch (err) {
      console.error('Error deleting symptom:', err);
      setError(err.response?.data?.detail || 'Failed to delete symptom');
    } finally {
      setLoading(false);
    }
  };

  const unlinkSymptom = async (symptomName) => {
    if (!selectedDisorder) return;
    
    setLoading(true);
    setError('');
    setSuccess('');
    
    try {
      await api.delete(`/api/therapist/disorders/${selectedDisorder}/symptoms/${symptomName}`);
      setSuccess(`Symptom "${symptomName}" unlinked from "${selectedDisorder}"`);
      fetchDisorderSymptoms(selectedDisorder);
    } catch (err) {
      console.error('Error unlinking symptom:', err);
      setError(err.response?.data?.detail || 'Failed to unlink symptom');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      <h1>Disorder & Symptom Management</h1>
      <p className="subtitle">
        Manage mental health disorders and symptoms used by the chatbot for diagnosis
      </p>
      
      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}
      
      <div className="content-grid">
        <div className="left-panel">
          <div className="section">
            <h2>Add New Disorder</h2>
            <form onSubmit={addDisorder} className="form">
              <div className="form-group">
                <input
                  type="text"
                  placeholder="Disorder Name"
                  value={newDisorderName}
                  onChange={(e) => setNewDisorderName(e.target.value)}
                  required
                />
              </div>
              <button 
                type="submit" 
                className="btn primary-btn" 
                disabled={loading || !newDisorderName.trim()}
              >
                Add Disorder
              </button>
            </form>
          </div>
          
          <div className="section">
            <h2>Add New Symptom</h2>
            <form onSubmit={addSymptom} className="form">
              <div className="form-group">
                <input
                  type="text"
                  placeholder="Symptom Name"
                  value={newSymptomName}
                  onChange={(e) => setNewSymptomName(e.target.value)}
                  required
                />
              </div>
              <button 
                type="submit" 
                className="btn primary-btn" 
                disabled={loading || !newSymptomName.trim()}
              >
                Add Symptom
              </button>
            </form>
          </div>
          
          <div className="section">
            <h2>All Symptoms</h2>
            <div className="list-container">
              {symptoms.length > 0 ? (
                <ul className="item-list">
                  {symptoms.map((symptom, index) => (
                    <li key={index} className="list-item">
                      <span>{symptom}</span>
                      <button 
                        className="btn danger-btn small-btn"
                        onClick={() => deleteSymptom(symptom)}
                        title="Delete symptom"
                      >
                        ✕
                      </button>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="empty-message">No symptoms found</p>
              )}
            </div>
          </div>
        </div>
        
        <div className="right-panel">
          <div className="section">
            <h2>Disorders</h2>
            <div className="list-container">
              {disorders.length > 0 ? (
                <ul className="item-list">
                  {disorders.map((disorder, index) => (
                    <li 
                      key={index} 
                      className={`list-item ${selectedDisorder === disorder ? 'selected' : ''}`}
                      onClick={() => setSelectedDisorder(disorder)}
                    >
                      <span>{disorder}</span>
                      <button 
                        className="btn danger-btn small-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteDisorder(disorder);
                        }}
                        title="Delete disorder"
                      >
                        ✕
                      </button>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="empty-message">No disorders found</p>
              )}
            </div>
          </div>
          
          {selectedDisorder && (
            <>
              <div className="section">
                <h2>Link Symptom to {selectedDisorder}</h2>
                <form onSubmit={linkSymptomToDisorder} className="form">
                  <div className="form-group">
                    <select
                      value={linkSymptomName}
                      onChange={(e) => setLinkSymptomName(e.target.value)}
                      required
                    >
                      <option value="">Select a symptom</option>
                      {symptoms
                        .filter(s => !disorderSymptoms.includes(s))
                        .map((symptom, index) => (
                          <option key={index} value={symptom}>
                            {symptom}
                          </option>
                        ))}
                    </select>
                  </div>
                  <button 
                    type="submit" 
                    className="btn primary-btn" 
                    disabled={loading || !linkSymptomName}
                  >
                    Link Symptom
                  </button>
                </form>
              </div>
              
              <div className="section">
                <h2>Symptoms of {selectedDisorder}</h2>
                <div className="list-container">
                  {disorderSymptoms.length > 0 ? (
                    <ul className="item-list">
                      {disorderSymptoms.map((symptom, index) => (
                        <li key={index} className="list-item">
                          <span>{symptom}</span>
                          <button 
                            className="btn warning-btn small-btn"
                            onClick={() => unlinkSymptom(symptom)}
                            title="Unlink from disorder"
                          >
                            Unlink
                          </button>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="empty-message">No symptoms linked to this disorder</p>
                  )}
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default DisorderManager; 
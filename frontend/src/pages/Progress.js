import React, { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import api from "../api";
import "../styles/progress.css";

function Progress() {
  const [progressData, setProgressData] = useState(null);
  const [treatments, setTreatments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { token } = useAuth();

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // Fetch progress data
        const progressResponse = await api.get("/api/progress");
        if (progressResponse.data) {
          setProgressData(progressResponse.data);
        }

        // Fetch treatment plans
        const treatmentsResponse = await api.get("/api/treatments");
        if (treatmentsResponse.data) {
          setTreatments(treatmentsResponse.data);
        }
      } catch (err) {
        console.error("Error fetching data:", err);
        // Make sure we store only a string in the error state
        setError(err.response?.data?.detail || "Failed to load your progress data. Please try again later.");
      } finally {
        setLoading(false);
      }
    };

    if (token) {
      fetchData();
    }
  }, [token]);

  if (loading) {
    return <div className="loading">Loading progress data...</div>;
  }

  // Ensure error is always rendered as a string
  if (error) {
    return <div className="error">{typeof error === 'object' ? JSON.stringify(error) : error}</div>;
  }

  return (
    <div className="page-container">
      <div className="progress-page">
        <h1>My Progress</h1>
        
        {progressData && (
          <div className="progress-summary">
            <div className="progress-section">
              <h2>Mood Summary</h2>
              <div className="stat-cards">
                <div className="stat-card">
                  <h3>Average Mood</h3>
                  <p className="stat-value">
                    {typeof progressData.average_mood === 'number' 
                      ? progressData.average_mood.toFixed(1) 
                      : 'N/A'}
                  </p>
                  <p className="stat-label">Out of 10</p>
                </div>
                <div className="stat-card">
                  <h3>Journal Entries</h3>
                  <p className="stat-value">{progressData.total_entries || 0}</p>
                  <p className="stat-label">Last 30 days</p>
                </div>
                <div className="stat-card">
                  <h3>Sentiment</h3>
                  <p className="stat-value">
                    {typeof progressData.average_sentiment === 'number'
                      ? progressData.average_sentiment.toFixed(2)
                      : 'N/A'}
                  </p>
                  <p className="stat-label">-1 to 1 scale</p>
                </div>
              </div>
            </div>
          </div>
        )}
        
        <div className="treatment-section">
          <h2>My Treatment Plans</h2>
          {treatments.length > 0 ? (
            <div className="treatments-list">
              {treatments.map((treatment, index) => (
                <div key={index} className={`treatment-card ${treatment.status.toLowerCase()}`}>
                  <div className="treatment-header">
                    <h3>{treatment.disorder}</h3>
                    <span className={`status-badge ${treatment.status.toLowerCase()}`}>
                      {treatment.status}
                    </span>
                  </div>
                  
                  <div className="treatment-content">
                    <p>{treatment.treatment_plan}</p>
                  </div>
                  
                  <div className="treatment-footer">
                    <div className="treatment-dates">
                      <span>Started: {new Date(treatment.start_date).toLocaleDateString()}</span>
                      <span>Expected completion: {new Date(treatment.end_date).toLocaleDateString()}</span>
                    </div>
                    
                    {treatment.status === "Active" && (
                      <div className="progress-bar-container">
                        <div 
                          className="progress-bar" 
                          style={{ width: `${treatment.progress_percentage}%` }}
                        ></div>
                        <span className="progress-percentage">{treatment.progress_percentage}% Complete</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="no-treatments">
              <p>You don't have any active treatment plans.</p>
              <p>Your therapist will assign treatments based on your condition.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Progress;

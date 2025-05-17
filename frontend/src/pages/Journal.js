import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api';
import '../styles/journal.css';

function Journal() {
  const { role } = useAuth();
  const [entries, setEntries] = useState([]);
  const [treatmentProgress, setTreatmentProgress] = useState([]);
  const [newEntry, setNewEntry] = useState({
    entry: '',
    mood_rating: 5
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch journal entries and treatment progress
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        // Fetch journal entries
        const entriesResponse = await api.get('/journal/entries');
        setEntries(entriesResponse.data);

        // Fetch treatment progress if user role
        if (role === 'user') {
          const progressResponse = await api.get('/my/treatment/progress');
          setTreatmentProgress(progressResponse.data);
        }
        setLoading(false);
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Failed to load your journal data');
        setLoading(false);
      }
    };

    fetchData();
  }, [role]);

  const handleEntrySubmit = async (e) => {
    e.preventDefault();
    if (!newEntry.entry.trim()) return;

    try {
      await api.post('/journal/entry', newEntry);
      // Refresh entries after adding new one
      const response = await api.get('/journal/entries');
      setEntries(response.data);
      setNewEntry({ entry: '', mood_rating: 5 });
    } catch (err) {
      console.error('Error adding journal entry:', err);
      setError('Failed to add journal entry');
    }
  };

  if (loading) return <div className="loading">Loading your journal...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="journal-page">
      <div className="journal-section">
        <h2>My Journal</h2>
        
        {/* New Entry Form */}
        <form onSubmit={handleEntrySubmit} className="new-entry-form">
          <div className="form-group">
            <label htmlFor="entry">New Entry</label>
            <textarea
              id="entry"
              value={newEntry.entry}
              onChange={(e) => setNewEntry({ ...newEntry, entry: e.target.value })}
              placeholder="Write your thoughts..."
              rows={4}
            />
          </div>
          <div className="form-group">
            <label htmlFor="mood">Mood Rating (1-10)</label>
            <input
              type="range"
              id="mood"
              min="1"
              max="10"
              value={newEntry.mood_rating}
              onChange={(e) => setNewEntry({ ...newEntry, mood_rating: parseInt(e.target.value) })}
            />
            <span>{newEntry.mood_rating}</span>
          </div>
          <button type="submit">Save Entry</button>
        </form>

        {/* Journal Entries List */}
        <div className="entries-list">
          {entries.map((entry) => (
            <div key={entry.id} className="journal-entry">
              <div className="entry-header">
                <span className="timestamp">{new Date(entry.timestamp).toLocaleString()}</span>
                <span className="mood-rating">Mood: {entry.mood_rating}/10</span>
              </div>
              <p className="entry-content">{entry.entry}</p>
              {entry.sentiment_score !== null && (
                <div className="sentiment-score">
                  Sentiment: {entry.sentiment_score > 0 ? 'Positive' : entry.sentiment_score < 0 ? 'Negative' : 'Neutral'}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Treatment Progress Section (for users only) */}
      {role === 'user' && treatmentProgress.length > 0 && (
        <div className="treatment-section">
          <h2>Treatment Progress</h2>
          <div className="progress-list">
            {treatmentProgress.map((progress) => (
              <div key={progress.id} className="progress-entry">
                <div className="progress-header">
                  <span className="timestamp">{new Date(progress.timestamp).toLocaleString()}</span>
                  <span className="status">{progress.progress_status}</span>
                </div>
                <h3>Treatment Plan</h3>
                <p>{progress.treatment_plan}</p>
                <h3>Notes</h3>
                <p>{progress.notes}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default Journal;

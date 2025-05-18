import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api';
import '../styles/pages.css';
import '../styles/journal.css';

const Journal = () => {
  const navigate = useNavigate();
  const { token, role } = useAuth();
  const [entries, setEntries] = useState([]);
  const [newEntry, setNewEntry] = useState({
    title: '',
    content: '',
    mood: 'neutral',
    activities: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isWriting, setIsWriting] = useState(false);

  const moods = [
    'happy', 'excited', 'peaceful', 'neutral', 
    'anxious', 'sad', 'angry', 'stressed'
  ];

  const commonActivities = [
    'Exercise', 'Reading', 'Meditation', 'Work',
    'Social Activity', 'Therapy Session', 'Relaxation',
    'Outdoor Activity', 'Creative Activity', 'Family Time'
  ];

  const getMoodFromRating = (rating) => {
    // Convert 1-based rating back to mood string
    return moods[rating - 1] || 'neutral';
  };

  useEffect(() => {
    if (role !== 'user') {
      navigate('/login');
      return;
    }
    fetchEntries();
  }, [role, navigate]);

  const fetchEntries = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/journal');
      // Transform the entries to include mood string
      const transformedEntries = response.data.map(entry => ({
        ...entry,
        mood: getMoodFromRating(entry.mood_rating)
      }));
      setEntries(transformedEntries);
      setError(null);
    } catch (err) {
      console.error('Error fetching journal entries:', err);
      setError('Failed to load journal entries');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post('/api/journal', {
        entry: newEntry.content,
        mood_rating: moods.indexOf(newEntry.mood) + 1 // Convert mood to number rating
      });
      setNewEntry({
        title: '',
        content: '',
        mood: 'neutral',
        activities: []
      });
      setIsWriting(false);
      fetchEntries();
    } catch (err) {
      console.error('Error creating journal entry:', err);
      setError('Failed to save journal entry');
    }
  };

  const toggleActivity = (activity) => {
    setNewEntry(prev => ({
      ...prev,
      activities: prev.activities.includes(activity)
        ? prev.activities.filter(a => a !== activity)
        : [...prev.activities, activity]
    }));
  };

  return (
    <div className="page-container">
      <div className="journal-container">
        <div className="journal-header">
          <h1>My Journal</h1>
          <p className="subtitle">Express your thoughts and track your emotional journey</p>
          {!isWriting && (
            <button 
              onClick={() => setIsWriting(true)}
              className="new-entry-button"
            >
              Write New Entry
            </button>
          )}
        </div>

        {error && <div className="error-message">{error}</div>}

        {isWriting && (
          <form onSubmit={handleSubmit} className="journal-form">
            <div className="form-group">
              <label htmlFor="title">Title</label>
              <input
                type="text"
                id="title"
                value={newEntry.title}
                onChange={(e) => setNewEntry(prev => ({ ...prev, title: e.target.value }))}
                placeholder="Give your entry a title..."
                required
              />
            </div>

            <div className="form-group">
              <label>How are you feeling?</label>
              <div className="mood-selector">
                {moods.map(mood => (
                  <button
                    key={mood}
                    type="button"
                    className={`mood-button ${newEntry.mood === mood ? 'active' : ''}`}
                    onClick={() => setNewEntry(prev => ({ ...prev, mood }))}
                  >
                    {mood.charAt(0).toUpperCase() + mood.slice(1)}
                  </button>
                ))}
              </div>
            </div>

            <div className="form-group">
              <label>Activities (Optional)</label>
              <div className="activities-grid">
                {commonActivities.map(activity => (
                  <button
                    key={activity}
                    type="button"
                    className={`activity-tag ${newEntry.activities.includes(activity) ? 'active' : ''}`}
                    onClick={() => toggleActivity(activity)}
                  >
                    {activity}
                  </button>
                ))}
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="content">Your Thoughts</label>
              <textarea
                id="content"
                value={newEntry.content}
                onChange={(e) => setNewEntry(prev => ({ ...prev, content: e.target.value }))}
                placeholder="Write about your day, thoughts, feelings..."
                rows="8"
                required
              />
            </div>

            <div className="form-actions">
              <button 
                type="button" 
                className="cancel-button"
                onClick={() => setIsWriting(false)}
              >
                Cancel
              </button>
              <button type="submit" className="save-button">
                Save Entry
              </button>
            </div>
          </form>
        )}

        {loading ? (
          <div className="loading">Loading journal entries...</div>
        ) : (
          <div className="entries-list">
            {entries.map(entry => (
              <div key={entry.id} className="journal-entry">
                <div className="entry-header">
                  <h3>{entry.title}</h3>
                  <span className="entry-date">
                    {new Date(entry.timestamp).toLocaleDateString()}
                  </span>
                </div>
                <div className="entry-mood">
                  Mood: <span className={`mood-indicator ${entry.mood}`}>
                    {entry.mood.charAt(0).toUpperCase() + entry.mood.slice(1)}
                  </span>
                </div>
                {entry.activities && entry.activities.length > 0 && (
                  <div className="entry-activities">
                    {entry.activities.map(activity => (
                      <span key={activity} className="activity-tag">
                        {activity}
                      </span>
                    ))}
                  </div>
                )}
                <p className="entry-content">{entry.content}</p>
              </div>
            ))}
            {entries.length === 0 && (
              <div className="no-entries">
                No journal entries yet. Start writing to track your journey!
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Journal;

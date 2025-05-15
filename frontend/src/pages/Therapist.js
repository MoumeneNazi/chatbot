import React, { useState } from 'react';
import '../styles/therapist.css';

function Therapist() {
  const [username, setUsername] = useState('');
  const [entries, setEntries] = useState([]);
  const [error, setError] = useState('');

  const token = localStorage.getItem('token');

  const fetchUserJournal = async () => {
    setError('');
    try {
      const res = await fetch(`http://localhost:8000/admin/journal/${username}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await res.json();
      if (res.ok) {
        setEntries(data);
      } else {
        setError(data.detail || 'Access denied');
      }
    } catch {
      setError('Server error');
    }
  };

  return (
    <div className="therapist-page">
      <h2>Review User Journal</h2>
      <input
        placeholder="Enter username"
        value={username}
        onChange={e => setUsername(e.target.value)}
      />
      <button onClick={fetchUserJournal}>Fetch</button>
      {error && <p className="error">{error}</p>}
      <div className="journal-entries">
        {entries.map((e, i) => (
          <div key={i} className="entry-box">
            <p>{e.entry}</p>
            <span>{e.sentiment} — {new Date(e.timestamp).toLocaleString()}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Therapist;

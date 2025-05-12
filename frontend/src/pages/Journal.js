import React, { useState, useEffect } from 'react';
import { get, post } from '../api';

function Journal() {
  const [entry, setEntry] = useState('');
  const [logs, setLogs] = useState([]);

  const loadLogs = async () => {
    const data = await get('/journal');
    setLogs(data.entries || []);
  };

  const saveEntry = async () => {
    if (!entry) return;
    await post('/journal', { entry });
    setEntry('');
    loadLogs();
  };

  useEffect(() => { loadLogs(); }, []);

  return (
    <div className="form-box">
      <h2>Daily Journal</h2>
      <textarea rows={4} value={entry} onChange={e => setEntry(e.target.value)} />
      <button onClick={saveEntry}>Save</button>
      <div className="journal-list">
        {logs.map((log, i) => (
          <div key={i} className="log">
            <div><strong>{new Date(log.timestamp).toLocaleString()}</strong></div>
            <div>{log.entry}</div>
            {log.sentiment && <small>Sentiment: {log.sentiment}</small>}
          </div>
        ))}
      </div>
    </div>
  );
}

export default Journal;

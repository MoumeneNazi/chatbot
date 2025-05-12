import React, { useState } from 'react';
import { get } from '../api';

function Therapist() {
  const [username, setUsername] = useState('');
  const [chat, setChat] = useState([]);
  const [journal, setJournal] = useState([]);

  const fetchData = async () => {
    const chatData = await get(`/admin/chat/${username}`);
    const journalData = await get(`/admin/journal/${username}`);
    setChat(chatData);
    setJournal(journalData);
  };

  return (
    <div className="form-box">
      <h2>Therapist Review</h2>
      <input placeholder="Username" onChange={e => setUsername(e.target.value)} />
      <button onClick={fetchData}>Fetch User Data</button>

      <h3>Chat History</h3>
      {chat.map((c, i) => (
        <div key={i}><strong>{c.role}:</strong> {c.message}</div>
      ))}

      <h3>Journal Entries</h3>
      {journal.map((j, i) => (
        <div key={i}>
          <strong>{new Date(j.timestamp).toLocaleString()}</strong><br />
          {j.entry}<br />
          {j.sentiment && <em>Sentiment: {j.sentiment}</em>}
        </div>
      ))}
    </div>
  );
}

export default Therapist;

import React, { useState, useEffect } from 'react';
import '../styles/journal.css';

function Journal() {
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [journalEntries, setJournalEntries] = useState([]);
  const token = localStorage.getItem('token');

  const fetchUsers = async () => {
    try {
      const res = await fetch('http://localhost:8000/admin/users', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setUsers(data);
      } else {
        console.error('Failed to fetch users');
      }
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  const fetchJournalEntries = async (username) => {
    try {
      const res = await fetch(`http://localhost:8000/admin/journal/${username}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setJournalEntries(data);
        setSelectedUser(username);
      } else {
        console.error('Failed to fetch journal entries');
      }
    } catch (error) {
      console.error('Error fetching journal entries:', error);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  return (
    <div className="journal-page">
      <h2>Journal Entries</h2>
      <div className="user-list">
        <h3>Users</h3>
        <ul>
          {users.map((user) => (
            <li key={user.username} onClick={() => fetchJournalEntries(user.username)}>
              {user.username} ({user.role})
            </li>
          ))}
        </ul>
      </div>
      <div className="journal-entries">
        <h3>{selectedUser ? `${selectedUser}'s Journal Entries` : 'Select a user to view their journal entries'}</h3>
        <ul>
          {journalEntries.map((entry, i) => (
            <li key={i}>
              <p>{entry.entry}</p>
              <span>Sentiment: {entry.sentiment}</span>
              <span>{new Date(entry.timestamp).toLocaleString()}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default Journal;

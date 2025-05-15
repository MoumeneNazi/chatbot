import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from '../api';
import '../styles/userDashboard.css';

const UserDashboard = () => {
  const [messages, setMessages] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");
    const role = localStorage.getItem("role");

    if (!token || role !== "user") {
      navigate("/login");
    }

    axios
      .get("/chat/history", {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then((res) => setMessages(res.data))
      .catch((err) => console.error(err));
  }, [navigate]);

  return (
    <div className="user-dashboard">
      <h1>Your Personal Mental Health Journal</h1>
      <div className="message-list">
        {messages.length === 0 ? (
          <p>No messages yet. Start chatting!</p>
        ) : (
          messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.role}`}>
              <strong>{msg.role === 'user' ? 'You' : 'Bot'}</strong>: {msg.message}
              <span className="timestamp">{new Date(msg.timestamp).toLocaleString()}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default UserDashboard;

import React, { useState, useEffect, useRef } from 'react';
import '../styles/chat.css';

function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const token = localStorage.getItem('token');
  const chatBoxRef = useRef(null); // Reference to the chat box for auto-scroll

  const fetchHistory = async () => {
    try {
      const res = await fetch('http://localhost:8000/chat/history', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setMessages(data);
      } else {
        console.error('Failed to fetch chat history');
      }
    } catch (error) {
      console.error('Error fetching chat history:', error);
    }
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', message: input, timestamp: new Date().toISOString() };
    setMessages((prev) => [...prev, userMessage]);

    try {
      const res = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ message: input }),
      });

      if (res.ok) {
        const data = await res.json();
        const botMessage =
          typeof data.response === 'string'
            ? data.response
            : JSON.stringify(data.response); // Convert object to string if necessary
        setMessages((prev) => [
          ...prev,
          { role: 'bot', message: botMessage, timestamp: new Date().toISOString() },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          { role: 'bot', message: 'Sorry, something went wrong.', timestamp: new Date().toISOString() },
        ]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages((prev) => [
        ...prev,
        { role: 'bot', message: 'Unable to connect to the server.', timestamp: new Date().toISOString() },
      ]);
    }

    setInput('');
  };

  const handleKeyDown = (event) => {
    if (event.key === 'Enter') {
      sendMessage();
    }
  };

  // Auto-scroll to the bottom of the chat box whenever messages change
  useEffect(() => {
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  }, [messages]);

  useEffect(() => {
    fetchHistory();
  }, []);

  return (
    <div className="chat-page">
      <h2>Your Conversation</h2>
      <div className="chat-box" ref={chatBoxRef}>
        {messages.map((msg, i) => (
          <div key={i} className={`chat-bubble ${msg.role}`}>
            <p>{typeof msg.message === 'string' ? msg.message : JSON.stringify(msg.message)}</p>
            <span>{new Date(msg.timestamp).toLocaleTimeString()}</span>
          </div>
        ))}
      </div>
      <div className="chat-input">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message..."
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
}

export default Chat;

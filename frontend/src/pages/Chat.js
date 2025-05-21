import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import '../styles/chat.css';
import api from '../api';

function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [selectedUser, setSelectedUser] = useState(null);
  const [exporting, setExporting] = useState(false);
  const chatBoxRef = useRef(null);
  const { userId } = useParams();
  const { role } = useAuth();

  const fetchHistory = async () => {
    try {
      const endpoint = role === 'therapist' && userId 
        ? `/api/chat/history/${userId}`
        : '/api/chat/history';
      
      const response = await api.get(endpoint);
      setMessages(response.data);
      
      if (role === 'therapist' && userId) {
        // Fetch user details for therapist view
        const userResponse = await api.get(`/api/users/${userId}`);
        setSelectedUser(userResponse.data);
      }
    } catch (error) {
      console.error('Error fetching chat history:', error);
    }
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    try {
      // Add user message to UI immediately
      const userMessage = {
        role: 'user',
        content: input,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, userMessage]);
      setInput('');

      // Send message to server
      const endpoint = role === 'therapist' && userId 
        ? `/api/chat/${userId}`
        : '/api/chat';
      
      const response = await api.post(endpoint, { message: input });
      
      // Add bot response to UI
      const botMessage = {
        role: 'assistant',
        content: response.data.message,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.',
          timestamp: new Date().toISOString()
        }
      ]);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  const exportChat = async () => {
    try {
      setExporting(true);
      const endpoint = role === 'therapist' && userId 
        ? `/api/chat/export/${userId}`
        : '/api/chat/export';
      
      // Open the export URL in a new tab/window
      window.open(endpoint, '_blank');
    } catch (error) {
      console.error('Error exporting chat:', error);
    } finally {
      setExporting(false);
    }
  };

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  }, [messages]);

  // Fetch chat history on component mount or when userId changes
  useEffect(() => {
    fetchHistory();
  }, [userId]);

  return (
    <div className="chat-page">
      <div className="chat-header">
        <h2>
          {role === 'therapist' && selectedUser 
            ? `Chat with ${selectedUser.username}`
            : 'Your Conversation'
          }
        </h2>
        <button 
          className="export-button" 
          onClick={exportChat} 
          disabled={exporting || messages.length === 0}
          title="Export chat as HTML"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="7 10 12 15 17 10"></polyline>
            <line x1="12" y1="15" x2="12" y2="3"></line>
          </svg>
          {exporting ? 'Exporting...' : 'Share'}
        </button>
      </div>
      <div className="chat-box" ref={chatBoxRef}>
        {messages.map((msg, i) => (
          <div key={i} className={`chat-bubble ${msg.role}`}>
            <p>{msg.message || msg.content}</p>
            <span>{new Date(msg.timestamp).toLocaleTimeString()}</span>
          </div>
        ))}
      </div>
      <div className="chat-input">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message..."
          rows={2}
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
}

export default Chat;

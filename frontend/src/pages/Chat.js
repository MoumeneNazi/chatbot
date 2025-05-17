import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import '../styles/chat.css';
import api from '../api';

function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [selectedUser, setSelectedUser] = useState(null);
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
        content: response.data.response,
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
      <h2>
        {role === 'therapist' && selectedUser 
          ? `Chat with ${selectedUser.username}`
          : 'Your Conversation'
        }
      </h2>
      <div className="chat-box" ref={chatBoxRef}>
        {messages.map((msg, i) => (
          <div key={i} className={`chat-bubble ${msg.role}`}>
            <p>{msg.content}</p>
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

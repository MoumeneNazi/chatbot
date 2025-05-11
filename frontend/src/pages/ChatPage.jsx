import React, { useState } from 'react';

const ChatPage = () => {
  const [messages, setMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');

  const handleSend = () => {
    setMessages([...messages, { sender: 'user', text: currentMessage }]);
    setCurrentMessage('');
    // Simulate bot response
    setMessages((prev) => [...prev, { sender: 'bot', text: 'Thank you for sharing!' }]);
  };

  return (
    <div>
      <h2>Chat</h2>
      <div>
        {messages.map((msg, index) => (
          <div key={index} style={{ textAlign: msg.sender === 'user' ? 'right' : 'left' }}>
            <p>{msg.text}</p>
          </div>
        ))}
      </div>
      <input
        type="text"
        value={currentMessage}
        onChange={(e) => setCurrentMessage(e.target.value)}
      />
      <button onClick={handleSend}>Send</button>
    </div>
  );
};

export default ChatPage;
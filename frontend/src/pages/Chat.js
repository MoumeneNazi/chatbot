import React, { useState } from 'react';
import { post } from '../api';

function Chat() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);

  const sendMessage = async () => {
    if (!input) return;
    const userMessage = { role: 'user', message: input };
    setMessages([...messages, userMessage]);

    const res = await post('/chat', { message: input });
    setMessages(prev => [...prev, { role: 'bot', message: res.response }]);
    setInput('');
  };

  return (
    <div className="chat-box">
      <h2>Therapeutic Chat</h2>
      <div className="chat-window">
        {messages.map((m, i) => (
          <div key={i} className={`msg ${m.role}`}>
            <strong>{m.role === 'user' ? 'You' : 'Bot'}:</strong> {m.message}
          </div>
        ))}
      </div>
      <input value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && sendMessage()} />
      <button onClick={sendMessage}>Send</button>
    </div>
  );
}

export default Chat;

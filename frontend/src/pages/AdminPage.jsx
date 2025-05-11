import React, { useState } from 'react';

const AdminPage = () => {
  const [chats, setChats] = useState([
    { id: 1, user: 'JohnDoe', messages: ['Hello', 'How are you?'] },
    { id: 2, user: 'JaneDoe', messages: ['I need help', 'Feeling stressed'] },
  ]);

  return (
    <div>
      <h2>Admin Dashboard</h2>
      {chats.map((chat) => (
        <div key={chat.id}>
          <h3>Chat with {chat.user}</h3>
          {chat.messages.map((msg, index) => (
            <p key={index}>{msg}</p>
          ))}
          <hr />
        </div>
      ))}
    </div>
  );
};

export default AdminPage;
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/admin.css';

function AdminDashboard() {
  const [users, setUsers] = useState([]);
  const [error, setError] = useState('');
  const token = localStorage.getItem('token');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const res = await fetch('http://localhost:8000/admin/users', {
          headers: { Authorization: `Bearer ${token}` }
        });
        const data = await res.json();
        if (res.ok) {
          setUsers(data);
        } else {
          setError(data.detail || 'Access denied');
        }
      } catch {
        setError('Server error');
      }
    };
    fetchUsers();
  }, [token]);

  const promoteUser = async (username) => {
    try {
      const res = await fetch(`http://localhost:8000/admin/promote/${username}`, {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      const data = await res.json();
      if (res.ok) {
        alert(data.msg);
        // Refresh user list
        setUsers(prev =>
          prev.map(u =>
            u.username === username ? { ...u, role: 'therapist' } : u
          )
        );
      } else {
        alert(data.detail || 'Failed to promote');
      }
    } catch {
      alert('Server error');
    }
  };
  



  const viewJournal = (username) => navigate(`/therapist?username=${username}`);
  const viewChat = (username) => navigate(`/therapist/chat/${username}`);

  return (
    <div className="admin-dashboard">
      <h2>Therapist Dashboard</h2>
      {error && <p className="error">{error}</p>}
      <div className="user-list">
        {users.map((u, i) => (
          <div key={i} className="user-card">
            <h4>{u.username}</h4>
            <p>Role: {u.role}</p>
            <button onClick={() => viewJournal(u.username)}>View Journal</button>
            <button onClick={() => viewChat(u.username)}>View Chat</button>
            {u.role !== "therapist" && (
            <button onClick={() => promoteUser(u.username)}>Promote</button>
          )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default AdminDashboard;

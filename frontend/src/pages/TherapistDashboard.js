import React, { useEffect, useState } from "react";
import axios from "../api";
import "../styles/therapistDashboard.css";

const TherapistDashboard = () => {
  const [users, setUsers] = useState([]);
  const [statusMsg, setStatusMsg] = useState("");

  const token = localStorage.getItem("token");

  useEffect(() => {
    axios
      .get("/admin/users", {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then((res) => {
        setUsers(res.data);
      })
      .catch((err) => {
        console.error("Error fetching users", err);
      });
  }, [token]);

  const promoteUser = (username) => {
    axios
      .put(`/admin/promote/${username}`, {}, {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then((res) => {
        setStatusMsg(res.data.msg);
        setUsers((prev) =>
          prev.map((u) =>
            u.username === username ? { ...u, role: "therapist" } : u
          )
        );
      })
      .catch((err) => {
        setStatusMsg("Failed to promote user.");
        console.error("Promotion failed", err);
      });
  };

  return (
    <div className="therapist-dashboard">
      <h2>🩺 Therapist Admin Dashboard</h2>
      {statusMsg && <div className="status-msg">{statusMsg}</div>}

      <table>
        <thead>
          <tr>
            <th>Username</th>
            <th>Role</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.username}>
              <td>{u.username}</td>
              <td>{u.role}</td>
              <td>
                {u.role !== "therapist" && (
                  <button onClick={() => promoteUser(u.username)}>Promote</button>
                )}
                <a
                  href={`/therapist/journal?user=${u.username}`}
                  target="_blank"
                  rel="noreferrer"
                >
                  View Journal
                </a>{" "}
                |{" "}
                <a
                  href={`/therapist/chat?user=${u.username}`}
                  target="_blank"
                  rel="noreferrer"
                >
                  View Chat
                </a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default TherapistDashboard;

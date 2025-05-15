import React, { useEffect, useState } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import UserDashboard from "./pages/UserDashboard";
import TherapistDashboard from "./pages/TherapistDashboard";
import Progress from "./pages/Progress";
import Journal from "./pages/Journal";
import Home from "./pages/Home";
import Navbar from "./components/Navbar";
import Chat from "./pages/Chat";

const App = () => {
  const [role, setRole] = useState(localStorage.getItem("role"));

  useEffect(() => {
    const storedRole = localStorage.getItem("role");
    setRole(storedRole);
  }, [localStorage.getItem("role")]);

  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* User Routes */}
        <Route
          path="/user/dashboard"
          element={role === "user" ? <UserDashboard /> : <Navigate to="/login" />}
        />
        <Route
          path="/chat"
          element={role === "user" ? <Chat /> : <Navigate to="/login" />}
        />

        {/* Therapist Routes */}
        <Route
          path="/therapist/dashboard"
          element={role === "therapist" ? <TherapistDashboard /> : <Navigate to="/login" />}
        />
        <Route
          path="/therapist/progress"
          element={role === "therapist" ? <Progress /> : <Navigate to="/login" />}
        />
        <Route
          path="/therapist/journal"
          element={role === "therapist" ? <Journal /> : <Navigate to="/login" />}
        />

        {/* Catch all unknown paths */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Router>
  );
};

export default App;

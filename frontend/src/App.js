import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Home from "./pages/Home";
import Chat from "./pages/Chat";
import Journal from "./pages/Journal";
import Progress from "./pages/Progress";
import TherapistDashboard from "./pages/TherapistDashboard";
import AdminDashboard from "./pages/AdminDashboard";
import About from "./pages/About";
import Contact from "./pages/Contact"; // previously 'Conatct'
import UserDashboard from "./pages/UserDashboard";     
import ProgressPage from "./pages/Progress";           
import JournalPage from "./pages/Journal";             



const App = () => {
  const userRole = localStorage.getItem("role");

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />

        {/* User Dashboard */}
        <Route
          path="/user/dashboard"
          element={
            userRole === "user" ? <UserDashboard /> : <Navigate to="/login" />
          }
        />

        {/* Therapist Dashboard */}
        <Route
          path="/therapist/dashboard"
          element={
            userRole === "therapist" ? <TherapistDashboard /> : <Navigate to="/login" />
          }
        />
        <Route
          path="/therapist/progress"
          element={
            userRole === "therapist" ? <ProgressPage /> : <Navigate to="/login" />
          }
        />
        <Route
          path="/therapist/journal"
          element={
            userRole === "therapist" ? <JournalPage /> : <Navigate to="/login" />
          }
        />

        {/* Redirect unknown paths to login */}
        <Route path="*" element={<Navigate to="/login" />} />
      </Routes>
    </Router>
  );
};

export default App;

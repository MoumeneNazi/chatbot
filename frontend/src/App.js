import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import TherapistDashboard from "./pages/TherapistDashboard";
import Chat from "./pages/Chat";
import Progress from "./pages/Progress";
import Journal from "./pages/Journal";
import Review from "./pages/Review";
import AddReview from "./pages/AddReview";
import Therapist from "./pages/Therapist";
import TherapistChat from "./pages/TherapistChat";
import TherapistJournal from "./pages/TherapistJournal";
import TherapistApplication from "./pages/TherapistApplication";

const ProtectedRoute = ({ children, roles }) => {
  const { token, hasPermission } = useAuth();
  
  // Check if user is authenticated
  if (!token) {
    return <Navigate to="/login" />;
  }
  
  // Check if user has required role permissions
  if (roles && !roles.some(role => hasPermission(role))) {
    return <Navigate to="/" />;
  }
  
  return children;
};

const AppRoutes = () => (
  <Routes>
    {/* Public Routes */}
    <Route path="/" element={<Home />} />
    <Route path="/login" element={<Login />} />
    <Route path="/register" element={<Register />} />

    {/* User Routes */}
    <Route
      path="/chat"
      element={
        <ProtectedRoute roles={["user"]}>
          <Chat />
        </ProtectedRoute>
      }
    />
    <Route
      path="/journal"
      element={
        <ProtectedRoute roles={["user"]}>
          <Journal />
        </ProtectedRoute>
      }
    />
    <Route
      path="/progress"
      element={
        <ProtectedRoute roles={["user"]}>
          <Progress />
        </ProtectedRoute>
      }
    />
    <Route
      path="/review"
      element={
        <ProtectedRoute roles={["user", "therapist"]}>
          <Review />
        </ProtectedRoute>
      }
    />
    <Route
      path="/reviews/add"
      element={
        <ProtectedRoute roles={["therapist"]}>
          <AddReview />
        </ProtectedRoute>
      }
    />
    <Route
      path="/apply-therapist"
      element={
        <ProtectedRoute roles={["user"]}>
          <TherapistApplication />
        </ProtectedRoute>
      }
    />

    {/* Therapist Routes */}
    <Route
      path="/therapist/dashboard"
      element={
        <ProtectedRoute roles={["therapist"]}>
          <TherapistDashboard />
        </ProtectedRoute>
      }
    />
    <Route
      path="/therapist/chat/:username"
      element={
        <ProtectedRoute roles={["therapist"]}>
          <TherapistChat />
        </ProtectedRoute>
      }
    />
    <Route
      path="/therapist/journal/:username"
      element={
        <ProtectedRoute roles={["therapist"]}>
          <TherapistJournal />
        </ProtectedRoute>
      }
    />
    <Route
      path="/therapist"
      element={
        <ProtectedRoute roles={["therapist"]}>
          <Therapist />
        </ProtectedRoute>
      }
    />

    {/* Fallback Route */}
    <Route path="*" element={<Navigate to="/" />} />
  </Routes>
);

const App = () => (
  <AuthProvider>
    <Router>
      <Navbar />
      <AppRoutes />
    </Router>
  </AuthProvider>
);

export default App;
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

const ProtectedRoute = ({ children, roles }) => {
  const { role, token } = useAuth();
  if (!token || (roles && !roles.includes(role))) return <Navigate to="/login" />;
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
      path="/reviews"
      element={
        <ProtectedRoute roles={["user", "therapist"]}>
          <Review />
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
      path="/therapist/reviews/add"
      element={
        <ProtectedRoute roles={["therapist"]}>
          <AddReview />
        </ProtectedRoute>
      }
    />
    <Route
      path="/therapist/chat/:userId"
      element={
        <ProtectedRoute roles={["therapist"]}>
          <Chat />
        </ProtectedRoute>
      }
    />
    <Route
      path="/therapist/user/:userId"
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
import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import AdminDashboard from "./pages/AdminDashboard";
import Chat from "./pages/Chat";
import UserDashboard from "./pages/UserDashboard";
import Progress from "./pages/Progress";
import Journal from "./pages/Journal";

const ProtectedRoute = ({ children, roles }) => {
  const { role, token } = useAuth();
  if (!token || (roles && !roles.includes(role))) return <Navigate to="/login" />;
  return children;
};

const AppRoutes = () => (
  <Routes>
    <Route path="/" element={<Home />} />
    <Route path="/login" element={<Login />} />
    <Route path="/register" element={<Register />} />
    <Route
      path="/chat"
      element={
        <ProtectedRoute roles={["user"]}>
          <Chat />
        </ProtectedRoute>
      }
    />
    <Route
      path="/user/dashboard"
      element={
        <ProtectedRoute roles={["user"]}>
          <UserDashboard />
        </ProtectedRoute>
      }
    />
    <Route
      path="/admin/dashboard"
      element={
        <ProtectedRoute roles={["therapist"]}>
          <AdminDashboard />
        </ProtectedRoute>
      }
    />
    <Route
      path="/progress"
      element={
        <ProtectedRoute roles={["therapist"]}>
          <Progress />
        </ProtectedRoute>
      }
    />
    <Route
      path="/journal"
      element={
        <ProtectedRoute roles={["therapist"]}>
          <Journal />
        </ProtectedRoute>
      }
    />
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
import React, { createContext, useContext, useState, useEffect } from "react";

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("token"));
  const [role, setRole] = useState(() => localStorage.getItem("role"));
  const [username, setUsername] = useState(() => localStorage.getItem("username"));

  // Handle token storage
  useEffect(() => {
    if (token) {
      localStorage.setItem("token", token);
    } else {
      localStorage.removeItem("token");
    }
  }, [token]);

  // Handle role storage
  useEffect(() => {
    if (role) {
      localStorage.setItem("role", role);
    } else {
      localStorage.removeItem("role");
    }
  }, [role]);

  // Handle username storage
  useEffect(() => {
    if (username) {
      localStorage.setItem("username", username);
    } else {
      localStorage.removeItem("username");
    }
  }, [username]);

  const login = (newToken, userRole, userName) => {
    setToken(newToken);
    setRole(userRole);
    setUsername(userName);
  };

  const logout = () => {
    setToken(null);
    setRole(null);
    setUsername(null);
    localStorage.clear();
  };

  const hasPermission = (requiredRole) => {
    const roleHierarchy = {
      admin: ["admin", "therapist", "user"],
      therapist: ["therapist", "user"],
      user: ["user"]
    };

    if (!role || !roleHierarchy[role]) {
      return false;
    }

    return roleHierarchy[role].includes(requiredRole);
  };

  return (
    <AuthContext.Provider value={{ 
      token,
      role, 
      username,
      login, 
      logout,
      hasPermission,
      isAuthenticated: !!token,
      isAdmin: role === "admin",
      isTherapist: role === "therapist",
      isUser: role === "user"
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
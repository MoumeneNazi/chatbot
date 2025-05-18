import axios from "axios";

// Create axios instance with base URL
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || "http://localhost:8000", // FastAPI server URL
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // If error is 401, redirect to login
    if (error.response?.status === 401) {
      localStorage.clear();
      window.location.href = "/login";
    }
    
    // Handle validation errors
    if (error.response?.data?.detail) {
      // Normalize validation errors to strings
      if (typeof error.response.data.detail === 'object') {
        try {
          // If it's a validation error object with standard FastAPI format
          const validationObj = error.response.data.detail;
          if (validationObj.type && validationObj.msg) {
            error.response.data.detail = validationObj.msg;
          } else if (Array.isArray(validationObj)) {
            // If it's an array of validation errors
            error.response.data.detail = validationObj
              .map(err => err.msg || JSON.stringify(err))
              .join(', ');
          } else {
            // Generic fallback for other object formats
            error.response.data.detail = JSON.stringify(validationObj);
          }
        } catch (e) {
          // If JSON stringify fails, set a generic error
          error.response.data.detail = "An error occurred with the request";
          console.error("Error processing validation error:", e);
        }
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;
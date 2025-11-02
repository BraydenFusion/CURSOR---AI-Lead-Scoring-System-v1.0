import axios from "axios";

// Use environment variable, fallback to local
// Railway will set VITE_API_URL or use VITE_API_BASE_URL
const API_BASE_URL = 
  import.meta.env.VITE_API_URL || 
  import.meta.env.VITE_API_BASE_URL || 
  'http://localhost:8000/api';

console.log('API Base URL:', API_BASE_URL);

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10_000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to all requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default apiClient;

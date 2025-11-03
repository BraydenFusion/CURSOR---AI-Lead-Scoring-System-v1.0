import axios from "axios";
import { getApiConfig, initializeApiConfig } from "../config";

// Initialize API config asynchronously
initializeApiConfig().catch(console.error);

const API_BASE_URL = getApiConfig().baseUrl;

console.log('API Base URL:', API_BASE_URL);
console.log('VITE_API_URL env var (raw):', import.meta.env.VITE_API_URL);

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30_000, // 30 seconds - increased for slower connections
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to all requests
apiClient.interceptors.request.use(
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

// Enhanced error handling with retry logic
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Handle 401 errors - unauthorized
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/login";
      return Promise.reject(error);
    }

    // Handle network errors and timeouts with retry
    if (
      (!error.response || error.code === 'ECONNABORTED') &&
      !originalRequest._retry
    ) {
      originalRequest._retry = true;

      // Retry for network errors (max 2 retries)
      if (originalRequest._retryCount < 2) {
        originalRequest._retryCount = (originalRequest._retryCount || 0) + 1;
        
        // Exponential backoff: wait 1s, 2s
        const delay = Math.pow(2, originalRequest._retryCount - 1) * 1000;
        
        await new Promise(resolve => setTimeout(resolve, delay));
        return apiClient(originalRequest);
      }
    }

    // Handle 500 errors - server errors
    if (error.response?.status === 500) {
      console.error("Server error:", error.response.data);
      // Show user-friendly message
      error.userMessage = "The server encountered an error. Please try again later.";
    }

    // Handle 503 errors - service unavailable
    if (error.response?.status === 503) {
      error.userMessage = "Service is temporarily unavailable. Please try again in a moment.";
    }

    // Handle timeout errors
    if (error.code === 'ECONNABORTED') {
      error.userMessage = "Request timed out. Please check your connection and try again.";
    }

    return Promise.reject(error);
  }
);

export default apiClient;

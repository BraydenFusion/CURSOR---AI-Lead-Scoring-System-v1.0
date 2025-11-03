import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useNavigate } from "react-router-dom";

interface User {
  id: string;
  email: string;
  username: string;
  full_name: string;
  role: "admin" | "manager" | "sales_rep";
  is_active: boolean;
}

interface RegisterData {
  email: string;
  username: string;
  full_name: string;
  password: string;
}

interface AuthContextType {
  user: User | null;
  login: (username: string, password: string) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

import { getApiConfig } from "../config";

const API_BASE_URL = getApiConfig().baseUrl;

// Log API URL on module load for debugging
console.log("🔗 AuthContext API Base URL:", API_BASE_URL);
console.log("🔗 VITE_API_URL env var (raw):", import.meta.env.VITE_API_URL);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    // Check for stored token on mount
    const token = localStorage.getItem("token");
    if (token) {
      fetchCurrentUser(token);
    } else {
      setIsLoading(false);
    }
  }, []);

  const fetchCurrentUser = async (token: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      } else {
        localStorage.removeItem("token");
      }
    } catch (error) {
      console.error("Failed to fetch user:", error);
      localStorage.removeItem("token");
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (username: string, password: string) => {
    const formData = new FormData();
    formData.append("username", username);
    formData.append("password", password);

    try {
      console.log("Attempting login to:", `${API_BASE_URL}/auth/login`);
      
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        body: formData,
      });

      console.log("Login response status:", response.status);
      console.log("Login response headers:", response.headers.get("content-type"));

      if (!response.ok) {
        // Try to parse JSON, but handle non-JSON responses gracefully
        let errorMessage = "Login failed";
        const contentType = response.headers.get("content-type");
        
        if (contentType && contentType.includes("application/json")) {
          try {
            const error = await response.json();
            errorMessage = error.detail || error.message || "Login failed";
          } catch (e) {
            console.error("Failed to parse error JSON:", e);
            const text = await response.text();
            errorMessage = text || `HTTP ${response.status}: ${response.statusText}`;
          }
        } else {
          // Response is not JSON (likely HTML error page or CORS error)
          const text = await response.text();
          console.error("Non-JSON error response:", text);
          
          if (response.status === 0) {
            errorMessage = `Cannot connect to backend at ${API_BASE_URL}. This is likely a CORS issue. Check Railway backend CORS configuration.`;
          } else if (response.status === 404) {
            errorMessage = `Backend endpoint not found (404). The login route may not be registered. Check Railway backend deploy logs.`;
          } else if (response.status === 403) {
            errorMessage = "Access forbidden. Please check CORS configuration on backend.";
          } else {
            errorMessage = `Server error (${response.status}): ${response.statusText}`;
          }
        }
        
        throw new Error(errorMessage);
      }

      // Check if response is actually JSON before parsing
      const contentType = response.headers.get("content-type");
      if (!contentType || !contentType.includes("application/json")) {
        const text = await response.text();
        console.error("Expected JSON but got:", contentType, text);
        throw new Error("Server returned invalid response. Please check backend configuration.");
      }

      const data = await response.json();
      
      if (!data.access_token) {
        throw new Error("Invalid response from server: missing access token");
      }
      
      localStorage.setItem("token", data.access_token);
      setUser(data.user);
      navigate("/dashboard");
    } catch (error) {
      console.error("Login error:", error);
      
      // Re-throw with better message if it's a network error
      if (error instanceof TypeError && error.message.includes("fetch")) {
        const apiUrl = API_BASE_URL;
        throw new Error(
          `Network error: Cannot connect to backend at ${apiUrl}. ` +
          `This could be a CORS issue or the backend may be down. ` +
          `Check Railway deploy logs for backend service.`
        );
      }
      
      throw error;
    }
  };

  const register = async (data: RegisterData) => {
    try {
      console.log("Attempting registration to:", `${API_BASE_URL}/auth/register`);
      
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: data.email,
          username: data.username,
          full_name: data.full_name,
          password: data.password,
          role: "sales_rep", // Default role for new users
        }),
      });

      console.log("Registration response status:", response.status);

      if (!response.ok) {
        let errorMessage = "Registration failed";
        const contentType = response.headers.get("content-type");
        
        if (contentType && contentType.includes("application/json")) {
          try {
            const error = await response.json();
            errorMessage = error.detail || error.message || "Registration failed";
          } catch (e) {
            console.error("Failed to parse error JSON:", e);
            const text = await response.text();
            errorMessage = text || `HTTP ${response.status}: ${response.statusText}`;
          }
        } else {
          const text = await response.text();
          console.error("Non-JSON error response:", text);
          
          if (response.status === 0 || response.status === 404) {
            errorMessage = `Cannot connect to server at ${API_BASE_URL}. Check that the backend is running and Railway deploy logs.`;
          } else {
            errorMessage = `Server error (${response.status}): ${response.statusText}`;
          }
        }
        
        throw new Error(errorMessage);
      }

      // Check if response is actually JSON before parsing
      const contentType = response.headers.get("content-type");
      if (!contentType || !contentType.includes("application/json")) {
        const text = await response.text();
        console.error("Expected JSON but got:", contentType, text);
        throw new Error("Server returned invalid response. Please check backend configuration.");
      }

      const userData = await response.json();
      
      // After successful registration, automatically log the user in
      // We'll use the same credentials to login
      await login(data.username, data.password);
    } catch (error) {
      console.error("Registration error:", error);
      
      // Re-throw with better message if it's a network error
      if (error instanceof TypeError && error.message.includes("fetch")) {
        const apiUrl = API_BASE_URL;
        throw new Error(
          `Network error: Cannot connect to backend at ${apiUrl}. ` +
          `This could be a CORS issue or the backend may be down. ` +
          `Check Railway deploy logs for backend service.`
        );
      }
      
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    setUser(null);
    navigate("/login");
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        login,
        register,
        logout,
        isAuthenticated: !!user,
        isLoading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}


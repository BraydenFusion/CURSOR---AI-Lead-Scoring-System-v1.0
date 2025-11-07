import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useNavigate } from "react-router-dom";

interface User {
  id: string;
  email: string;
  username: string;
  full_name: string;
  role: "admin" | "manager" | "sales_rep";
  is_active: boolean;
  company_name?: string | null;
  company_role?: string | null;
  payment_plan?: string | null;
  onboarding_completed?: boolean;
  profile_picture_url?: string | null;
}

interface RegisterData {
  email: string;
  username: string;
  full_name: string;
  password: string;
  company_role?: string;
}

interface AuthContextType {
  user: User | null;
  login: (username: string, password: string) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  googleSignIn: () => Promise<void>;
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

  // Handle Firebase redirect result FIRST (before checking stored token)
  useEffect(() => {
    const handleFirebaseRedirect = async () => {
      try {
        const firebase = (window as any).firebase;
        if (!firebase) {
          console.log("⚠️  Firebase not loaded yet, checking for stored token...");
          // Firebase not loaded yet, check for stored token instead
          const token = localStorage.getItem("token");
          if (token) {
            await fetchCurrentUser(token);
          } else {
            setIsLoading(false);
          }
          return;
        }
        
        const auth = firebase.auth();
        
        // Check if we're returning from a redirect
        console.log("🔍 Checking for Firebase redirect result...");
        const result = await auth.getRedirectResult();
        
        if (result.user) {
          console.log("✅ Google Sign-In redirect successful, user:", result.user.email);
          setIsLoading(true);
          
          try {
            // User successfully signed in via redirect
            const idToken = await result.user.getIdToken();
            console.log("✅ Got ID token from Firebase");
            
            // Send ID token to backend
            console.log("📤 Sending ID token to backend...");
            const response = await fetch(`${API_BASE_URL}/auth/google`, {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              mode: 'cors',
              credentials: 'include',
              body: JSON.stringify({
                id_token: idToken,
              }),
            });
            
            if (!response.ok) {
              const error = await response.json().catch(() => ({ detail: "Google authentication failed" }));
              throw new Error(error.detail || "Google authentication failed");
            }
            
            const data = await response.json();
            console.log("✅ Backend authentication successful, user role:", data.user?.role);
            
            if (!data.access_token) {
              throw new Error("Invalid response from server: missing access token");
            }
            
            // Store token and user info
            localStorage.setItem("token", data.access_token);
            setUser(data.user);
            console.log("✅ User state updated, onboarding_completed:", data.user?.onboarding_completed);
            
            // Small delay to ensure state is updated before navigation
            await new Promise(resolve => setTimeout(resolve, 100));
            
            // Check if user needs onboarding (new Google sign-up)
            if (!data.user.onboarding_completed) {
              console.log("📝 User needs onboarding, redirecting to /onboarding");
              navigate("/onboarding", { replace: true });
              setIsLoading(false);
              return;
            }
            
            // Redirect to appropriate dashboard based on role
            const returnUrl = sessionStorage.getItem('googleSignInReturnUrl');
            if (returnUrl && returnUrl !== window.location.pathname) {
              console.log("🔙 Redirecting to return URL:", returnUrl);
              sessionStorage.removeItem('googleSignInReturnUrl');
              navigate(returnUrl, { replace: true });
            } else {
              // Redirect based on role
              let dashboardPath = "/dashboard";
              if (data.user.role === "sales_rep") {
                dashboardPath = "/dashboard/sales-rep";
              } else if (data.user.role === "manager") {
                dashboardPath = "/dashboard/manager";
              } else if (data.user.role === "admin") {
                dashboardPath = "/dashboard/owner";
              }
              console.log("🎯 Redirecting to dashboard:", dashboardPath);
              navigate(dashboardPath, { replace: true });
            }
            
            setIsLoading(false);
            return; // Don't check for stored token if we just authenticated
          } catch (authError: any) {
            console.error("❌ Error during Google authentication:", authError);
            setIsLoading(false);
            // Don't throw - fall through to check for stored token
            // This allows the user to try again or use regular login
          }
        } else {
          console.log("ℹ️  No Firebase redirect result found");
        }
      } catch (error: any) {
        console.error("❌ Firebase redirect handling error:", error);
        // Clear any stored return URL on error
        sessionStorage.removeItem('googleSignInReturnUrl');
        // Don't set loading to false here - let it fall through to check token
      }
      
      // If no redirect result or error occurred, check for stored token
      const token = localStorage.getItem("token");
      if (token) {
        console.log("🔑 Found stored token, fetching user...");
        await fetchCurrentUser(token);
      } else {
        console.log("ℹ️  No stored token, user not authenticated");
        setIsLoading(false);
      }
    };
    
    handleFirebaseRedirect();
  }, [navigate]);

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
        
        // Redirect to onboarding if not completed (but not if already on onboarding page or auth pages)
        const currentPath = window.location.pathname;
        if (!userData.onboarding_completed && 
            currentPath !== "/onboarding" && 
            currentPath !== "/login" && 
            currentPath !== "/register" &&
            !currentPath.startsWith("/reset-password")) {
          navigate("/onboarding");
        }
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

  // Helper to test backend connectivity before making requests
  const testBackendConnection = async (): Promise<{connected: boolean, error?: string}> => {
    try {
      // Test health endpoint (simpler, no auth required)
      const healthUrl = API_BASE_URL.replace('/api', '/health.json');
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
      
      try {
        const healthResponse = await fetch(healthUrl, {
          method: 'GET',
          mode: 'cors',
          signal: controller.signal,
        });
        
        clearTimeout(timeoutId);
        
        if (healthResponse.ok || healthResponse.status < 500) {
          return { connected: true };
        }
        return { connected: false, error: `Health check returned ${healthResponse.status}` };
      } finally {
        clearTimeout(timeoutId);
      }
    } catch (error: any) {
      console.error("Backend health check failed:", error);
      
      // Determine specific error type
      if (error.name === 'AbortError' || error.message?.includes('timeout')) {
        return { connected: false, error: 'Backend request timed out. The backend may be slow or down.' };
      } else if (error.message?.includes('Failed to fetch') || error.message?.includes('NetworkError')) {
        return { connected: false, error: 'Cannot connect to backend. The backend may be down or unreachable.' };
      } else if (error.message?.includes('CORS')) {
        return { connected: false, error: 'CORS error: Backend is blocking requests from this origin.' };
      }
      return { connected: false, error: error.message || 'Unknown connection error' };
    }
  };

  const login = async (username: string, password: string) => {
    const formData = new FormData();
    formData.append("username", username);
    formData.append("password", password);

    try {
      console.log("Attempting login to:", `${API_BASE_URL}/auth/login`);
      
      // First, test backend connectivity
      const connectionTest = await testBackendConnection();
      if (!connectionTest.connected) {
        throw new Error(
          `Cannot connect to backend at ${API_BASE_URL.replace('/api', '')}. ${connectionTest.error || 'The backend may be down or unreachable.'} ` +
          `Please check Railway deploy logs for the backend service.`
        );
      }
      
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        body: formData,
        mode: 'cors',
        credentials: 'include',
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
      
      // First, test backend connectivity
      const connectionTest = await testBackendConnection();
      if (!connectionTest.connected) {
        throw new Error(
          `Cannot connect to backend at ${API_BASE_URL.replace('/api', '')}. ${connectionTest.error || 'The backend may be down or unreachable.'} ` +
          `Please check Railway deploy logs for the backend service.`
        );
      }
      
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        mode: 'cors',
        credentials: 'include',
        body: JSON.stringify({
          email: data.email,
          username: data.username,
          full_name: data.full_name,
          password: data.password,
          role: "sales_rep", // Default role for new users
          company_role: data.company_role || null,
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

  const googleSignIn = async () => {
    setIsLoading(true);
    
    try {
      // Check if Firebase is available
      if (typeof window === 'undefined' || !(window as any).firebase) {
        throw new Error("Firebase is not loaded. Please refresh the page.");
      }
      
      const firebase = (window as any).firebase;
      const auth = firebase.auth();
      const provider = new firebase.auth.GoogleAuthProvider();
      
      // Use redirect flow instead of popup to avoid domain authorization issues
      // Store the current URL so we can redirect back after authentication
      const currentUrl = window.location.href;
      sessionStorage.setItem('googleSignInReturnUrl', currentUrl);
      
      // Use redirect instead of popup
      await auth.signInWithRedirect(provider);
      
      // Note: The redirect will happen, so this code won't execute until after redirect
      // We'll handle the result in a useEffect that checks for redirect result
    } catch (error: any) {
      console.error("Google Sign-In error:", error);
      setIsLoading(false);
      
      // Provide helpful error message
      let errorMessage = "Google Sign-In failed";
      
      if (error.code === 'auth/unauthorized-domain') {
        errorMessage = `This domain (${window.location.hostname}) is not authorized for Firebase. Please add it to Firebase Console → Authentication → Settings → Authorized domains.`;
      } else if (error.code === 'auth/operation-not-allowed') {
        errorMessage = "Google Sign-In is not enabled. Please enable it in Firebase Console → Authentication → Sign-in method.";
      } else if (error.message?.includes('redirect_uri_mismatch') || error.message?.includes('invalid request')) {
        errorMessage = `OAuth redirect URI mismatch. Add these redirect URIs to Google Cloud Console → APIs & Services → Credentials → OAuth 2.0 Client ID → Authorized redirect URIs:\n\n1. https://ventrix-477422.firebaseapp.com/__/auth/handler\n2. https://ventrix-477422.web.app/__/auth/handler\n3. ${window.location.origin}/__/auth/handler\n\nSee GOOGLE_OAUTH_FIX.md for detailed instructions.`;
      } else if (error.message?.includes('not authorized')) {
        errorMessage = `Domain authorization error: ${window.location.hostname} needs to be added to Firebase authorized domains. Go to Firebase Console → Authentication → Settings → Authorized domains and add your domain.`;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      throw new Error(errorMessage);
    }
  };


  const logout = () => {
    // Sign out from Firebase if signed in
    if (typeof window !== 'undefined' && (window as any).firebase) {
      (window as any).firebase.auth().signOut().catch(() => {
        // Ignore errors
      });
    }
    
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
        googleSignIn,
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


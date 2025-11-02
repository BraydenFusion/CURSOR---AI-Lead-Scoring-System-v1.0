import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider } from "./contexts/AuthContext";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { NavBar } from "./components/NavBar";
import { LoginPage } from "./pages/LoginPage";
import { ForgotPasswordPage } from "./pages/ForgotPasswordPage";
import { ResetPasswordPage } from "./pages/ResetPasswordPage";
import { LeadDashboard } from "./components/LeadDashboard";
import { MyLeadsPage } from "./pages/MyLeadsPage";
import { LeadDetailPage } from "./pages/LeadDetailPage";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <AuthProvider>
            <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/forgot-password" element={<ForgotPasswordPage />} />
            <Route path="/reset-password" element={<ResetPasswordPage />} />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <div className="min-h-screen bg-slate-50 text-slate-900">
                    <NavBar />
                    <main className="mx-auto max-w-6xl px-6 py-8">
                      <LeadDashboard />
                    </main>
                  </div>
                </ProtectedRoute>
              }
            />
            <Route
              path="/my-leads"
              element={
                <ProtectedRoute allowedRoles={["sales_rep", "manager", "admin"]}>
                  <MyLeadsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/leads/:leadId"
              element={
                <ProtectedRoute>
                  <LeadDetailPage />
                </ProtectedRoute>
              }
            />
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;

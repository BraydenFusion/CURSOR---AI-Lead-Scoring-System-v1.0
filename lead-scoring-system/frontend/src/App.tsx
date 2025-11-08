import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import { ForgotPasswordPage } from "./pages/ForgotPasswordPage";
import { ResetPasswordPage } from "./pages/ResetPasswordPage";
import { MyLeadsPage } from "./pages/MyLeadsPage";
import { LeadDetailPage } from "./pages/LeadDetailPage";
import { SalesRepDashboard } from "./pages/SalesRepDashboard";
import { ManagerDashboard } from "./pages/ManagerDashboard";
import { OwnerDashboard } from "./pages/OwnerDashboard";
import { HomePage } from "./pages/HomePage";
import { PricingPage } from "./pages/PricingPage";
import { FeaturesPage } from "./pages/FeaturesPage";
import { TermsOfServicePage } from "./pages/TermsOfServicePage";
import { PrivacyPolicyPage } from "./pages/PrivacyPolicyPage";
import { SettingsPage } from "./pages/SettingsPage";
import { OnboardingPage } from "./pages/OnboardingPage";
import { LegacyDashboardPage } from "./pages/LegacyDashboardPage";
import { AnalyticsDashboard } from "./pages/AnalyticsDashboard";
import { ReportBuilder } from "./pages/ReportBuilder";
import { AssignmentRules } from "./pages/AssignmentRules";

// Role-based dashboard redirect component
function DashboardRedirect() {
  const { user } = useAuth();
  
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  
  // Redirect based on role
  if (user.role === "sales_rep") {
    return <Navigate to="/dashboard/sales-rep" replace />;
  } else if (user.role === "manager") {
    return <Navigate to="/dashboard/manager" replace />;
  } else if (user.role === "admin") {
    return <Navigate to="/dashboard/owner" replace />;
  }
  
  // Fallback to old dashboard
  return <Navigate to="/dashboard/legacy" replace />;
}

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
            <Route path="/" element={<HomePage />} />
            <Route path="/features" element={<FeaturesPage />} />
            <Route path="/pricing" element={<PricingPage />} />
            <Route path="/terms" element={<TermsOfServicePage />} />
            <Route path="/privacy" element={<PrivacyPolicyPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/forgot-password" element={<ForgotPasswordPage />} />
            <Route path="/reset-password" element={<ResetPasswordPage />} />
            <Route
              path="/onboarding"
              element={
                <ProtectedRoute>
                  <OnboardingPage />
                </ProtectedRoute>
              }
            />
              <Route
                path="/dashboard/analytics"
                element={
                  <ProtectedRoute allowedRoles={["admin", "manager"]}>
                    <AnalyticsDashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/dashboard/reports"
                element={
                  <ProtectedRoute allowedRoles={["admin", "manager"]}>
                    <ReportBuilder />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/assignment-rules"
                element={
                  <ProtectedRoute allowedRoles={["admin", "manager"]}>
                    <AssignmentRules />
                  </ProtectedRoute>
                }
              />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <DashboardRedirect />
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/sales-rep"
              element={
                <ProtectedRoute allowedRoles={["sales_rep"]}>
                  <SalesRepDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/manager"
              element={
                <ProtectedRoute allowedRoles={["manager", "admin"]}>
                  <ManagerDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/owner"
              element={
                <ProtectedRoute allowedRoles={["admin"]}>
                  <OwnerDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/settings"
              element={
                <ProtectedRoute>
                  <SettingsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/legacy"
              element={
                <ProtectedRoute>
                  <LegacyDashboardPage />
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
            <Route path="/home" element={<HomePage />} />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;

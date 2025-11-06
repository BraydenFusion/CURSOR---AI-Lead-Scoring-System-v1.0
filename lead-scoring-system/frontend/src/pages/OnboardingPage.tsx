import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { getApiConfig } from "../config";

const API_BASE_URL = getApiConfig().baseUrl;

const COMPANY_ROLES = [
  "CEO/Founder",
  "VP Sales",
  "Sales Director",
  "Sales Manager",
  "Sales Rep",
  "Marketing Manager",
  "Other",
];

const PAYMENT_PLANS = [
  { id: "free", name: "Free", price: "$0", period: "forever", description: "Perfect for trying out LeadScore AI" },
  { id: "pro", name: "Pro", price: "$49", period: "per month", description: "For individual sales professionals" },
  { id: "team", name: "Team", price: "$149", period: "per month", description: "For small teams (up to 5 users)" },
  { id: "enterprise", name: "Enterprise", price: "Custom", period: "per month", description: "For large dealerships" },
];

export function OnboardingPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    company_name: "",
    company_role: "",
    payment_plan: "",
  });
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  // Redirect if user has already completed onboarding
  useEffect(() => {
    if (user?.onboarding_completed) {
      // Redirect to appropriate dashboard based on role
      if (user.role === "sales_rep") {
        navigate("/dashboard/sales-rep");
      } else if (user.role === "manager") {
        navigate("/dashboard/manager");
      } else if (user.role === "admin") {
        navigate("/dashboard/owner");
      } else {
        navigate("/dashboard");
      }
    }
  }, [user, navigate]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setError("");
  };

  const handleNext = () => {
    if (step === 1) {
      if (!formData.company_name.trim()) {
        setError("Company name is required");
        return;
      }
      if (!formData.company_role) {
        setError("Company role is required");
        return;
      }
      setStep(2);
    } else if (step === 2) {
      if (!formData.payment_plan) {
        setError("Please select a payment plan to continue");
        return;
      }
      handleComplete();
    }
  };

  const handleComplete = async () => {
    setIsLoading(true);
    setError("");

    try {
      const token = localStorage.getItem("token");
      if (!token) {
        throw new Error("Not authenticated");
      }

      const response = await fetch(`${API_BASE_URL}/auth/onboarding/complete`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        mode: "cors",
        credentials: "include",
        body: JSON.stringify({
          company_name: formData.company_name,
          company_role: formData.company_role,
          payment_plan: formData.payment_plan,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "Failed to complete onboarding" }));
        throw new Error(errorData.detail || "Failed to complete onboarding");
      }

      const userData = await response.json();
      
      // Redirect to appropriate dashboard based on role
      if (userData.role === "sales_rep") {
        navigate("/dashboard/sales-rep");
      } else if (userData.role === "manager") {
        navigate("/dashboard/manager");
      } else if (userData.role === "admin") {
        navigate("/dashboard/owner");
      } else {
        navigate("/dashboard");
      }
    } catch (err: any) {
      setError(err.message || "Failed to complete onboarding. Please try again.");
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 py-12 px-4">
      <Card className="w-full max-w-2xl">
        <CardHeader>
          <CardTitle className="text-2xl text-center">
            Welcome to LeadScore AI{user ? `, ${user.full_name}` : ""}!
          </CardTitle>
          <p className="text-center text-slate-600">
            Let's set up your account ({step} of 2)
          </p>
        </CardHeader>
        <CardContent>
          {error && (
            <div className="bg-red-50 text-red-600 p-3 rounded-md text-sm mb-4">{error}</div>
          )}

          {step === 1 && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">
                  Company Name <span className="text-red-500">*</span>
                </label>
                <Input
                  type="text"
                  name="company_name"
                  value={formData.company_name}
                  onChange={handleChange}
                  required
                  placeholder="Enter your company name"
                  disabled={isLoading}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">
                  Your Company Role <span className="text-red-500">*</span>
                </label>
                <select
                  name="company_role"
                  value={formData.company_role}
                  onChange={handleChange}
                  required
                  disabled={isLoading}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-navy-600 focus:border-transparent"
                >
                  <option value="">Select your role</option>
                  {COMPANY_ROLES.map((role) => (
                    <option key={role} value={role}>
                      {role}
                    </option>
                  ))}
                </select>
              </div>

              <Button
                onClick={handleNext}
                className="w-full bg-navy-600 hover:bg-navy-700"
                disabled={isLoading}
              >
                Continue
              </Button>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-semibold mb-4">Select a Payment Plan</h3>
                <p className="text-sm text-slate-600 mb-4">
                  Choose the plan that's right for you. You can change or cancel anytime.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {PAYMENT_PLANS.map((plan) => (
                  <div
                    key={plan.id}
                    onClick={() => {
                      setFormData((prev) => ({ ...prev, payment_plan: plan.id }));
                      setError("");
                    }}
                    className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                      formData.payment_plan === plan.id
                        ? "border-navy-600 bg-navy-50"
                        : "border-gray-200 hover:border-navy-300"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-semibold text-lg">{plan.name}</h4>
                      {formData.payment_plan === plan.id && (
                        <div className="w-5 h-5 rounded-full bg-navy-600 flex items-center justify-center">
                          <svg
                            className="w-3 h-3 text-white"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M5 13l4 4L19 7"
                            />
                          </svg>
                        </div>
                      )}
                    </div>
                    <div className="mb-2">
                      <span className="text-2xl font-bold">{plan.price}</span>
                      {plan.period !== "forever" && plan.price !== "Custom" && (
                        <span className="text-slate-600">/{plan.period}</span>
                      )}
                      {plan.period === "forever" && (
                        <span className="text-slate-600"> {plan.period}</span>
                      )}
                    </div>
                    <p className="text-sm text-slate-600">{plan.description}</p>
                  </div>
                ))}
              </div>

              <div className="flex gap-4">
                <Button
                  onClick={() => setStep(1)}
                  className="flex-1 bg-gray-200 text-gray-700 hover:bg-gray-300"
                  disabled={isLoading}
                >
                  Back
                </Button>
                <Button
                  onClick={handleNext}
                  className="flex-1 bg-navy-600 hover:bg-navy-700"
                  disabled={isLoading || !formData.payment_plan}
                >
                  {isLoading ? "Completing..." : "Complete Setup"}
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}


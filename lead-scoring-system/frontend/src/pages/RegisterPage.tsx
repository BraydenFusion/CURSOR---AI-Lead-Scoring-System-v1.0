import { useState, useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";

export function RegisterPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const selectedPlan = (location.state as any)?.plan || "free";
  
  const [formData, setFormData] = useState({
    email: "",
    username: "",
    full_name: "",
    password: "",
    confirmPassword: "",
    plan: selectedPlan,
    membership_type: "individual", // individual or team
    company_role: "",
  });
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const { register } = useAuth();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    // Validation
    if (formData.password.length < 8) {
      setError("Password must be at least 8 characters long");
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (formData.username.length < 3) {
      setError("Username must be at least 3 characters long");
      return;
    }

    if (!formData.company_role) {
      setError("Please select your company role");
      return;
    }

    setIsLoading(true);

    try {
      await register({
        email: formData.email,
        username: formData.username,
        full_name: formData.full_name,
        password: formData.password,
        company_role: formData.company_role || undefined,
      });
      // After successful registration, register function automatically logs in and redirects
    } catch (err: any) {
      setError(err.message || "Registration failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 py-12 px-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-2xl text-center">Create Account</CardTitle>
          <p className="text-center text-slate-600">Start your free trial - No credit card required</p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="bg-red-50 text-red-600 p-3 rounded-md text-sm">{error}</div>
            )}

            <div>
              <label className="block text-sm font-medium mb-1">Full Name</label>
              <Input
                type="text"
                name="full_name"
                value={formData.full_name}
                onChange={handleChange}
                required
                placeholder="Enter your full name"
                disabled={isLoading}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Email</label>
              <Input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                placeholder="Enter your email"
                disabled={isLoading}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Username</label>
              <Input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleChange}
                required
                minLength={3}
                placeholder="Choose a username (min 3 characters)"
                disabled={isLoading}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Password</label>
              <Input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                minLength={8}
                placeholder="Create a password (min 8 characters)"
                disabled={isLoading}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Confirm Password</label>
              <Input
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
                placeholder="Confirm your password"
                disabled={isLoading}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Membership Type</label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setFormData({ ...formData, membership_type: "individual" })}
                  className={`rounded-lg border-2 px-4 py-2 text-sm font-medium ${
                    formData.membership_type === "individual"
                      ? "border-navy-600 bg-navy-50 text-navy-600"
                      : "border-slate-300 bg-white text-slate-700 hover:bg-slate-50"
                  }`}
                >
                  Individual
                </button>
                <button
                  type="button"
                  onClick={() => setFormData({ ...formData, membership_type: "team" })}
                  className={`rounded-lg border-2 px-4 py-2 text-sm font-medium ${
                    formData.membership_type === "team"
                      ? "border-navy-600 bg-navy-50 text-navy-600"
                      : "border-slate-300 bg-white text-slate-700 hover:bg-slate-50"
                  }`}
                >
                  Team
                </button>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">What is your company role?</label>
              <select
                name="company_role"
                value={formData.company_role}
                onChange={(e) => setFormData({ ...formData, company_role: e.target.value })}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                required
                disabled={isLoading}
              >
                <option value="">Select your role</option>
                <option value="CEO/Founder">CEO/Founder</option>
                <option value="VP Sales">VP Sales</option>
                <option value="Sales Director">Sales Director</option>
                <option value="Sales Manager">Sales Manager</option>
                <option value="Sales Representative">Sales Representative</option>
                <option value="Account Executive">Account Executive</option>
                <option value="Business Development">Business Development</option>
                <option value="Marketing Manager">Marketing Manager</option>
                <option value="Marketing Director">Marketing Director</option>
                <option value="Operations Manager">Operations Manager</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Plan</label>
              <select
                name="plan"
                value={formData.plan}
                onChange={(e) => setFormData({ ...formData, plan: e.target.value })}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                disabled={isLoading}
              >
                <option value="free">Free (50 leads/month)</option>
                <option value="pro">Pro - $49/month (14-day trial)</option>
                {formData.membership_type === "team" && (
                  <>
                    <option value="team">Team - $149/month (14-day trial)</option>
                    <option value="enterprise">Enterprise (Custom pricing)</option>
                  </>
                )}
              </select>
              <p className="mt-1 text-xs text-slate-500">
                {formData.plan === "free" && "Perfect for trying out LeadScore AI"}
                {formData.plan === "pro" && "14-day free trial, then $49/month"}
                {formData.plan === "team" && "14-day free trial, then $149/month"}
                {formData.plan === "enterprise" && "Contact us for custom pricing"}
              </p>
            </div>

            <Button type="submit" className="w-full bg-navy-600 hover:bg-navy-700" disabled={isLoading}>
              {isLoading ? "Creating account..." : "Start Free Trial"}
            </Button>

            <div className="text-center mt-4 space-y-2">
              <p className="text-sm text-slate-600">
                Already have an account?{" "}
                <Link to="/login" className="text-navy-600 hover:underline font-medium">
                  Sign in
                </Link>
              </p>
              <p className="text-xs text-slate-500">
                By signing up, you agree to our Terms of Service and Privacy Policy
              </p>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}


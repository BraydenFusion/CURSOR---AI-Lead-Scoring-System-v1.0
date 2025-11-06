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
  const { register, googleSignIn } = useAuth();

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
    if (formData.password.length < 12) {
      setError("Password must be at least 12 characters long");
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
              <label htmlFor="company_role" className="block text-sm font-medium mb-1">What is your company role?</label>
              <select
                id="company_role"
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

            <div className="relative my-4">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">Or continue with</span>
              </div>
            </div>

            <Button
              type="button"
              onClick={async () => {
                setError("");
                setIsLoading(true);
                try {
                  await googleSignIn();
                } catch (err: any) {
                  setError(err.message || "Google Sign-In failed");
                } finally {
                  setIsLoading(false);
                }
              }}
              className="w-full bg-white text-gray-700 border border-gray-300 hover:bg-gray-50"
              disabled={isLoading}
            >
              <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                <path
                  fill="#4285F4"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="#34A853"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="#FBBC05"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                />
                <path
                  fill="#EA4335"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                />
              </svg>
              Sign up with Google
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


import { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { apiClient } from "../services/api";
import { NavBar } from "../components/NavBar";

interface UserProfile {
  id: string;
  email: string;
  username: string;
  full_name: string;
  role: string;
  profile_picture_url?: string;
}

export function SettingsPage() {
  const { user, login } = useAuth();
  const [activeTab, setActiveTab] = useState<"profile" | "security" | "documentation" | "notifications" | "billing">("profile");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  // Profile state
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [profilePicture, setProfilePicture] = useState<File | null>(null);
  const [profilePreview, setProfilePreview] = useState<string | null>(null);

  // Security state
  const [passwordForm, setPasswordForm] = useState({
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  });

  // Email state
  const [emailForm, setEmailForm] = useState({
    newEmail: "",
    password: "",
  });

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const response = await apiClient.get("/auth/me");
      setProfile(response.data);
      if (response.data.profile_picture_url) {
        setProfilePreview(response.data.profile_picture_url);
      }
    } catch (error) {
      console.error("Failed to load profile:", error);
    }
  };

  const handleProfilePictureChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith("image/")) {
        setMessage({ type: "error", text: "Please select an image file" });
        return;
      }
      // Validate file size (2MB max)
      if (file.size > 2 * 1024 * 1024) {
        setMessage({ type: "error", text: "Image must be less than 2MB" });
        return;
      }
      setProfilePicture(file);
      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setProfilePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleProfilePictureUpload = async () => {
    if (!profilePicture) return;

    setLoading(true);
    setMessage(null);

    try {
      const formData = new FormData();
      formData.append("file", profilePicture);

      const response = await apiClient.post("/auth/profile-picture", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setMessage({ type: "success", text: "Profile picture updated successfully!" });
      setProfilePicture(null);
      if (response.data.profile_picture_url) {
        setProfilePreview(response.data.profile_picture_url);
      }
    } catch (error: any) {
      setMessage({
        type: "error",
        text: error.response?.data?.detail || "Failed to upload profile picture",
      });
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      setMessage({ type: "error", text: "New passwords do not match" });
      setLoading(false);
      return;
    }

    try {
      await apiClient.post("/auth/change-password", {
        current_password: passwordForm.currentPassword,
        new_password: passwordForm.newPassword,
      });

      setMessage({ type: "success", text: "Password changed successfully!" });
      setPasswordForm({
        currentPassword: "",
        newPassword: "",
        confirmPassword: "",
      });
    } catch (error: any) {
      setMessage({
        type: "error",
        text: error.response?.data?.detail || "Failed to change password",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleEmailChange = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      await apiClient.post("/auth/change-email", {
        new_email: emailForm.newEmail,
        password: emailForm.password,
      });

      setMessage({ type: "success", text: "Email changed successfully! Please log in again." });
      setEmailForm({
        newEmail: "",
        password: "",
      });
      // Optionally log out user
      setTimeout(() => {
        window.location.href = "/login";
      }, 2000);
    } catch (error: any) {
      setMessage({
        type: "error",
        text: error.response?.data?.detail || "Failed to change email",
      });
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-slate-50">
        <NavBar />
        <div className="mx-auto max-w-7xl px-6 py-8">
          <div className="text-center">Please log in to access settings.</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <NavBar />
      <main className="mx-auto max-w-7xl px-6 py-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-slate-900">Settings</h1>
          <p className="mt-1 text-slate-600">Manage your account settings and preferences</p>
        </div>

        {/* Tabs */}
        <div className="mb-6 border-b border-slate-200">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: "profile" as const, label: "Profile", icon: "👤" },
              { id: "security" as const, label: "Security", icon: "🔒" },
              { id: "documentation" as const, label: "Documentation", icon: "📚" },
              { id: "notifications" as const, label: "Notifications", icon: "🔔" },
              { id: "billing" as const, label: "Billing", icon: "💳" },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => {
                  setActiveTab(tab.id);
                  setMessage(null);
                }}
                className={`flex items-center space-x-2 border-b-2 px-1 py-4 text-sm font-medium ${
                  activeTab === tab.id
                    ? "border-navy-600 text-navy-600"
                    : "border-transparent text-slate-500 hover:border-slate-300 hover:text-slate-700"
                }`}
              >
                <span>{tab.icon}</span>
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Message */}
        {message && (
          <div
            className={`mb-6 rounded-lg p-4 ${
              message.type === "success" ? "bg-green-50 text-green-700" : "bg-red-50 text-red-700"
            }`}
          >
            {message.text}
          </div>
        )}

        {/* Profile Tab */}
        {activeTab === "profile" && (
          <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="mb-6 text-xl font-bold text-slate-900">Profile Information</h2>

            {/* Profile Picture */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-slate-700">Profile Picture</label>
              <div className="mt-2 flex items-center space-x-6">
                <div className="flex h-24 w-24 items-center justify-center overflow-hidden rounded-full bg-slate-200">
                  {profilePreview ? (
                    <img src={profilePreview} alt="Profile" className="h-full w-full object-cover" />
                  ) : (
                    <span className="text-2xl text-slate-500">{user.full_name?.[0]?.toUpperCase() || "U"}</span>
                  )}
                </div>
                <div>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleProfilePictureChange}
                    className="block text-sm text-slate-500 file:mr-4 file:rounded file:border-0 file:bg-navy-50 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-navy-700 hover:file:bg-navy-100"
                  />
                  <p className="mt-1 text-xs text-slate-500">JPG, PNG or GIF. Max size 2MB.</p>
                  {profilePicture && (
                    <button
                      onClick={handleProfilePictureUpload}
                      disabled={loading}
                      className="mt-2 rounded-lg bg-navy-600 px-4 py-2 text-sm font-semibold text-white hover:bg-navy-700 disabled:opacity-50"
                    >
                      {loading ? "Uploading..." : "Upload Picture"}
                    </button>
                  )}
                </div>
              </div>
            </div>

            {/* Profile Info */}
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-slate-700">Full Name</label>
                <div className="mt-1 rounded-md border border-slate-300 bg-slate-50 px-3 py-2 text-slate-900">
                  {user.full_name}
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700">Username</label>
                <div className="mt-1 rounded-md border border-slate-300 bg-slate-50 px-3 py-2 text-slate-900">
                  {user.username}
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700">Email</label>
                <div className="mt-1 rounded-md border border-slate-300 bg-slate-50 px-3 py-2 text-slate-900">
                  {user.email}
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700">Role</label>
                <div className="mt-1 rounded-md border border-slate-300 bg-slate-50 px-3 py-2 text-slate-900 capitalize">
                  {user.role.replace("_", " ")}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Security Tab */}
        {activeTab === "security" && (
          <div className="space-y-6">
            {/* Change Password */}
            <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="mb-4 text-xl font-bold text-slate-900">Change Password</h2>
              <form onSubmit={handlePasswordChange} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700">Current Password</label>
                  <input
                    type="password"
                    value={passwordForm.currentPassword}
                    onChange={(e) => setPasswordForm({ ...passwordForm, currentPassword: e.target.value })}
                    className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700">New Password</label>
                  <input
                    type="password"
                    value={passwordForm.newPassword}
                    onChange={(e) => setPasswordForm({ ...passwordForm, newPassword: e.target.value })}
                    className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2"
                    required
                    minLength={12}
                  />
                  <p className="mt-1 text-xs text-slate-500">
                    Must be at least 12 characters with uppercase, lowercase, number, and special character
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700">Confirm New Password</label>
                  <input
                    type="password"
                    value={passwordForm.confirmPassword}
                    onChange={(e) => setPasswordForm({ ...passwordForm, confirmPassword: e.target.value })}
                    className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2"
                    required
                    minLength={12}
                  />
                </div>
                <button
                  type="submit"
                  disabled={loading}
                  className="rounded-lg bg-navy-600 px-4 py-2 font-semibold text-white hover:bg-navy-700 disabled:opacity-50"
                >
                  {loading ? "Changing..." : "Change Password"}
                </button>
              </form>
            </div>

            {/* Change Email */}
            <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="mb-4 text-xl font-bold text-slate-900">Change Email</h2>
              <form onSubmit={handleEmailChange} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700">New Email</label>
                  <input
                    type="email"
                    value={emailForm.newEmail}
                    onChange={(e) => setEmailForm({ ...emailForm, newEmail: e.target.value })}
                    className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700">Current Password</label>
                  <input
                    type="password"
                    value={emailForm.password}
                    onChange={(e) => setEmailForm({ ...emailForm, password: e.target.value })}
                    className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2"
                    required
                  />
                  <p className="mt-1 text-xs text-slate-500">Enter your current password to confirm the change</p>
                </div>
                <button
                  type="submit"
                  disabled={loading}
                  className="rounded-lg bg-navy-600 px-4 py-2 font-semibold text-white hover:bg-navy-700 disabled:opacity-50"
                >
                  {loading ? "Changing..." : "Change Email"}
                </button>
              </form>
            </div>
          </div>
        )}

        {/* Documentation Tab */}
        {activeTab === "documentation" && (
          <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="mb-6 text-xl font-bold text-slate-900">API Documentation</h2>
            <div className="space-y-4">
              <div className="rounded-lg border border-slate-200 p-4">
                <h3 className="font-semibold text-slate-900">Interactive API Documentation</h3>
                <p className="mt-1 text-sm text-slate-600">
                  Explore our API endpoints with interactive Swagger UI documentation.
                </p>
                <a
                  href="/docs"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-2 inline-block rounded-lg bg-navy-600 px-4 py-2 text-sm font-semibold text-white hover:bg-navy-700"
                >
                  Open Swagger UI →
                </a>
              </div>
              <div className="rounded-lg border border-slate-200 p-4">
                <h3 className="font-semibold text-slate-900">ReDoc Documentation</h3>
                <p className="mt-1 text-sm text-slate-600">
                  View our API documentation in a clean, readable format.
                </p>
                <a
                  href="/redoc"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-2 inline-block rounded-lg bg-navy-600 px-4 py-2 text-sm font-semibold text-white hover:bg-navy-700"
                >
                  Open ReDoc →
                </a>
              </div>
              <div className="rounded-lg border border-slate-200 p-4">
                <h3 className="font-semibold text-slate-900">OpenAPI Schema</h3>
                <p className="mt-1 text-sm text-slate-600">
                  Download the OpenAPI 3.0 schema for programmatic access.
                </p>
                <a
                  href="/openapi.json"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-2 inline-block rounded-lg bg-navy-600 px-4 py-2 text-sm font-semibold text-white hover:bg-navy-700"
                >
                  Download Schema →
                </a>
              </div>
              <div className="mt-6 rounded-lg bg-slate-50 p-4">
                <h3 className="font-semibold text-slate-900">Quick Start</h3>
                <p className="mt-2 text-sm text-slate-600">Get started with our API:</p>
                <ol className="ml-6 mt-2 list-decimal space-y-1 text-sm text-slate-600">
                  <li>Authenticate using <code className="rounded bg-slate-200 px-1">POST /api/auth/login</code></li>
                  <li>Use the returned JWT token in the Authorization header</li>
                  <li>Make API calls to endpoints like <code className="rounded bg-slate-200 px-1">GET /api/leads</code></li>
                  <li>Upload leads via <code className="rounded bg-slate-200 px-1">POST /api/upload/csv</code></li>
                </ol>
              </div>
            </div>
          </div>
        )}

        {/* Notifications Tab */}
        {activeTab === "notifications" && (
          <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="mb-6 text-xl font-bold text-slate-900">Notification Preferences</h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between rounded-lg border border-slate-200 p-4">
                <div>
                  <h3 className="font-semibold text-slate-900">Email Notifications</h3>
                  <p className="mt-1 text-sm text-slate-600">Receive email notifications for important events</p>
                </div>
                <label className="relative inline-flex cursor-pointer items-center">
                  <input type="checkbox" className="peer sr-only" defaultChecked />
                  <div className="peer h-6 w-11 rounded-full bg-slate-200 after:absolute after:left-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:border after:border-slate-300 after:bg-white after:transition-all after:content-[''] peer-checked:bg-navy-600 peer-checked:after:translate-x-full peer-checked:after:border-white"></div>
                </label>
              </div>
              <div className="flex items-center justify-between rounded-lg border border-slate-200 p-4">
                <div>
                  <h3 className="font-semibold text-slate-900">Lead Assignment Notifications</h3>
                  <p className="mt-1 text-sm text-slate-600">Get notified when leads are assigned to you</p>
                </div>
                <label className="relative inline-flex cursor-pointer items-center">
                  <input type="checkbox" className="peer sr-only" defaultChecked />
                  <div className="peer h-6 w-11 rounded-full bg-slate-200 after:absolute after:left-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:border after:border-slate-300 after:bg-white after:transition-all after:content-[''] peer-checked:bg-navy-600 peer-checked:after:translate-x-full peer-checked:after:border-white"></div>
                </label>
              </div>
              <div className="flex items-center justify-between rounded-lg border border-slate-200 p-4">
                <div>
                  <h3 className="font-semibold text-slate-900">Weekly Summary</h3>
                  <p className="mt-1 text-sm text-slate-600">Receive weekly performance summaries</p>
                </div>
                <label className="relative inline-flex cursor-pointer items-center">
                  <input type="checkbox" className="peer sr-only" />
                  <div className="peer h-6 w-11 rounded-full bg-slate-200 after:absolute after:left-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:border after:border-slate-300 after:bg-white after:transition-all after:content-[''] peer-checked:bg-navy-600 peer-checked:after:translate-x-full peer-checked:after:border-white"></div>
                </label>
              </div>
            </div>
          </div>
        )}

        {/* Billing Tab */}
        {activeTab === "billing" && (
          <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="mb-6 text-xl font-bold text-slate-900">Billing & Subscription</h2>
            <div className="space-y-4">
              <div className="rounded-lg border border-slate-200 p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold text-slate-900">Current Plan</h3>
                    <p className="mt-1 text-sm text-slate-600">Free Plan</p>
                  </div>
                  <Link
                    to="/pricing"
                    className="rounded-lg bg-navy-600 px-4 py-2 text-sm font-semibold text-white hover:bg-navy-700"
                  >
                    Upgrade Plan
                  </Link>
                </div>
              </div>
              <div className="rounded-lg border border-slate-200 p-4">
                <h3 className="font-semibold text-slate-900">Billing History</h3>
                <p className="mt-2 text-sm text-slate-600">No billing history available.</p>
              </div>
              <div className="rounded-lg border border-slate-200 p-4">
                <h3 className="font-semibold text-slate-900">Payment Methods</h3>
                <p className="mt-2 text-sm text-slate-600">No payment methods on file.</p>
                <button className="mt-2 rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50">
                  Add Payment Method
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}


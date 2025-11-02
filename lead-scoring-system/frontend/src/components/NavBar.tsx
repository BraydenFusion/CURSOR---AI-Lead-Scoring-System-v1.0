import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { Button } from "./ui/button";
import { NotificationBell } from "./NotificationBell";

export function NavBar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="container mx-auto px-4 sm:px-6 py-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center">
            <h1
              className="text-lg sm:text-xl font-bold cursor-pointer"
              onClick={() => {
                navigate("/dashboard");
                setMobileMenuOpen(false);
              }}
            >
              Lead Scoring System
            </h1>
            {/* Mobile menu button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="ml-4 sm:hidden p-2 rounded-md text-gray-600 hover:bg-gray-100"
              aria-label="Toggle menu"
            >
              <svg
                className="w-6 h-6"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                {mobileMenuOpen ? (
                  <path d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>

          {/* Desktop navigation */}
          <div className="hidden sm:flex gap-4 items-center">
            {user && (
              <p className="text-sm text-gray-600 hidden md:block">
                Welcome, {user.full_name} ({user.role})
              </p>
            )}
            {user?.role === "sales_rep" && (
              <Button onClick={() => navigate("/my-leads")} variant="outline" size="sm">
                My Leads
              </Button>
            )}
            {user && <NotificationBell />}
            {user && (
              <Button onClick={logout} variant="outline" size="sm">
                Logout
              </Button>
            )}
          </div>

          {/* Mobile navigation menu */}
          {mobileMenuOpen && (
            <div className="absolute top-full left-0 right-0 bg-white border-b shadow-lg sm:hidden z-50">
              <div className="container mx-auto px-4 py-4 space-y-3">
                {user && (
                  <div className="pb-3 border-b">
                    <p className="text-sm font-medium text-gray-900">{user.full_name}</p>
                    <p className="text-xs text-gray-500">{user.role}</p>
                  </div>
                )}
                {user?.role === "sales_rep" && (
                  <button
                    onClick={() => {
                      navigate("/my-leads");
                      setMobileMenuOpen(false);
                    }}
                    className="w-full text-left px-4 py-2 rounded-md hover:bg-gray-100 text-gray-700"
                  >
                    My Leads
                  </button>
                )}
                <button
                  onClick={() => {
                    navigate("/dashboard");
                    setMobileMenuOpen(false);
                  }}
                  className="w-full text-left px-4 py-2 rounded-md hover:bg-gray-100 text-gray-700"
                >
                  Dashboard
                </button>
                <div className="flex items-center justify-between px-4 py-2">
                  <span className="text-gray-700">Notifications</span>
                  {user && <NotificationBell />}
                </div>
                {user && (
                  <button
                    onClick={() => {
                      logout();
                      setMobileMenuOpen(false);
                    }}
                    className="w-full text-left px-4 py-2 rounded-md hover:bg-gray-100 text-red-600 font-medium"
                  >
                    Logout
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}


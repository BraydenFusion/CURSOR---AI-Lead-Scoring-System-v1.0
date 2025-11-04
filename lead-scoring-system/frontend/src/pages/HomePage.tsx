import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export function HomePage() {
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const handleGetStarted = () => {
    if (isAuthenticated) {
      navigate("/dashboard");
    } else {
      navigate("/register");
    }
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-7xl px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-navy-600 text-white">
                <span className="text-xl font-bold">LS</span>
              </div>
              <span className="text-xl font-bold text-slate-900">LeadScore AI</span>
            </div>
            <div className="hidden items-center space-x-6 md:flex">
              <Link to="/features" className="text-slate-600 hover:text-navy-600">
                Features
              </Link>
              <Link to="/pricing" className="text-slate-600 hover:text-navy-600">
                Pricing
              </Link>
              {isAuthenticated ? (
                <Link
                  to="/dashboard"
                  className="rounded-lg bg-navy-600 px-4 py-2 font-semibold text-white hover:bg-navy-700"
                >
                  Dashboard
                </Link>
              ) : (
                <>
                  <Link to="/login" className="text-slate-600 hover:text-navy-600">
                    Login
                  </Link>
                  <button
                    onClick={handleGetStarted}
                    className="rounded-lg bg-navy-600 px-4 py-2 font-semibold text-white hover:bg-navy-700"
                  >
                    Start for Free
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="bg-gradient-to-b from-slate-50 to-white py-20">
        <div className="mx-auto max-w-7xl px-6">
          <div className="text-center">
            <h1 className="text-5xl font-bold tracking-tight text-slate-900 sm:text-6xl">
              AI-Powered Lead Scoring
              <br />
              <span className="text-navy-600">for Modern Dealerships</span>
            </h1>
            <p className="mx-auto mt-6 max-w-2xl text-lg leading-8 text-slate-600">
              Transform your sales process with intelligent lead scoring. Upload leads, get instant AI-powered insights,
              and prioritize your hottest prospects—all in one platform.
            </p>
            <div className="mt-10 flex items-center justify-center gap-x-6">
              <button
                onClick={handleGetStarted}
                className="rounded-lg bg-navy-600 px-6 py-3 text-base font-semibold text-white shadow-sm hover:bg-navy-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-navy-600"
              >
                Start for Free
              </button>
              <Link
                to="/pricing"
                className="text-base font-semibold leading-6 text-slate-900 hover:text-navy-600"
              >
                View Pricing <span aria-hidden="true">→</span>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20">
        <div className="mx-auto max-w-7xl px-6">
          <div className="text-center">
            <h2 className="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
              Everything you need to grow your dealership
            </h2>
            <p className="mx-auto mt-4 max-w-2xl text-lg text-slate-600">
              Powerful features designed to help you close more deals, faster.
            </p>
          </div>

          <div className="mt-16 grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3">
            <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-navy-100">
                <svg className="h-6 w-6 text-navy-600" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-slate-900">AI-Powered Scoring</h3>
              <p className="mt-2 text-slate-600">
                Get instant lead scores using advanced AI. Automatically classify leads as HOT, WARM, or COLD based on
                engagement, buying signals, and demographics.
              </p>
            </div>

            <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-navy-100">
                <svg className="h-6 w-6 text-navy-600" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-slate-900">Bulk CSV Upload</h3>
              <p className="mt-2 text-slate-600">
                Import hundreds of leads at once with our CSV upload feature. Perfect for migrating from your existing
                CRM or importing leads from trade shows and events.
              </p>
            </div>

            <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-navy-100">
                <svg className="h-6 w-6 text-navy-600" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-slate-900">Role-Based Dashboards</h3>
              <p className="mt-2 text-slate-600">
                Custom dashboards for sales reps, managers, and owners. Each role sees exactly what they need to manage
                leads effectively.
              </p>
            </div>

            <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-navy-100">
                <svg className="h-6 w-6 text-navy-600" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 18L9 11.25l4.306 4.307a11.95 11.95 0 015.814-5.518l2.74-1.22m0 0l-5.94-2.28m5.94 2.28l-2.28 5.941" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-slate-900">Real-Time Analytics</h3>
              <p className="mt-2 text-slate-600">
                Track performance with comprehensive analytics. See conversion rates, top performers, and lead sources
                all in one place.
              </p>
            </div>

            <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-navy-100">
                <svg className="h-6 w-6 text-navy-600" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 21a9.004 9.004 0 008.716-6.747M12 21a9.004 9.004 0 01-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 017.843 4.582M12 3a8.997 8.997 0 00-7.843 4.582m15.686 0A11.953 11.953 0 0112 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0121 12c0 .778-.099 1.533-.284 2.253m0 0A17.919 17.919 0 0112 16.5c-3.162 0-6.133-.815-8.716-2.247m0 0A9.015 9.015 0 013 12c0-1.605.42-3.113 1.157-4.418" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-slate-900">Team Collaboration</h3>
              <p className="mt-2 text-slate-600">
                Managers can oversee all sales reps, assign leads, and track team performance. Perfect for growing
                dealerships.
              </p>
            </div>

            <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-navy-100">
                <svg className="h-6 w-6 text-navy-600" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 0112 2.25c-2.851 0-5.432.968-7.5 2.532A11.99 11.99 0 003 18.75a11.98 11.98 0 007.5 2.5c.357 0 .708-.023 1.05-.07m0-16.5a11.95 11.95 0 0114.318 0M14.25 18.75a11.95 11.95 0 01-1.432-5.77m0 0a11.95 11.95 0 015.432-5.77M14.25 18.75a11.98 11.98 0 01-1.432 5.77m5.432-5.77a11.95 11.95 0 00-5.432-5.77" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-slate-900">Secure & Reliable</h3>
              <p className="mt-2 text-slate-600">
                Enterprise-grade security with encrypted data storage. Your leads and customer data are always safe
                and secure.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-navy-600 py-16">
        <div className="mx-auto max-w-7xl px-6 text-center">
          <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
            Ready to transform your sales process?
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-navy-100">
            Join dealerships already using AI to close more deals and grow their business.
          </p>
          <div className="mt-10">
            <button
              onClick={handleGetStarted}
              className="rounded-lg bg-white px-6 py-3 text-base font-semibold text-navy-600 shadow-sm hover:bg-slate-50"
            >
              Start for Free
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white">
        <div className="mx-auto max-w-7xl px-6 py-12">
          <div className="grid grid-cols-1 gap-8 md:grid-cols-4">
            <div>
              <div className="flex items-center space-x-2">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-navy-600 text-white">
                  <span className="text-xl font-bold">LS</span>
                </div>
                <span className="text-xl font-bold text-slate-900">LeadScore AI</span>
              </div>
              <p className="mt-4 text-sm text-slate-600">
                AI-powered lead scoring for modern dealerships.
              </p>
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-900">Product</h3>
              <ul className="mt-4 space-y-2">
                <li>
                  <Link to="/features" className="text-sm text-slate-600 hover:text-navy-600">
                    Features
                  </Link>
                </li>
                <li>
                  <Link to="/pricing" className="text-sm text-slate-600 hover:text-navy-600">
                    Pricing
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-900">Company</h3>
              <ul className="mt-4 space-y-2">
                <li>
                  <a href="#" className="text-sm text-slate-600 hover:text-navy-600">
                    About
                  </a>
                </li>
                <li>
                  <a href="#" className="text-sm text-slate-600 hover:text-navy-600">
                    Contact
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-900">Legal</h3>
              <ul className="mt-4 space-y-2">
                <li>
                  <a href="#" className="text-sm text-slate-600 hover:text-navy-600">
                    Privacy
                  </a>
                </li>
                <li>
                  <a href="#" className="text-sm text-slate-600 hover:text-navy-600">
                    Terms
                  </a>
                </li>
              </ul>
            </div>
          </div>
          <div className="mt-8 border-t border-slate-200 pt-8 text-center text-sm text-slate-600">
            © 2025 LeadScore AI. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
}


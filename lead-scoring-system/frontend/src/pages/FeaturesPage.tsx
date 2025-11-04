import { Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export function FeaturesPage() {
  const { isAuthenticated } = useAuth();

  const features = [
    {
      icon: "🎯",
      title: "AI-Powered Lead Scoring",
      description: "Get instant lead scores using advanced GPT-4 AI. Automatically classify leads as HOT, WARM, or COLD based on engagement patterns, buying signals, and demographic fit.",
      details: [
        "Overall score (0-100) with detailed breakdown",
        "Engagement score based on activity patterns",
        "Buying signal detection",
        "Demographic fit analysis",
        "Confidence level for each score",
        "AI-generated insights and talking points"
      ]
    },
    {
      icon: "📤",
      title: "Bulk CSV Upload",
      description: "Import hundreds of leads at once with our secure CSV upload feature. Perfect for migrating from your existing CRM or importing leads from trade shows.",
      details: [
        "Drag-and-drop CSV file upload",
        "Automatic validation and error reporting",
        "Up to 1000 leads per upload",
        "10MB file size limit",
        "Real-time processing status",
        "Detailed error reports for failed rows"
      ]
    },
    {
      icon: "📊",
      title: "Role-Based Dashboards",
      description: "Custom dashboards for every role. Sales reps see their leads, managers see team performance, and owners see complete system analytics.",
      details: [
        "Sales Rep Dashboard: Personal leads and statistics",
        "Manager Dashboard: Team overview and performance",
        "Owner Dashboard: Complete system analytics",
        "Real-time updates",
        "Interactive charts and graphs",
        "Export capabilities"
      ]
    },
    {
      icon: "🔍",
      title: "Advanced Analytics",
      description: "Track performance with comprehensive analytics. See conversion rates, top performers, and lead sources all in one place.",
      details: [
        "Conversion rate tracking",
        "Top performing sales reps",
        "Lead source analysis",
        "Hot/Warm/Cold breakdown",
        "Average score trends",
        "Status distribution"
      ]
    },
    {
      icon: "👥",
      title: "Team Collaboration",
      description: "Managers can oversee all sales reps, assign leads, and track team performance. Perfect for growing dealerships.",
      details: [
        "Lead assignment system",
        "Team performance comparison",
        "Shared workspace",
        "Activity tracking",
        "Notification system",
        "Notes and comments"
      ]
    },
    {
      icon: "🔐",
      title: "Enterprise Security",
      description: "Enterprise-grade security with encrypted data storage. Your leads and customer data are always safe and secure.",
      details: [
        "End-to-end encryption",
        "Role-based access control",
        "Audit logging",
        "Secure password requirements",
        "Breach database checking",
        "Regular security audits"
      ]
    },
    {
      icon: "⚡",
      title: "Real-Time Updates",
      description: "All data updates in real-time. See new leads, score changes, and team activity as it happens.",
      details: [
        "Live dashboard updates",
        "Instant scoring results",
        "Real-time notifications",
        "Activity feed",
        "Status changes",
        "Performance metrics"
      ]
    },
    {
      icon: "📱",
      title: "Mobile Responsive",
      description: "Access your dashboard from any device. Fully responsive design works perfectly on desktop, tablet, and mobile.",
      details: [
        "Mobile-optimized interface",
        "Touch-friendly controls",
        "Responsive tables and charts",
        "Offline capability",
        "Progressive Web App ready",
        "Cross-platform compatibility"
      ]
    },
    {
      icon: "🔌",
      title: "API Access",
      description: "Integrate LeadScore AI with your existing systems using our comprehensive REST API.",
      details: [
        "RESTful API design",
        "Comprehensive documentation",
        "API key authentication",
        "Rate limiting",
        "Webhook support",
        "SDK libraries"
      ]
    }
  ];

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-7xl px-6 py-4">
          <div className="flex items-center justify-between">
            <Link to="/" className="flex items-center space-x-2">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-[#1e3a8a] text-white">
                <span className="text-xl font-bold">LS</span>
              </div>
              <span className="text-xl font-bold text-slate-900">LeadScore AI</span>
            </Link>
            <div className="hidden items-center space-x-6 md:flex">
              <Link to="/" className="text-slate-600 hover:text-navy-600">
                Home
              </Link>
              <Link to="/features" className="font-semibold text-navy-600">
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
                  <Link
                    to="/register"
                    className="rounded-lg bg-navy-600 px-4 py-2 font-semibold text-white hover:bg-navy-700"
                  >
                    Start for Free
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="bg-gradient-to-b from-slate-50 to-white py-16">
        <div className="mx-auto max-w-7xl px-6 text-center">
          <h1 className="text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
            Powerful Features for Modern Dealerships
          </h1>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-slate-600">
            Everything you need to grow your dealership with AI-powered lead scoring and management.
          </p>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-20">
        <div className="mx-auto max-w-7xl px-6">
          <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3">
            {features.map((feature, index) => (
              <div
                key={index}
                className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm transition-shadow hover:shadow-md"
              >
                <div className="mb-4 text-4xl">{feature.icon}</div>
                <h3 className="text-xl font-semibold text-slate-900">{feature.title}</h3>
                <p className="mt-2 text-slate-600">{feature.description}</p>
                <ul className="mt-4 space-y-2">
                  {feature.details.map((detail, idx) => (
                    <li key={idx} className="flex items-start text-sm text-slate-600">
                      <svg
                        className="mr-2 h-5 w-5 flex-shrink-0 text-navy-600"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fillRule="evenodd"
                          d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z"
                          clipRule="evenodd"
                        />
                      </svg>
                      {detail}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-navy-600 py-16">
        <div className="mx-auto max-w-7xl px-6 text-center">
          <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
            Ready to get started?
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-navy-100">
            Start your free trial today. No credit card required.
          </p>
          <div className="mt-10">
            {isAuthenticated ? (
              <Link
                to="/dashboard"
                className="rounded-lg bg-white px-6 py-3 text-base font-semibold text-navy-600 shadow-sm hover:bg-slate-50"
              >
                Go to Dashboard
              </Link>
            ) : (
              <Link
                to="/register"
                className="rounded-lg bg-white px-6 py-3 text-base font-semibold text-navy-600 shadow-sm hover:bg-slate-50"
              >
                Start for Free
              </Link>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}


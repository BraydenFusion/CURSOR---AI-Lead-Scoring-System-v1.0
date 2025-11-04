import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export function PricingPage() {
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const handleGetStarted = (plan: string) => {
    if (isAuthenticated) {
      navigate("/dashboard");
    } else {
      navigate("/register", { state: { plan } });
    }
  };

  const individualPlans = [
    {
      name: "Free",
      price: "$0",
      period: "forever",
      description: "Perfect for trying out LeadScore AI",
      features: [
        "Up to 50 leads per month",
        "AI-powered scoring",
        "Basic dashboard",
        "CSV upload support",
        "Email support",
      ],
      cta: "Start for Free",
      popular: false,
    },
    {
      name: "Pro",
      price: "$49",
      period: "per month",
      description: "For individual sales professionals",
      features: [
        "Unlimited leads",
        "Advanced AI scoring",
        "Full dashboard access",
        "Priority support",
        "Export reports",
        "API access",
      ],
      cta: "Start Free Trial",
      popular: true,
    },
  ];

  const teamPlans = [
    {
      name: "Team",
      price: "$149",
      period: "per month",
      description: "For small teams (up to 5 users)",
      features: [
        "Everything in Pro",
        "Up to 5 team members",
        "Manager dashboard",
        "Team analytics",
        "Lead assignment",
        "Shared workspace",
      ],
      cta: "Start Free Trial",
      popular: false,
    },
    {
      name: "Enterprise",
      price: "Custom",
      period: "per month",
      description: "For large dealerships",
      features: [
        "Everything in Team",
        "Unlimited team members",
        "Owner dashboard",
        "Advanced analytics",
        "Custom integrations",
        "Dedicated support",
        "SLA guarantee",
      ],
      cta: "Contact Sales",
      popular: false,
    },
  ];

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-7xl px-6 py-4">
          <div className="flex items-center justify-between">
            <Link to="/" className="flex items-center space-x-2">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-navy-600 text-white">
                <span className="text-xl font-bold">LS</span>
              </div>
              <span className="text-xl font-bold text-slate-900">LeadScore AI</span>
            </Link>
            <div className="hidden items-center space-x-6 md:flex">
              <Link to="/" className="text-slate-600 hover:text-navy-600">
                Home
              </Link>
              <Link to="/features" className="text-slate-600 hover:text-navy-600">
                Features
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

      {/* Pricing Header */}
      <section className="bg-gradient-to-b from-slate-50 to-white py-16">
        <div className="mx-auto max-w-7xl px-6 text-center">
          <h1 className="text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
            Simple, transparent pricing
          </h1>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-slate-600">
            Choose the plan that's right for you. Start free, upgrade anytime.
          </p>
        </div>
      </section>

      {/* Individual Plans */}
      <section className="py-16">
        <div className="mx-auto max-w-7xl px-6">
          <div className="mb-12 text-center">
            <h2 className="text-3xl font-bold text-slate-900">Individual Plans</h2>
            <p className="mt-2 text-slate-600">Perfect for solo sales professionals</p>
          </div>

          <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-2">
            {individualPlans.map((plan) => (
              <div
                key={plan.name}
                className={`relative rounded-lg border-2 p-8 ${
                  plan.popular
                    ? "border-navy-600 bg-white shadow-lg"
                    : "border-slate-200 bg-white"
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                    <span className="rounded-full bg-navy-600 px-4 py-1 text-sm font-semibold text-white">
                      Most Popular
                    </span>
                  </div>
                )}
                <div className="text-center">
                  <h3 className="text-2xl font-bold text-slate-900">{plan.name}</h3>
                  <div className="mt-4">
                    <span className="text-4xl font-bold text-slate-900">{plan.price}</span>
                    {plan.period !== "forever" && (
                      <span className="text-slate-600">/{plan.period}</span>
                    )}
                    {plan.period === "forever" && (
                      <span className="text-slate-600"> {plan.period}</span>
                    )}
                  </div>
                  <p className="mt-2 text-sm text-slate-600">{plan.description}</p>
                </div>
                <ul className="mt-8 space-y-4">
                  {plan.features.map((feature, index) => (
                    <li key={index} className="flex items-start">
                      <svg
                        className="h-5 w-5 flex-shrink-0 text-navy-600"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fillRule="evenodd"
                          d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z"
                          clipRule="evenodd"
                        />
                      </svg>
                      <span className="ml-3 text-slate-600">{feature}</span>
                    </li>
                  ))}
                </ul>
                <button
                  onClick={() => handleGetStarted(plan.name.toLowerCase())}
                  className={`mt-8 w-full rounded-lg px-4 py-3 font-semibold ${
                    plan.popular
                      ? "bg-navy-600 text-white hover:bg-navy-700"
                      : "border-2 border-navy-600 bg-white text-navy-600 hover:bg-navy-50"
                  }`}
                >
                  {plan.cta}
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Team Plans */}
      <section className="bg-slate-50 py-16">
        <div className="mx-auto max-w-7xl px-6">
          <div className="mb-12 text-center">
            <h2 className="text-3xl font-bold text-slate-900">Team Plans</h2>
            <p className="mt-2 text-slate-600">For growing dealerships and teams</p>
          </div>

          <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-2">
            {teamPlans.map((plan) => (
              <div
                key={plan.name}
                className={`relative rounded-lg border-2 p-8 ${
                  plan.popular
                    ? "border-navy-600 bg-white shadow-lg"
                    : "border-slate-200 bg-white"
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                    <span className="rounded-full bg-navy-600 px-4 py-1 text-sm font-semibold text-white">
                      Most Popular
                    </span>
                  </div>
                )}
                <div className="text-center">
                  <h3 className="text-2xl font-bold text-slate-900">{plan.name}</h3>
                  <div className="mt-4">
                    <span className="text-4xl font-bold text-slate-900">{plan.price}</span>
                    {plan.price !== "Custom" && (
                      <span className="text-slate-600">/{plan.period}</span>
                    )}
                  </div>
                  <p className="mt-2 text-sm text-slate-600">{plan.description}</p>
                </div>
                <ul className="mt-8 space-y-4">
                  {plan.features.map((feature, index) => (
                    <li key={index} className="flex items-start">
                      <svg
                        className="h-5 w-5 flex-shrink-0 text-navy-600"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fillRule="evenodd"
                          d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z"
                          clipRule="evenodd"
                        />
                      </svg>
                      <span className="ml-3 text-slate-600">{feature}</span>
                    </li>
                  ))}
                </ul>
                <button
                  onClick={() => handleGetStarted(plan.name.toLowerCase())}
                  className={`mt-8 w-full rounded-lg px-4 py-3 font-semibold ${
                    plan.popular
                      ? "bg-navy-600 text-white hover:bg-navy-700"
                      : "border-2 border-navy-600 bg-white text-navy-600 hover:bg-navy-50"
                  }`}
                >
                  {plan.cta}
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-16">
        <div className="mx-auto max-w-3xl px-6">
          <h2 className="text-center text-3xl font-bold text-slate-900">Frequently Asked Questions</h2>
          <div className="mt-12 space-y-8">
            <div>
              <h3 className="text-lg font-semibold text-slate-900">Can I change plans later?</h3>
              <p className="mt-2 text-slate-600">
                Yes! You can upgrade or downgrade your plan at any time. Changes take effect immediately.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-slate-900">What payment methods do you accept?</h3>
              <p className="mt-2 text-slate-600">
                We accept all major credit cards. Enterprise plans can be invoiced.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-slate-900">Is there a free trial?</h3>
              <p className="mt-2 text-slate-600">
                Yes! All paid plans come with a 14-day free trial. No credit card required.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-slate-900">How does AI scoring work?</h3>
              <p className="mt-2 text-slate-600">
                Our AI analyzes lead data, engagement patterns, and buying signals to automatically score and
                classify leads. All scoring happens instantly when you upload leads.
              </p>
            </div>
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
            <Link
              to="/register"
              className="rounded-lg bg-white px-6 py-3 text-base font-semibold text-navy-600 shadow-sm hover:bg-slate-50"
            >
              Start for Free
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}


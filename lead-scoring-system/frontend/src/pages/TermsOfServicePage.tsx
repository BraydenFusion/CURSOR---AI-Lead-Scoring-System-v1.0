import { Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export function TermsOfServicePage() {
  const { isAuthenticated } = useAuth();

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

      {/* Content */}
      <main className="mx-auto max-w-4xl px-6 py-12">
        <h1 className="text-4xl font-bold text-slate-900">Terms of Service</h1>
        <p className="mt-2 text-slate-600">Last updated: January 4, 2025</p>

        <div className="prose prose-slate mt-8 max-w-none">
          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-slate-900">1. Acceptance of Terms</h2>
            <p className="mt-2 text-slate-600">
              By accessing and using LeadScore AI ("Service"), you accept and agree to be bound by the terms and
              provision of this agreement. If you do not agree to these Terms of Service, please do not use the Service.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-slate-900">2. Use License</h2>
            <p className="mt-2 text-slate-600">
              Permission is granted to temporarily access the materials on LeadScore AI's website for personal,
              non-commercial transitory viewing only. This is the grant of a license, not a transfer of title, and under
              this license you may not:
            </p>
            <ul className="ml-6 mt-2 list-disc text-slate-600">
              <li>Modify or copy the materials</li>
              <li>Use the materials for any commercial purpose or for any public display</li>
              <li>Attempt to reverse engineer any software contained on LeadScore AI's website</li>
              <li>Remove any copyright or other proprietary notations from the materials</li>
              <li>Transfer the materials to another person or "mirror" the materials on any other server</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-slate-900">3. User Accounts</h2>
            <p className="mt-2 text-slate-600">
              You are responsible for maintaining the confidentiality of your account and password. You agree to accept
              responsibility for all activities that occur under your account or password. You must notify us immediately
              of any unauthorized use of your account.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-slate-900">4. Data and Privacy</h2>
            <p className="mt-2 text-slate-600">
              You retain all rights to your data. We will not access, use, or share your data except as necessary to
              provide the Service or as required by law. Please review our Privacy Policy for more information.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-slate-900">5. Payment Terms</h2>
            <p className="mt-2 text-slate-600">
              If you choose a paid plan, you agree to pay all charges associated with your subscription. All fees are
              charged in advance on a monthly or annual basis. You may cancel your subscription at any time, and your
              access will continue until the end of the current billing period.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-slate-900">6. Service Availability</h2>
            <p className="mt-2 text-slate-600">
              We strive to provide reliable service but do not guarantee uninterrupted access. The Service may be
              temporarily unavailable due to maintenance, updates, or circumstances beyond our control.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-slate-900">7. Prohibited Uses</h2>
            <p className="mt-2 text-slate-600">You may not use the Service:</p>
            <ul className="ml-6 mt-2 list-disc text-slate-600">
              <li>In any way that violates any applicable law or regulation</li>
              <li>To transmit any malicious code or viruses</li>
              <li>To attempt to gain unauthorized access to any part of the Service</li>
              <li>To interfere with or disrupt the Service or servers</li>
              <li>To collect or store personal data about other users</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-slate-900">8. Intellectual Property</h2>
            <p className="mt-2 text-slate-600">
              All content, features, and functionality of the Service are owned by LeadScore AI and are protected by
              international copyright, trademark, and other intellectual property laws.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-slate-900">9. Limitation of Liability</h2>
            <p className="mt-2 text-slate-600">
              In no event shall LeadScore AI or its suppliers be liable for any damages (including, without limitation,
              damages for loss of data or profit, or due to business interruption) arising out of the use or inability to
              use the Service.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-slate-900">10. Termination</h2>
            <p className="mt-2 text-slate-600">
              We reserve the right to terminate or suspend your account and access to the Service immediately, without
              prior notice, for conduct that we believe violates these Terms of Service or is harmful to other users,
              us, or third parties.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-slate-900">11. Changes to Terms</h2>
            <p className="mt-2 text-slate-600">
              We reserve the right to revise these Terms of Service at any time. By continuing to use the Service after
              changes are made, you agree to be bound by the revised terms.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-slate-900">12. Contact Information</h2>
            <p className="mt-2 text-slate-600">
              If you have any questions about these Terms of Service, please contact us at support@leadscoreai.com
            </p>
          </section>
        </div>
      </main>
    </div>
  );
}


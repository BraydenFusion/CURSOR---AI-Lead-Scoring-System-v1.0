import { Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export function PrivacyPolicyPage() {
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
        <h1 className="text-4xl font-bold text-slate-900">Privacy Policy</h1>
        <p className="mt-2 text-slate-600">Last updated: January 4, 2025</p>

        <div className="prose prose-slate mt-8 max-w-none">
          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-slate-900">1. Introduction</h2>
            <p className="mt-2 text-slate-600">
              LeadScore AI ("we," "our," or "us") is committed to protecting your privacy. This Privacy Policy explains
              how we collect, use, disclose, and safeguard your information when you use our Service.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-slate-900">2. Information We Collect</h2>
            <h3 className="mt-4 text-xl font-semibold text-slate-900">2.1 Account Information</h3>
            <p className="mt-2 text-slate-600">
              When you create an account, we collect:
            </p>
            <ul className="ml-6 mt-2 list-disc text-slate-600">
              <li>Email address</li>
              <li>Username</li>
              <li>Full name</li>
              <li>Password (encrypted)</li>
            </ul>

            <h3 className="mt-4 text-xl font-semibold text-slate-900">2.2 Lead Data</h3>
            <p className="mt-2 text-slate-600">
              When you upload leads, we store:
            </p>
            <ul className="ml-6 mt-2 list-disc text-slate-600">
              <li>Lead names and contact information</li>
              <li>Email addresses and phone numbers</li>
              <li>Lead source and location data</li>
              <li>Scoring and classification data</li>
              <li>Activity and engagement data</li>
            </ul>

            <h3 className="mt-4 text-xl font-semibold text-slate-900">2.3 Usage Data</h3>
            <p className="mt-2 text-slate-600">
              We automatically collect information about how you use the Service, including:
            </p>
            <ul className="ml-6 mt-2 list-disc text-slate-600">
              <li>Login times and frequency</li>
              <li>Features accessed</li>
              <li>API usage</li>
              <li>Error logs</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-slate-900">3. How We Use Your Information</h2>
            <p className="mt-2 text-slate-600">We use the information we collect to:</p>
            <ul className="ml-6 mt-2 list-disc text-slate-600">
              <li>Provide, maintain, and improve the Service</li>
              <li>Process and score your leads using AI</li>
              <li>Send you important updates about the Service</li>
              <li>Respond to your inquiries and support requests</li>
              <li>Detect and prevent fraud or abuse</li>
              <li>Comply with legal obligations</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-slate-900">4. Data Storage and Security</h2>
            <p className="mt-2 text-slate-600">
              We implement industry-standard security measures to protect your data:
            </p>
            <ul className="ml-6 mt-2 list-disc text-slate-600">
              <li>Encryption in transit (HTTPS/TLS)</li>
              <li>Encryption at rest</li>
              <li>Secure password hashing (bcrypt)</li>
              <li>Regular security audits</li>
              <li>Access controls and authentication</li>
              <li>Data backup and recovery procedures</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-slate-900">5. Data Sharing and Disclosure</h2>
            <p className="mt-2 text-slate-600">
              We do not sell, trade, or rent your personal information to third parties. We may share your information
              only in the following circumstances:
            </p>
            <ul className="ml-6 mt-2 list-disc text-slate-600">
              <li>
                <strong>Service Providers:</strong> With trusted third-party service providers who assist in operating
                our Service (e.g., cloud hosting, AI processing)
              </li>
              <li>
                <strong>Legal Requirements:</strong> When required by law or to protect our rights
              </li>
              <li>
                <strong>Business Transfers:</strong> In connection with a merger, acquisition, or sale of assets
              </li>
              <li>
                <strong>With Your Consent:</strong> When you explicitly authorize us to share your information
              </li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-slate-900">6. AI Processing and Third-Party Services</h2>
            <p className="mt-2 text-slate-600">
              We use OpenAI's GPT-4 API to process and score leads. When you upload leads, relevant data is sent to
              OpenAI for AI analysis. OpenAI's use of your data is governed by their privacy policy. We do not use your
              lead data to train OpenAI's models.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-slate-900">7. Your Rights and Choices</h2>
            <p className="mt-2 text-slate-600">You have the right to:</p>
            <ul className="ml-6 mt-2 list-disc text-slate-600">
              <li>
                <strong>Access:</strong> Request a copy of your personal data
              </li>
              <li>
                <strong>Correction:</strong> Update or correct inaccurate information
              </li>
              <li>
                <strong>Deletion:</strong> Request deletion of your account and data
              </li>
              <li>
                <strong>Export:</strong> Export your lead data in a standard format
              </li>
              <li>
                <strong>Opt-Out:</strong> Unsubscribe from marketing communications
              </li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-slate-900">8. Data Retention</h2>
            <p className="mt-2 text-slate-600">
              We retain your data for as long as your account is active or as needed to provide the Service. If you
              delete your account, we will delete your personal information within 30 days, except where we are required
              to retain it for legal purposes.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-slate-900">9. Cookies and Tracking</h2>
            <p className="mt-2 text-slate-600">
              We use cookies and similar technologies to maintain your session, remember your preferences, and analyze
              Service usage. You can control cookies through your browser settings, but this may affect Service
              functionality.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-slate-900">10. Children's Privacy</h2>
            <p className="mt-2 text-slate-600">
              Our Service is not intended for children under 13 years of age. We do not knowingly collect personal
              information from children under 13.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-slate-900">11. International Data Transfers</h2>
            <p className="mt-2 text-slate-600">
              Your information may be transferred to and processed in countries other than your country of residence.
              We ensure appropriate safeguards are in place to protect your data in accordance with this Privacy Policy.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-slate-900">12. Changes to This Privacy Policy</h2>
            <p className="mt-2 text-slate-600">
              We may update this Privacy Policy from time to time. We will notify you of any changes by posting the new
              Privacy Policy on this page and updating the "Last updated" date.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-slate-900">13. Contact Us</h2>
            <p className="mt-2 text-slate-600">
              If you have any questions about this Privacy Policy, please contact us at:
            </p>
            <ul className="ml-6 mt-2 list-disc text-slate-600">
              <li>Email: privacy@leadscoreai.com</li>
              <li>Support: support@leadscoreai.com</li>
            </ul>
          </section>
        </div>
      </main>
    </div>
  );
}


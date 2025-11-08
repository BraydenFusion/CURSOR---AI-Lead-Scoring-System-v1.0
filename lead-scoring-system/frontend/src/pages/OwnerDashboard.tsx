import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { apiClient } from "../services/api";
import { WelcomeWalkthrough } from "../components/WelcomeWalkthrough";
import { DashboardLayout } from "../components/layout/DashboardLayout";

interface RepPerformance {
  rep: {
    id: string;
    name: string;
    email: string;
  };
  total_leads: number;
  hot_leads: number;
  average_score: number;
  conversion_rate: number;
}

interface RecentLead {
  id: string;
  name: string;
  email: string;
  score: number;
  classification: string;
  status: string;
  source: string;
  created_by: string | null;
  created_at: string;
}

interface DashboardData {
  owner: {
    id: string;
    name: string;
    email: string;
  };
  system_statistics: {
    total_users: number;
    sales_reps: number;
    managers: number;
    total_leads: number;
    hot_leads: number;
    warm_leads: number;
    cold_leads: number;
    average_score: number;
    status_breakdown: Record<string, number>;
    source_breakdown: Record<string, number>;
  };
  top_performers: RepPerformance[];
  recent_leads: RecentLead[];
}

export function OwnerDashboard() {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [showWalkthrough, setShowWalkthrough] = useState(false);

  useEffect(() => {
    loadDashboard();
    
    // Check if walkthrough should be shown (first-time user)
    const walkthroughCompleted = localStorage.getItem("walkthrough_completed");
    const walkthroughRole = localStorage.getItem("walkthrough_role");
    if (!walkthroughCompleted || walkthroughRole !== user?.role) {
      setShowWalkthrough(true);
    }
  }, []);

  const loadDashboard = async () => {
    try {
      const response = await apiClient.get("/dashboard/owner");
      setDashboardData(response.data);
    } catch (error) {
      console.error("Failed to load dashboard:", error);
    } finally {
      setLoading(false);
    }
  };

  const headerActions = (
    <Link
      to="/settings"
      className="inline-flex items-center gap-2 rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
      title="Settings"
    >
      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
        />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
      Settings
    </Link>
  );

  if (loading) {
    return (
      <DashboardLayout title="Owner Dashboard" subtitle="Complete System Overview & Analytics" actions={headerActions}>
        <div className="rounded-lg border border-slate-200 bg-white p-6 text-center text-slate-500 shadow-sm">
          Loading dashboard...
        </div>
      </DashboardLayout>
    );
  }

  const stats = dashboardData?.system_statistics;

  return (
    <DashboardLayout
      title="Owner Dashboard"
      subtitle="Complete System Overview & Analytics"
      actions={headerActions}
    >
      {showWalkthrough && user && (
        <WelcomeWalkthrough
          role={user.role as "sales_rep" | "manager" | "admin"}
          onComplete={() => setShowWalkthrough(false)}
        />
      )}
      {/* System Statistics */}
        <div className="mb-6 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4" data-walkthrough="system-stats">
          <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <div className="text-sm font-medium text-slate-600">Total Users</div>
            <div className="mt-2 text-3xl font-bold text-slate-900">{stats?.total_users || 0}</div>
            <div className="mt-1 text-xs text-slate-500">
              {stats?.sales_reps || 0} Reps, {stats?.managers || 0} Managers
            </div>
          </div>
          <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <div className="text-sm font-medium text-slate-600">Total Leads</div>
            <div className="mt-2 text-3xl font-bold text-slate-900">{stats?.total_leads || 0}</div>
          </div>
          <div className="rounded-lg border border-red-200 bg-red-50 p-6 shadow-sm">
            <div className="text-sm font-medium text-red-600">🔥 Hot Leads</div>
            <div className="mt-2 text-3xl font-bold text-red-900">{stats?.hot_leads || 0}</div>
          </div>
          <div className="rounded-lg border border-blue-200 bg-blue-50 p-6 shadow-sm">
          <div className="text-sm font-medium text-navy-600">Average Score</div>
          <div className="mt-2 text-3xl font-bold text-navy-900">{stats?.average_score.toFixed(1) || 0}/100</div>
          </div>
        </div>

        <div className="mb-6 grid grid-cols-1 gap-4 md:grid-cols-3">
          <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-6 shadow-sm">
            <div className="text-sm font-medium text-yellow-600">🟡 Warm Leads</div>
            <div className="mt-2 text-3xl font-bold text-yellow-900">{stats?.warm_leads || 0}</div>
          </div>
          <div className="rounded-lg border border-blue-200 bg-blue-50 p-6 shadow-sm">
            <div className="text-sm font-medium text-blue-600">🔵 Cold Leads</div>
            <div className="mt-2 text-3xl font-bold text-blue-900">{stats?.cold_leads || 0}</div>
          </div>
          <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <div className="text-sm font-medium text-slate-600">Hot Lead Rate</div>
            <div className="mt-2 text-3xl font-bold text-slate-900">
              {stats?.total_leads
                ? ((stats.hot_leads / stats.total_leads) * 100).toFixed(1)
                : 0}%
            </div>
          </div>
        </div>

        {/* Top Performers */}
        <div className="mb-6 rounded-lg border border-slate-200 bg-white shadow-sm" data-walkthrough="top-performers">
          <div className="border-b border-slate-200 px-6 py-4">
            <h2 className="text-xl font-bold text-slate-900">Top Performing Sales Reps</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-700">Rank</th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-700">Sales Rep</th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-700">Total Leads</th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-700">Hot Leads</th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-700">Avg Score</th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-700">Conversion Rate</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 bg-white">
                {dashboardData?.top_performers.map((rep, index) => (
                  <tr key={rep.rep.id} className="hover:bg-slate-50">
                    <td className="whitespace-nowrap px-6 py-4 text-sm font-bold text-slate-900">
                      #{index + 1}
                    </td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm font-medium text-slate-900">{rep.rep.name}</td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-600">{rep.total_leads}</td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm">
                      <span className="font-semibold text-red-600">{rep.hot_leads}</span>
                    </td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm">
                      <span className="font-bold text-navy-600">{rep.average_score.toFixed(1)}/100</span>
                    </td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm">
                      <span className="font-semibold text-green-600">{rep.conversion_rate.toFixed(1)}%</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {dashboardData?.top_performers.length === 0 && (
              <div className="px-6 py-12 text-center text-slate-500">No performance data yet.</div>
            )}
          </div>
        </div>

        {/* Source Breakdown */}
        {stats?.source_breakdown && Object.keys(stats.source_breakdown).length > 0 && (
          <div className="mb-6 rounded-lg border border-slate-200 bg-white p-6 shadow-sm" data-walkthrough="sources">
            <h2 className="mb-4 text-xl font-bold text-slate-900">Lead Sources</h2>
            <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
              {Object.entries(stats.source_breakdown).map(([source, count]) => (
                <div key={source} className="rounded-lg border border-slate-200 p-4">
                  <div className="text-sm font-medium text-slate-600 capitalize">{source}</div>
                  <div className="mt-1 text-2xl font-bold text-slate-900">{count}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Recent Leads */}
        <div className="rounded-lg border border-slate-200 bg-white shadow-sm">
          <div className="border-b border-slate-200 px-6 py-4">
            <h2 className="text-xl font-bold text-slate-900">Recent Leads</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-700">Name</th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-700">Email</th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-700">Score</th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-700">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-700">Source</th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-700">Created</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 bg-white">
                {dashboardData?.recent_leads.map((lead) => (
                  <tr key={lead.id} className="hover:bg-slate-50">
                    <td className="whitespace-nowrap px-6 py-4 text-sm font-medium text-slate-900">{lead.name}</td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-600">{lead.email}</td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm">
                      <span className={`font-bold ${lead.score >= 80 ? "text-red-600" : lead.score >= 50 ? "text-yellow-600" : "text-navy-600"}`}>
                        {lead.score}/100
                      </span>
                    </td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm">
                      <span
                        className={`inline-flex rounded-full px-2 py-1 text-xs font-semibold ${
                          lead.classification === "hot"
                            ? "bg-red-100 text-red-800"
                            : lead.classification === "warm"
                            ? "bg-yellow-100 text-yellow-800"
                            : "bg-blue-100 text-blue-800"
                        }`}
                      >
                        {lead.classification?.toUpperCase() || "N/A"}
                      </span>
                    </td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-600">{lead.source}</td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-500">
                      {new Date(lead.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {dashboardData?.recent_leads.length === 0 && (
              <div className="px-6 py-12 text-center text-slate-500">No recent leads.</div>
            )}
          </div>
        </div>
    </DashboardLayout>
  );
}


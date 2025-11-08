import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { apiClient } from "../services/api";
import { WelcomeWalkthrough } from "../components/WelcomeWalkthrough";
import { DashboardLayout } from "../components/layout/DashboardLayout";

interface RepStats {
  rep: {
    id: string;
    name: string;
    email: string;
    username: string;
  };
  statistics: {
    total_leads: number;
    hot_leads: number;
    warm_leads: number;
    cold_leads: number;
    average_score: number;
  };
}

interface DashboardData {
  manager: {
    id: string;
    name: string;
    email: string;
  };
  team_statistics: {
    total_sales_reps: number;
    total_leads: number;
    hot_leads: number;
    warm_leads: number;
    cold_leads: number;
    average_score: number;
  };
  sales_reps: RepStats[];
}

export function ManagerDashboard() {
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
      const response = await apiClient.get("/dashboard/manager");
      setDashboardData(response.data);
    } catch (error) {
      console.error("Failed to load dashboard:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <DashboardLayout title="Manager Dashboard" subtitle="Team Overview & Analytics">
        <div className="rounded-lg border border-slate-200 bg-white p-6 text-center text-slate-500 shadow-sm">
          Loading dashboard...
        </div>
      </DashboardLayout>
    );
  }

  const teamStats = dashboardData?.team_statistics;

  return (
    <DashboardLayout title="Manager Dashboard" subtitle="Team Overview & Analytics">
      {showWalkthrough && user && (
        <WelcomeWalkthrough
          role={user.role as "sales_rep" | "manager" | "admin"}
          onComplete={() => setShowWalkthrough(false)}
        />
      )}
      <div className="flex items-center justify-end pb-6">
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
      </div>

      {/* Team Statistics */}
        <div className="mb-6 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-5" data-walkthrough="team-stats">
          <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <div className="text-sm font-medium text-slate-600">Sales Reps</div>
            <div className="mt-2 text-3xl font-bold text-slate-900">{teamStats?.total_sales_reps || 0}</div>
          </div>
          <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <div className="text-sm font-medium text-slate-600">Total Leads</div>
            <div className="mt-2 text-3xl font-bold text-slate-900">{teamStats?.total_leads || 0}</div>
          </div>
          <div className="rounded-lg border border-red-200 bg-red-50 p-6 shadow-sm">
            <div className="text-sm font-medium text-red-600">🔥 Hot Leads</div>
            <div className="mt-2 text-3xl font-bold text-red-900">{teamStats?.hot_leads || 0}</div>
          </div>
          <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-6 shadow-sm">
            <div className="text-sm font-medium text-yellow-600">🟡 Warm Leads</div>
            <div className="mt-2 text-3xl font-bold text-yellow-900">{teamStats?.warm_leads || 0}</div>
          </div>
          <div className="rounded-lg border border-blue-200 bg-blue-50 p-6 shadow-sm">
            <div className="text-sm font-medium text-blue-600">🔵 Cold Leads</div>
            <div className="mt-2 text-3xl font-bold text-blue-900">{teamStats?.cold_leads || 0}</div>
          </div>
        </div>

        <div className="mb-6 rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <div className="text-2xl font-bold text-slate-900">Team Average Score</div>
          <div className="mt-2 text-4xl font-bold text-navy-600">{teamStats?.average_score.toFixed(1) || 0}/100</div>
        </div>

        {/* Sales Reps Overview */}
        <div className="rounded-lg border border-slate-200 bg-white shadow-sm" data-walkthrough="reps-table">
          <div className="border-b border-slate-200 px-6 py-4">
            <h2 className="text-xl font-bold text-slate-900">Sales Rep Performance</h2>
          </div>
          <div className="hidden overflow-x-auto md:block">
            <table className="w-full">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-700">
                    Sales Rep
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-700">
                    Email
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-700">
                    Total Leads
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-700">
                    Hot
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-700">
                    Warm
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-700">
                    Cold
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-700">
                    Avg Score
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 bg-white">
                {dashboardData?.sales_reps.map((rep) => (
                  <tr key={rep.rep.id} className="hover:bg-slate-50">
                    <td className="whitespace-nowrap px-6 py-4 text-sm font-medium text-slate-900">{rep.rep.name}</td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-600">{rep.rep.email}</td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-600">{rep.statistics.total_leads}</td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm">
                      <span className="font-semibold text-red-600">{rep.statistics.hot_leads}</span>
                    </td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm">
                      <span className="font-semibold text-yellow-600">{rep.statistics.warm_leads}</span>
                    </td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm">
                      <span className="font-semibold text-blue-600">{rep.statistics.cold_leads}</span>
                    </td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm">
                      <span className="font-bold text-navy-600">{rep.statistics.average_score.toFixed(1)}/100</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {dashboardData?.sales_reps.length === 0 && (
              <div className="px-6 py-12 text-center text-slate-500">No sales reps yet.</div>
            )}
          </div>

          <div className="block md:hidden">
            {dashboardData?.sales_reps.length === 0 ? (
              <div className="px-4 py-8 text-center text-slate-500">No sales reps yet.</div>
            ) : (
              <div className="space-y-4 p-4">
                {dashboardData?.sales_reps.map((rep) => (
                  <div key={rep.rep.id} className="rounded-lg border border-slate-200 p-4 shadow-sm">
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="text-base font-semibold text-slate-900">{rep.rep.name}</p>
                        <p className="text-sm text-slate-500">{rep.rep.email}</p>
                      </div>
                      <span className="rounded-full bg-navy-50 px-2 py-1 text-xs font-semibold text-navy-700">
                        {rep.statistics.average_score.toFixed(1)}/100
                      </span>
                    </div>
                    <div className="mt-4 grid grid-cols-2 gap-3 text-sm text-slate-600">
                      <div>
                        <p className="text-xs uppercase tracking-wide text-slate-400">Total Leads</p>
                        <p className="font-semibold text-slate-900">{rep.statistics.total_leads}</p>
                      </div>
                      <div>
                        <p className="text-xs uppercase tracking-wide text-slate-400">Hot Leads</p>
                        <p className="font-semibold text-red-600">{rep.statistics.hot_leads}</p>
                      </div>
                      <div>
                        <p className="text-xs uppercase tracking-wide text-slate-400">Warm Leads</p>
                        <p className="font-semibold text-yellow-600">{rep.statistics.warm_leads}</p>
                      </div>
                      <div>
                        <p className="text-xs uppercase tracking-wide text-slate-400">Cold Leads</p>
                        <p className="font-semibold text-blue-600">{rep.statistics.cold_leads}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
    </DashboardLayout>
  );
}


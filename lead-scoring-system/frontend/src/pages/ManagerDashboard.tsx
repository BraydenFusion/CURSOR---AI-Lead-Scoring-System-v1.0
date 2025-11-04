import { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { apiClient } from "../services/api";
import { NavBar } from "../components/NavBar";
import { WelcomeWalkthrough } from "../components/WelcomeWalkthrough";

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
      <div className="min-h-screen bg-slate-50">
        <NavBar />
        <div className="mx-auto max-w-7xl px-6 py-8">
          <div className="text-center">Loading dashboard...</div>
        </div>
      </div>
    );
  }

  const teamStats = dashboardData?.team_statistics;

  return (
    <div className="min-h-screen bg-slate-50">
      {showWalkthrough && user && (
        <WelcomeWalkthrough
          role={user.role as "sales_rep" | "manager" | "admin"}
          onComplete={() => setShowWalkthrough(false)}
        />
      )}
      <NavBar />
      <main className="mx-auto max-w-7xl px-6 py-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-slate-900">Manager Dashboard</h1>
          <p className="mt-1 text-slate-600">Team Overview & Analytics</p>
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
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-700">Sales Rep</th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-700">Email</th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-700">Total Leads</th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-700">Hot</th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-700">Warm</th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-700">Cold</th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-700">Avg Score</th>
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
        </div>
      </main>
    </div>
  );
}


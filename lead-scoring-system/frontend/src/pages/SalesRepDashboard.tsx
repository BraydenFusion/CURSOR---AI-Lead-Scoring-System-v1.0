import { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { apiClient } from "../services/api";
import { NavBar } from "../components/NavBar";
import { WelcomeWalkthrough } from "../components/WelcomeWalkthrough";

interface DashboardStats {
  total_leads: number;
  hot_leads: number;
  warm_leads: number;
  cold_leads: number;
  average_score: number;
  status_breakdown: Record<string, number>;
}

interface Lead {
  id: string;
  name: string;
  email: string;
  phone?: string;
  source: string;
  location?: string;
  score: number;
  classification: string;
  status: string;
  created_at: string;
  updated_at: string;
}

interface DashboardData {
  user: {
    id: string;
    name: string;
    email: string;
    role: string;
  };
  statistics: DashboardStats;
  recent_leads: Lead[];
}

export function SalesRepDashboard() {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [showUpload, setShowUpload] = useState(false);
  const [uploadType, setUploadType] = useState<"csv" | "individual">("csv");
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [uploadResult, setUploadResult] = useState<string | null>(null);
  const [showWalkthrough, setShowWalkthrough] = useState(false);
  const [individualForm, setIndividualForm] = useState({
    name: "",
    email: "",
    phone: "",
    source: "manual_entry",
    location: "",
  });

  useEffect(() => {
    loadDashboard();
    loadLeads();
    
    // Check if walkthrough should be shown (first-time user)
    const walkthroughCompleted = localStorage.getItem("walkthrough_completed");
    const walkthroughRole = localStorage.getItem("walkthrough_role");
    if (!walkthroughCompleted || walkthroughRole !== user?.role) {
      setShowWalkthrough(true);
    }
  }, []);

  const loadDashboard = async () => {
    try {
      const response = await apiClient.get("/dashboard/sales-rep");
      setDashboardData(response.data);
    } catch (error) {
      console.error("Failed to load dashboard:", error);
    } finally {
      setLoading(false);
    }
  };

  const loadLeads = async () => {
    try {
      const response = await apiClient.get("/dashboard/sales-rep/leads", {
        params: { page: 1, per_page: 50, sort: "score" },
      });
      setLeads(response.data.leads);
    } catch (error) {
      console.error("Failed to load leads:", error);
    }
  };

  const handleCsvUpload = async () => {
    if (!csvFile) return;

    setUploading(true);
    setUploadResult(null);

    try {
      const formData = new FormData();
      formData.append("file", csvFile);

      const response = await apiClient.post("/upload/csv", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setUploadResult(
        `✅ Successfully uploaded ${response.data.created} leads! ${response.data.errors > 0 ? `${response.data.errors} errors.` : ""}`
      );
      setCsvFile(null);
      setTimeout(() => {
        setShowUpload(false);
        loadDashboard();
        loadLeads();
      }, 2000);
    } catch (error: any) {
      setUploadResult(`❌ Upload failed: ${error.response?.data?.detail || error.message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleIndividualUpload = async () => {
    if (!individualForm.name || !individualForm.email) {
      setUploadResult("❌ Name and email are required");
      return;
    }

    setUploading(true);
    setUploadResult(null);

    try {
      await apiClient.post("/upload/individual", individualForm);
      setUploadResult("✅ Lead uploaded and AI-scored successfully!");
      setIndividualForm({
        name: "",
        email: "",
        phone: "",
        source: "manual_entry",
        location: "",
      });
      setTimeout(() => {
        setShowUpload(false);
        loadDashboard();
        loadLeads();
      }, 2000);
    } catch (error: any) {
      setUploadResult(`❌ Upload failed: ${error.response?.data?.detail || error.message}`);
    } finally {
      setUploading(false);
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

  const stats = dashboardData?.statistics;

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
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">My Dashboard</h1>
            <p className="mt-1 text-slate-600">Welcome back, {user?.full_name}</p>
          </div>
          <button
            onClick={() => setShowUpload(!showUpload)}
            data-walkthrough="upload-button"
            className="rounded-lg bg-navy-600 px-4 py-2 font-semibold text-white hover:bg-navy-700"
          >
            {showUpload ? "Cancel" : "+ Upload Leads"}
          </button>
        </div>

        {/* Upload Modal */}
        {showUpload && (
          <div className="mb-6 rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-4 flex gap-4">
              <button
                onClick={() => setUploadType("csv")}
                className={`rounded px-4 py-2 font-medium ${
                  uploadType === "csv"
                    ? "bg-blue-600 text-white"
                    : "bg-slate-100 text-slate-700 hover:bg-slate-200"
                }`}
              >
                CSV Upload
              </button>
              <button
                onClick={() => setUploadType("individual")}
                className={`rounded px-4 py-2 font-medium ${
                  uploadType === "individual"
                    ? "bg-blue-600 text-white"
                    : "bg-slate-100 text-slate-700 hover:bg-slate-200"
                }`}
              >
                Add Single Lead
              </button>
            </div>

            {uploadType === "csv" ? (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700">
                    CSV File (name, email, phone, source, location)
                  </label>
                  <input
                    type="file"
                    accept=".csv"
                    onChange={(e) => setCsvFile(e.target.files?.[0] || null)}
                    className="mt-1 block w-full text-sm text-slate-500 file:mr-4 file:rounded file:border-0 file:bg-blue-50 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-blue-700 hover:file:bg-blue-100"
                  />
                  <p className="mt-2 text-xs text-slate-500">
                    CSV format: name, email, phone (optional), source, location (optional)
                  </p>
                </div>
                <button
                  onClick={handleCsvUpload}
                  disabled={!csvFile || uploading}
                  className="rounded-lg bg-blue-600 px-4 py-2 font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
                >
                  {uploading ? "Uploading..." : "Upload CSV"}
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700">Name *</label>
                  <input
                    type="text"
                    value={individualForm.name}
                    onChange={(e) => setIndividualForm({ ...individualForm, name: e.target.value })}
                    className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700">Email *</label>
                  <input
                    type="email"
                    value={individualForm.email}
                    onChange={(e) => setIndividualForm({ ...individualForm, email: e.target.value })}
                    className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700">Phone</label>
                  <input
                    type="tel"
                    value={individualForm.phone}
                    onChange={(e) => setIndividualForm({ ...individualForm, phone: e.target.value })}
                    className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700">Source</label>
                  <input
                    type="text"
                    value={individualForm.source}
                    onChange={(e) => setIndividualForm({ ...individualForm, source: e.target.value })}
                    className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2"
                  />
                </div>
                <div className="col-span-2">
                  <label className="block text-sm font-medium text-slate-700">Location</label>
                  <input
                    type="text"
                    value={individualForm.location}
                    onChange={(e) => setIndividualForm({ ...individualForm, location: e.target.value })}
                    className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2"
                  />
                </div>
                <div className="col-span-2">
                  <button
                    onClick={handleIndividualUpload}
                    disabled={uploading}
                    className="rounded-lg bg-blue-600 px-4 py-2 font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
                  >
                    {uploading ? "Uploading..." : "Add Lead & AI Score"}
                  </button>
                </div>
              </div>
            )}

            {uploadResult && (
              <div className={`mt-4 rounded p-3 ${uploadResult.includes("✅") ? "bg-green-50 text-green-700" : "bg-red-50 text-red-700"}`}>
                {uploadResult}
              </div>
            )}
          </div>
        )}

        {/* Statistics Cards */}
        <div className="mb-6 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4" data-walkthrough="stats">
          <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <div className="text-sm font-medium text-slate-600">Total Leads</div>
            <div className="mt-2 text-3xl font-bold text-slate-900">{stats?.total_leads || 0}</div>
          </div>
          <div className="rounded-lg border border-red-200 bg-red-50 p-6 shadow-sm">
            <div className="text-sm font-medium text-red-600">🔥 Hot Leads</div>
            <div className="mt-2 text-3xl font-bold text-red-900">{stats?.hot_leads || 0}</div>
          </div>
          <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-6 shadow-sm">
            <div className="text-sm font-medium text-yellow-600">🟡 Warm Leads</div>
            <div className="mt-2 text-3xl font-bold text-yellow-900">{stats?.warm_leads || 0}</div>
          </div>
          <div className="rounded-lg border border-blue-200 bg-blue-50 p-6 shadow-sm">
            <div className="text-sm font-medium text-blue-600">🔵 Cold Leads</div>
            <div className="mt-2 text-3xl font-bold text-blue-900">{stats?.cold_leads || 0}</div>
          </div>
        </div>

        <div className="mb-4 rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <div className="text-2xl font-bold text-slate-900">Average Score</div>
          <div className="mt-2 text-4xl font-bold text-navy-600">{stats?.average_score.toFixed(1) || 0}/100</div>
        </div>

        {/* Leads Table */}
        <div className="rounded-lg border border-slate-200 bg-white shadow-sm" data-walkthrough="leads-table">
          <div className="border-b border-slate-200 px-6 py-4">
            <h2 className="text-xl font-bold text-slate-900">My Leads</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-700">Name</th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-700">Email</th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-700">Phone</th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-700">Score</th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-700">Classification</th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-700">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-700">Source</th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-700">Created</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 bg-white">
                {leads.map((lead) => (
                  <tr key={lead.id} className="hover:bg-slate-50">
                    <td className="whitespace-nowrap px-6 py-4 text-sm font-medium text-slate-900">{lead.name}</td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-600">{lead.email}</td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-600">{lead.phone || "-"}</td>
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
                    <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-600 capitalize">{lead.status}</td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-600">{lead.source}</td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-500">
                      {new Date(lead.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {leads.length === 0 && (
              <div className="px-6 py-12 text-center text-slate-500">No leads yet. Upload some leads to get started!</div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}


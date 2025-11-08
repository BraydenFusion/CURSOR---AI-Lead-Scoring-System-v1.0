import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import apiClient from "../services/api";
import { DashboardLayout } from "../components/layout/DashboardLayout";

interface Assignment {
  id: string;
  lead_id: string;
  lead_name: string;
  lead_email: string;
  lead_score: number;
  assigned_at: string;
  status: string;
}

export function MyLeadsPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [statusFilter, setStatusFilter] = useState("active");

  const { data: assignments, isLoading } = useQuery({
    queryKey: ["my-leads", statusFilter],
    queryFn: async () => {
      const response = await apiClient.get(`/assignments/my-leads?status=${statusFilter}`);
      return response.data;
    },
  });

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-red-600";
    if (score >= 50) return "text-yellow-600";
    return "text-blue-600";
  };

  const getClassificationBadge = (score: number) => {
    if (score >= 80) return <Badge className="bg-red-500">HOT</Badge>;
    if (score >= 50) return <Badge className="bg-yellow-500">WARM</Badge>;
    return <Badge className="bg-blue-500">COLD</Badge>;
  };

  if (isLoading) {
    return (
      <DashboardLayout title="My Assigned Leads" subtitle={user ? `${user.full_name} • ${user.role}` : undefined}>
        <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex animate-pulse flex-col gap-4">
            <div className="h-8 w-1/3 rounded bg-slate-200" />
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="rounded-lg border border-slate-200 bg-white p-4 shadow-inner">
                  <div className="h-5 w-2/3 rounded bg-slate-200" />
                  <div className="mt-3 h-4 w-full rounded bg-slate-100" />
                  <div className="mt-6 h-8 w-1/4 rounded bg-slate-200" />
                </div>
              ))}
            </div>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title="My Assigned Leads" subtitle={user ? `${user.full_name} • ${user.role}` : undefined}>
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm text-slate-500">
          Track every lead assigned to you and jump back into conversations in seconds.
        </p>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-[200px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="active">Active</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
            <SelectItem value="all">All</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {assignments?.length === 0 ? (
        <Card>
          <CardContent className="p-6">
            <p className="text-center text-gray-500">No leads assigned yet</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {assignments?.map((assignment: Assignment) => (
            <Card
              key={assignment.id}
              className="cursor-pointer transition-shadow hover:shadow-lg"
              onClick={() => navigate(`/leads/${assignment.lead_id}`)}
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <CardTitle className="text-lg">{assignment.lead_name}</CardTitle>
                  {getClassificationBadge(assignment.lead_score)}
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <p className="text-sm text-gray-600">{assignment.lead_email}</p>
                  <div className="mt-4 flex items-center justify-between">
                    <span className="text-sm font-medium text-slate-500">Score</span>
                    <span className={`text-3xl font-bold ${getScoreColor(assignment.lead_score)}`}>
                      {assignment.lead_score}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500">
                    Assigned {new Date(assignment.assigned_at).toLocaleDateString()}
                  </p>
                  <p className="text-xs uppercase tracking-wide text-slate-400">
                    Status: <span className="font-medium text-slate-600">{assignment.status}</span>
                  </p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </DashboardLayout>
  );
}


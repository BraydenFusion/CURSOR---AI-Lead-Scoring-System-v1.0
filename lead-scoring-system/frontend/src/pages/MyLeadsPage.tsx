import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { NavBar } from "../components/NavBar";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import apiClient from "../services/api";

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
      <div className="min-h-screen bg-gray-50">
        <NavBar />
        <div className="container mx-auto p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-gray-200 rounded w-1/4"></div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="rounded-lg border bg-white p-4 shadow-sm">
                  <div className="h-6 bg-gray-200 rounded w-2/3 mb-2"></div>
                  <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
                  <div className="h-8 bg-gray-200 rounded w-1/4 mt-4"></div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <NavBar />

      <div className="container mx-auto p-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">My Assigned Leads</h1>

          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-[180px]">
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
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {assignments?.map((assignment: Assignment) => (
              <Card
                key={assignment.id}
                className="cursor-pointer hover:shadow-lg transition-shadow"
                onClick={() => navigate(`/leads/${assignment.lead_id}`)}
              >
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <CardTitle className="text-lg">{assignment.lead_name}</CardTitle>
                    {getClassificationBadge(assignment.lead_score)}
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <p className="text-sm text-gray-600">{assignment.lead_email}</p>
                    <div className="flex items-center justify-between mt-4">
                      <span className="text-sm font-medium">Score:</span>
                      <span className={`text-3xl font-bold ${getScoreColor(assignment.lead_score)}`}>
                        {assignment.lead_score}
                      </span>
                    </div>
                    <p className="text-xs text-gray-500">
                      Assigned: {new Date(assignment.assigned_at).toLocaleDateString()}
                    </p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}


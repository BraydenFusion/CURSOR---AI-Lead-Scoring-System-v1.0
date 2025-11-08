import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { DashboardLayout } from "../components/layout/DashboardLayout";
import { AIInsightsPanel } from "../components/leads/AIInsightsPanel";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Textarea } from "../components/ui/textarea";
import apiClient from "../services/api";

interface Note {
  id: string;
  content: string;
  note_type: string;
  user_name: string;
  created_at: string;
}

interface Activity {
  id: string;
  activity_type: string;
  timestamp: string;
}

export function LeadDetailPage() {
  const { leadId } = useParams<{ leadId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [newNote, setNewNote] = useState("");
  const [noteType, setNoteType] = useState("general");
  const [activeTab, setActiveTab] = useState<"overview" | "ai">("overview");

  const { data: lead } = useQuery({
    queryKey: ["lead", leadId],
    queryFn: async () => {
      const response = await apiClient.get(`/leads/${leadId}`);
      return response.data;
    },
  });

  const { data: notes } = useQuery({
    queryKey: ["notes", leadId],
    queryFn: async () => {
      const response = await apiClient.get(`/notes/${leadId}`);
      return response.data;
    },
  });

  const { data: activities } = useQuery({
    queryKey: ["activities", leadId],
    queryFn: async () => {
      const response = await apiClient.get(`/leads/${leadId}/activities`);
      return response.data;
    },
  });

  const addNoteMutation = useMutation({
    mutationFn: async (data: { lead_id: string; content: string; note_type: string }) => {
      const response = await apiClient.post("/notes/", data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notes", leadId] });
      setNewNote("");
    },
  });

  const updateStatusMutation = useMutation({
    mutationFn: async (status: string) => {
      const response = await apiClient.put(`/leads/${leadId}/status`, { status });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["lead", leadId] });
    },
  });

  const handleAddNote = () => {
    if (!leadId || !newNote.trim()) {
      return;
    }

    addNoteMutation.mutate({
      lead_id: leadId,
      content: newNote,
      note_type: noteType,
    });
  };

  const headerActions = (
    <Button variant="outline" onClick={() => navigate(-1)}>
      Back to Leads
    </Button>
  );

  if (!lead) {
    return (
      <DashboardLayout title="Lead Detail" actions={headerActions}>
        <div className="animate-pulse space-y-6">
          <div className="rounded-lg border bg-white p-6 shadow-sm">
            <div className="mb-4 h-8 w-1/3 rounded bg-slate-200" />
            <div className="h-4 w-1/2 rounded bg-slate-100" />
          </div>
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <div className="rounded-lg border bg-white p-6 shadow-sm">
              <div className="mb-4 h-6 w-1/4 rounded bg-slate-200" />
              <div className="space-y-3">
                <div className="h-4 rounded bg-slate-100" />
                <div className="h-4 rounded bg-slate-100" />
              </div>
            </div>
            <div className="rounded-lg border bg-white p-6 shadow-sm">
              <div className="mb-4 h-6 w-1/4 rounded bg-slate-200" />
              <div className="space-y-3">
                <div className="h-4 rounded bg-slate-100" />
                <div className="h-4 rounded bg-slate-100" />
              </div>
            </div>
          </div>
        </div>
      </DashboardLayout>
    );
  }

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

  return (
    <DashboardLayout title={lead.name} subtitle={lead.email} actions={headerActions}>
      <div className="mb-6 flex items-center gap-2">
        <Button
          variant={activeTab === "overview" ? "default" : "outline"}
          size="sm"
          onClick={() => setActiveTab("overview")}
        >
          Overview
        </Button>
        <Button
          variant={activeTab === "ai" ? "default" : "outline"}
          size="sm"
          onClick={() => setActiveTab("ai")}
        >
          AI Insights
        </Button>
      </div>

      {activeTab === "ai" && leadId ? (
        <AIInsightsPanel leadId={leadId} leadName={lead.name} />
      ) : (
        <>
          <Card className="mb-6">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-2xl">{lead.name}</CardTitle>
                  <p className="text-gray-600">{lead.email}</p>
                  {lead.phone && <p className="text-gray-600">{lead.phone}</p>}
                </div>
                <div className="text-right">
                  <div className={`mb-2 text-4xl font-bold ${getScoreColor(lead.current_score)}`}>
                    {lead.current_score}
                  </div>
                  {getClassificationBadge(lead.current_score)}
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Source</p>
                  <p className="font-medium">{lead.source}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Status</p>
                  <Select value={lead.status} onValueChange={(value) => updateStatusMutation.mutate(value)}>
                    <SelectTrigger className="w-[180px]">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="new">New</SelectItem>
                      <SelectItem value="contacted">Contacted</SelectItem>
                      <SelectItem value="qualified">Qualified</SelectItem>
                      <SelectItem value="proposal">Proposal</SelectItem>
                      <SelectItem value="negotiation">Negotiation</SelectItem>
                      <SelectItem value="won">Won</SelectItem>
                      <SelectItem value="lost">Lost</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Notes</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="mb-4 max-h-96 space-y-4 overflow-y-auto">
                  {notes?.length === 0 ? (
                    <p className="text-sm text-gray-500">No notes yet</p>
                  ) : (
                    notes?.map((note: Note) => (
                      <div key={note.id} className="border-l-4 border-blue-500 pl-4 py-2">
                        <p className="text-sm font-medium">{note.user_name}</p>
                        <p className="text-gray-700">{note.content}</p>
                        <p className="mt-1 text-xs text-gray-500">
                          {new Date(note.created_at).toLocaleString()}
                        </p>
                      </div>
                    ))
                  )}
                </div>
                <div className="space-y-2">
                  <Textarea
                    placeholder="Add a note..."
                    value={newNote}
                    onChange={(event) => setNewNote(event.target.value)}
                  />
                  <div className="flex items-center justify-between">
                    <Select value={noteType} onValueChange={setNoteType}>
                      <SelectTrigger className="w-[160px]">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="general">General</SelectItem>
                        <SelectItem value="call">Call</SelectItem>
                        <SelectItem value="email">Email</SelectItem>
                        <SelectItem value="meeting">Meeting</SelectItem>
                      </SelectContent>
                    </Select>
                    <Button onClick={handleAddNote} disabled={addNoteMutation.isPending}>
                      Add Note
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Recent Activities</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {activities?.length === 0 ? (
                    <p className="text-sm text-gray-500">No activities recorded</p>
                  ) : (
                    activities?.map((activity: Activity) => (
                      <div key={activity.id} className="rounded border border-slate-200 bg-white p-3">
                        <p className="text-sm font-semibold text-slate-700">
                          {activity.activity_type.replace("_", " ").toUpperCase()}
                        </p>
                        <p className="text-xs text-slate-500">
                          {new Date(activity.timestamp).toLocaleString()}
                        </p>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </>
      )}
    </DashboardLayout>
  );
}

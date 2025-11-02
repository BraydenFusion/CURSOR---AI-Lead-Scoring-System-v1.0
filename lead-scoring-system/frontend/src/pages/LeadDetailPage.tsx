import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { NavBar } from "../components/NavBar";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Textarea } from "../components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
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
    if (newNote.trim() && leadId) {
      addNoteMutation.mutate({
        lead_id: leadId,
        content: newNote,
        note_type: noteType,
      });
    }
  };

  if (!lead) {
    return (
      <div className="min-h-screen bg-gray-50">
        <NavBar />
        <div className="container mx-auto p-6">
          <div className="animate-pulse space-y-6">
            <div className="rounded-lg border bg-white p-6">
              <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="rounded-lg border bg-white p-6">
                <div className="h-6 bg-gray-200 rounded w-1/4 mb-4"></div>
                <div className="space-y-3">
                  <div className="h-4 bg-gray-200 rounded"></div>
                  <div className="h-4 bg-gray-200 rounded"></div>
                </div>
              </div>
              <div className="rounded-lg border bg-white p-6">
                <div className="h-6 bg-gray-200 rounded w-1/4 mb-4"></div>
                <div className="space-y-3">
                  <div className="h-4 bg-gray-200 rounded"></div>
                  <div className="h-4 bg-gray-200 rounded"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
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
    <div className="min-h-screen bg-gray-50">
      <NavBar />

      <div className="container mx-auto p-6">
        {/* Lead Header */}
        <Card className="mb-6">
          <CardHeader>
            <div className="flex justify-between items-start">
              <div>
                <CardTitle className="text-2xl">{lead.name}</CardTitle>
                <p className="text-gray-600">{lead.email}</p>
                {lead.phone && <p className="text-gray-600">{lead.phone}</p>}
              </div>
              <div className="text-right">
                <div className={`text-4xl font-bold mb-2 ${getScoreColor(lead.current_score)}`}>
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

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Notes Section */}
          <Card>
            <CardHeader>
              <CardTitle>Notes</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4 mb-4 max-h-96 overflow-y-auto">
                {notes?.length === 0 ? (
                  <p className="text-sm text-gray-500">No notes yet</p>
                ) : (
                  notes?.map((note: Note) => (
                    <div key={note.id} className="border-l-4 border-blue-500 pl-4 py-2">
                      <p className="text-sm font-medium">{note.user_name}</p>
                      <p className="text-gray-700">{note.content}</p>
                      <p className="text-xs text-gray-500 mt-1">{new Date(note.created_at).toLocaleString()}</p>
                    </div>
                  ))
                )}
              </div>

              <div className="space-y-2">
                <Select value={noteType} onValueChange={setNoteType}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="general">General Note</SelectItem>
                    <SelectItem value="call">Phone Call</SelectItem>
                    <SelectItem value="email">Email</SelectItem>
                    <SelectItem value="meeting">Meeting</SelectItem>
                  </SelectContent>
                </Select>

                <Textarea
                  value={newNote}
                  onChange={(e) => setNewNote(e.target.value)}
                  placeholder="Add a note..."
                  rows={3}
                />

                <Button onClick={handleAddNote} className="w-full" disabled={addNoteMutation.isPending}>
                  {addNoteMutation.isPending ? "Adding..." : "Add Note"}
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Activity Timeline */}
          <Card>
            <CardHeader>
              <CardTitle>Activity Timeline</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {activities?.length === 0 ? (
                  <p className="text-sm text-gray-500">No activities yet</p>
                ) : (
                  activities?.map((activity: Activity) => (
                    <div key={activity.id} className="flex items-start gap-3">
                      <div className="w-2 h-2 mt-2 rounded-full bg-blue-500" />
                      <div className="flex-1">
                        <p className="font-medium">{activity.activity_type}</p>
                        <p className="text-xs text-gray-500">{new Date(activity.timestamp).toLocaleString()}</p>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}


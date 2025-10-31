import axios from "axios";

import type {
  Activity,
  Lead,
  LeadListResponse,
  ScoreResponse,
} from "../types";

const baseURL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api";

export const apiClient = axios.create({
  baseURL,
  timeout: 10_000,
  headers: {
    "Content-Type": "application/json",
  },
});

export const leadsApi = {
  getLeads: async (params: {
    sort: "score" | "date" | "source";
    classification: "all" | "hot" | "warm" | "cold";
    page: number;
    per_page: number;
    search?: string;
  }): Promise<LeadListResponse> => {
    const queryParams = { ...params };
    if (!queryParams.search) {
      delete queryParams.search;
    }
    const response = await apiClient.get<LeadListResponse>("/leads", { params: queryParams });
    return response.data;
  },

  getLead: async (leadId: string): Promise<Lead> => {
    const response = await apiClient.get<Lead>(`/leads/${leadId}`);
    return response.data;
  },

  getLeadScore: async (leadId: string): Promise<ScoreResponse> => {
    const response = await apiClient.get<ScoreResponse>(`/leads/${leadId}/score`);
    return response.data;
  },

  createLead: async (payload: {
    name: string;
    email: string;
    phone?: string;
    source: string;
    location?: string;
  }): Promise<Lead> => {
    const response = await apiClient.post<Lead>("/leads", payload);
    return response.data;
  },

  getLeadActivities: async (leadId: string): Promise<Activity[]> => {
    const response = await apiClient.get<Activity[]>(`/leads/${leadId}/activities`);
    return response.data;
  },

  createActivity: async (payload: {
    lead_id: string;
    activity_type: string;
    timestamp?: string;
    metadata?: Record<string, unknown>;
  }): Promise<Activity> => {
    const response = await apiClient.post<Activity>(
      `/leads/${payload.lead_id}/activity`,
      payload
    );
    return response.data;
  },
};

export default apiClient;

import apiClient from "./api";

export type SavedReport = {
  id: number;
  name: string;
  description?: string | null;
  report_type: string;
  filters: Record<string, any>;
  metrics: string[];
  schedule?: string | null;
  created_at: string;
  last_run?: string | null;
};

export type ReportPayload = {
  name: string;
  description?: string;
  report_type: string;
  filters: Record<string, any>;
  metrics: string[];
  schedule?: string | null;
};

export type ReportRunResult = {
  report_id: number;
  generated_at: string;
  metrics: string[];
  data: Record<string, any>;
};

export const reportsService = {
  async createReport(payload: ReportPayload) {
    const response = await apiClient.post<SavedReport>("/reports", payload);
    return response.data;
  },

  async updateReport(id: number, payload: Partial<ReportPayload>) {
    const response = await apiClient.put<SavedReport>(`/reports/${id}`, payload);
    return response.data;
  },

  async listReports() {
    const response = await apiClient.get<SavedReport[]>("/reports");
    return response.data;
  },

  async getReport(id: number) {
    const response = await apiClient.get<SavedReport>(`/reports/${id}`);
    return response.data;
  },

  async deleteReport(id: number) {
    await apiClient.delete(`/reports/${id}`);
  },

  async runReport(id: number, filters?: Record<string, any>) {
    const response = await apiClient.post<ReportRunResult>(`/reports/${id}/run`, filters ? { filters } : undefined);
    return response.data;
  },

  async exportReport(id: number, format: "csv" | "pdf" | "xlsx") {
    const response = await apiClient.get(`/reports/${id}/export`, {
      params: { format },
      responseType: "blob",
    });
    return response;
  },
};



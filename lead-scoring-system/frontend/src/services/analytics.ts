import apiClient from "./api";

export type DateRangeOption = "7days" | "30days" | "90days" | "custom";

export type AnalyticsFilters = {
  dateRange: DateRangeOption;
  startDate?: string | null;
  endDate?: string | null;
  source?: string;
  repId?: string;
  status?: string;
};

function buildQueryString(filters: AnalyticsFilters): string {
  const params = new URLSearchParams();

  if (filters.dateRange === "custom") {
    if (filters.startDate) {
      params.set("start_date", filters.startDate);
    }
    if (filters.endDate) {
      params.set("end_date", filters.endDate);
    }
    params.set("period", "custom");
  } else {
    params.set("period", filters.dateRange);
  }

  if (filters.source && filters.source !== "all") {
    params.set("source", filters.source);
  }

  if (filters.repId && filters.repId !== "all") {
    params.set("rep_id", filters.repId);
  }

  if (filters.status && filters.status !== "all") {
    params.set("status", filters.status);
  }

  return params.toString();
}

export const analyticsService = {
  async getOverview(filters: AnalyticsFilters) {
    const query = buildQueryString(filters);
    const response = await apiClient.get(`/analytics/overview?${query}`);
    return response.data;
  },

  async getConversionFunnel(filters: AnalyticsFilters) {
    const query = buildQueryString(filters);
    const response = await apiClient.get(`/analytics/conversion-funnel?${query}`);
    return response.data;
  },

  async getLeadSources(filters: AnalyticsFilters) {
    const query = buildQueryString(filters);
    const response = await apiClient.get(`/analytics/lead-sources?${query}`);
    return response.data;
  },

  async getRepPerformance(filters: AnalyticsFilters) {
    const query = buildQueryString(filters);
    const response = await apiClient.get(`/analytics/rep-performance?${query}`);
    return response.data;
  },

  async getScoreDistribution(filters: AnalyticsFilters) {
    const query = buildQueryString(filters);
    const response = await apiClient.get(`/analytics/score-distribution?${query}`);
    return response.data;
  },

  async getTimeline(filters: AnalyticsFilters) {
    const query = buildQueryString(filters);
    const response = await apiClient.get(`/analytics/timeline?${query}`);
    return response.data;
  },
};



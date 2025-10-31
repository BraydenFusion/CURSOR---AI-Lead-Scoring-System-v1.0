import { useQuery } from "@tanstack/react-query";

import { apiClient } from "../services/api";
import type { LeadListResponse } from "../types";

const LEADS_QUERY_KEY = ["leads"];

async function fetchLeads() {
  const { data } = await apiClient.get<LeadListResponse>("/leads");
  return data;
}

export function useLeads() {
  return useQuery({ queryKey: LEADS_QUERY_KEY, queryFn: fetchLeads });
}

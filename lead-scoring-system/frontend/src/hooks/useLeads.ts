import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { leadsApi } from "../services/api";

export function useLeads(filters: {
  sort: "score" | "date" | "source";
  classification: "all" | "hot" | "warm" | "cold";
  page: number;
  per_page: number;
  search?: string;
}) {
  return useQuery({
    queryKey: [
      "leads",
      filters.sort,
      filters.classification,
      filters.page,
      filters.per_page,
      filters.search?.trim() ?? "",
    ],
    queryFn: () => leadsApi.getLeads(filters),
  });
}

export function useLead(leadId: string | null) {
  return useQuery({
    queryKey: ["lead", leadId],
    queryFn: () => leadsApi.getLead(leadId as string),
    enabled: !!leadId,
  });
}

export function useLeadScore(leadId: string | null) {
  return useQuery({
    queryKey: ["lead-score", leadId],
    queryFn: () => leadsApi.getLeadScore(leadId as string),
    enabled: !!leadId,
    staleTime: 30_000,
  });
}

export function useCreateActivity() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: leadsApi.createActivity,
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["leads"] });
      queryClient.invalidateQueries({ queryKey: ["lead", variables.lead_id] });
      queryClient.invalidateQueries({ queryKey: ["lead-score", variables.lead_id] });
    },
  });
}

import { useMemo, useState } from "react";

import { useLeads } from "../hooks/useLeads";
import type { Lead } from "../types";
import { LeadCard } from "./LeadCard";
import { LeadFilters } from "./LeadFilters";
import { ScoreBreakdown } from "./ScoreBreakdown";
import { Badge } from "./ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "./ui/table";

const INITIAL_FILTERS = {
  sort: "score" as const,
  classification: "all" as const,
  page: 1,
  per_page: 25,
  search: "",
};

export function LeadDashboard() {
  const [filters, setFilters] = useState(INITIAL_FILTERS);
  const [selectedLeadId, setSelectedLeadId] = useState<string | null>(null);
  const [isBreakdownOpen, setIsBreakdownOpen] = useState(false);

  const { data, isLoading, error } = useLeads(filters);

  const leads = data?.leads ?? [];

  const selectedLead = useMemo<Lead | null>(() => {
    if (!selectedLeadId) return null;
    return leads.find((lead) => lead.id === selectedLeadId) ?? null;
  }, [selectedLeadId, leads]);

  const handleSelectLead = (lead: Lead) => {
    setSelectedLeadId(lead.id);
    setIsBreakdownOpen(true);
  };

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold text-slate-900">Lead Dashboard</h1>
        <p className="text-sm text-slate-500">
          Monitor, filter, and prioritize incoming leads based on AI-driven scoring.
        </p>
      </div>

      <LeadFilters
        filters={filters}
        onFilterChange={(partial) =>
          setFilters((prev) => {
            const next = { ...prev, ...partial };
            if (partial.search !== undefined) {
              next.search = partial.search.trim();
            }
            next.page = 1;
            return next;
          })
        }
      />

      {isLoading && (
        <div className="rounded-lg border border-slate-200 bg-white p-6 text-sm text-slate-500 shadow-sm">
          Loading leads...
        </div>
      )}

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-sm text-red-600">
          Failed to load leads. Please try again.
        </div>
      )}

      {!isLoading && !error && (
        <div className="rounded-lg border border-slate-200 bg-white shadow-sm">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Source</TableHead>
                <TableHead>Score</TableHead>
                <TableHead>Classification</TableHead>
                <TableHead>Updated</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {leads.map((lead) => (
                <TableRow
                  key={lead.id}
                  className="cursor-pointer"
                  onClick={() => handleSelectLead(lead)}
                  data-state={lead.id === selectedLeadId ? "selected" : undefined}
                >
                  <TableCell className="font-medium text-slate-800">{lead.name}</TableCell>
                  <TableCell className="text-slate-600">{lead.source}</TableCell>
                  <TableCell className={scoreText(lead.classification)}>{lead.current_score}</TableCell>
                  <TableCell>
                    <Badge className={classificationBadge(lead.classification)}>
                      {lead.classification.toUpperCase()}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-xs text-slate-500">
                    {new Date(lead.updated_at).toLocaleDateString()}
                  </TableCell>
                </TableRow>
              ))}
              {leads.length === 0 && (
                <TableRow>
                  <TableCell colSpan={5} className="py-6 text-center text-sm text-slate-500">
                    No leads match the selected filters.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
      )}

      {selectedLead && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-slate-900">Selected Lead</h2>
          <LeadCard lead={selectedLead} onClick={() => setIsBreakdownOpen(true)} />
        </div>
      )}

      {leads.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-slate-900">Top Leads</h2>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {leads.slice(0, 3).map((lead) => (
              <LeadCard key={lead.id} lead={lead} onClick={() => handleSelectLead(lead)} />
            ))}
          </div>
        </div>
      )}

      <ScoreBreakdown
        leadId={selectedLead?.id ?? null}
        leadName={selectedLead?.name ?? ""}
        classification={selectedLead?.classification ?? "cold"}
        isOpen={isBreakdownOpen && !!selectedLead}
        onClose={() => setIsBreakdownOpen(false)}
      />
    </div>
  );
}

function scoreText(classification: Lead["classification"]) {
  switch (classification) {
    case "hot":
      return "text-red-600 font-semibold";
    case "warm":
      return "text-yellow-600 font-semibold";
    case "cold":
    default:
      return "text-blue-600 font-semibold";
  }
}

function classificationBadge(classification: Lead["classification"]) {
  switch (classification) {
    case "hot":
      return "bg-red-500/10 text-red-600";
    case "warm":
      return "bg-yellow-500/10 text-yellow-600";
    case "cold":
    default:
      return "bg-blue-500/10 text-blue-600";
  }
}

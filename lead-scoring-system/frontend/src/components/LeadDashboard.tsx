import { useLeads } from "../hooks/useLeads";
import { LeadCard } from "./LeadCard";
import { LeadFilters } from "./LeadFilters";

export function LeadDashboard() {
  const { data, isLoading, error } = useLeads();

  if (isLoading) {
    return <div>Loading leads...</div>;
  }

  if (error) {
    return <div className="text-red-500">Failed to load leads.</div>;
  }

  return (
    <div className="space-y-6">
      <LeadFilters />
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {data?.items.map((lead) => (
          <LeadCard key={lead.id} lead={lead} />
        ))}
      </div>
    </div>
  );
}

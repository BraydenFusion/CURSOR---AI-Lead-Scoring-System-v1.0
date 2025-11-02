import { useLeads } from "../hooks/useLeads";
import { LeadCard } from "./LeadCard";
import { LeadFilters } from "./LeadFilters";
import { LoadingSkeleton } from "./LoadingSkeleton";

export function LeadDashboard() {
  const { data, isLoading, error } = useLeads();

  if (isLoading) {
    return <LoadingSkeleton />;
  }

  if (error) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">
        <p className="font-semibold">Failed to load leads</p>
        <p className="text-sm mt-1">
          {error instanceof Error ? error.message : "An unexpected error occurred. Please try again."}
        </p>
        <button
          onClick={() => window.location.reload()}
          className="mt-3 text-sm underline hover:no-underline"
        >
          Refresh page
        </button>
      </div>
    );
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

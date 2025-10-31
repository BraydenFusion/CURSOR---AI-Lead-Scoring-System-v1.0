import { useState } from "react";

import { ScoreBreakdown } from "./ScoreBreakdown";
import type { Lead } from "../types";

type LeadCardProps = {
  lead: Lead;
};

export function LeadCard({ lead }: LeadCardProps) {
  const [open, setOpen] = useState(false);

  const badgeColor =
    lead.classification === "hot"
      ? "bg-hot"
      : lead.classification === "warm"
        ? "bg-warm"
        : "bg-cold";

  return (
    <div className="rounded-lg border bg-white p-4 shadow-sm">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">{lead.name}</h3>
          <p className="text-sm text-slate-500">{lead.email}</p>
        </div>
        <div className="text-3xl font-bold text-slate-900">{lead.current_score}</div>
      </div>
      <div className="mt-3 flex items-center justify-between">
        <span className={`rounded-full px-3 py-1 text-xs font-medium text-white ${badgeColor}`}>
          {lead.classification?.toUpperCase() ?? "UNCATEGORIZED"}
        </span>
        <button className="text-sm text-blue-600" onClick={() => setOpen(true)}>
          View details
        </button>
      </div>

      <ScoreBreakdown lead={lead} open={open} onOpenChange={setOpen} />
    </div>
  );
}

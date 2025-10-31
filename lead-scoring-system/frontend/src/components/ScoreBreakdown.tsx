import { useEffect } from "react";

import type { Lead, ScoreDetails } from "../types";

type ScoreBreakdownProps = {
  lead: Lead;
  open: boolean;
  onOpenChange: (open: boolean) => void;
};

export function ScoreBreakdown({ lead, open, onOpenChange }: ScoreBreakdownProps) {
  useEffect(() => {
    if (!open) {
      return;
    }
    // Placeholder for future data fetching
  }, [open]);

  const breakdown = lead.score_breakdown ?? { engagement: 0, buying_signals: 0, demographic_fit: 0 };

  return open ? (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="w-full max-w-lg rounded-lg bg-white p-6 shadow-lg">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">Score Breakdown</h2>
          <button onClick={() => onOpenChange(false)} className="text-sm text-slate-500">
            Close
          </button>
        </div>
        <div className="mt-4 space-y-3">
          <BreakdownRow label="Engagement" value={breakdown.engagement} max={40} />
          <BreakdownRow label="Buying Signals" value={breakdown.buying_signals} max={40} />
          <BreakdownRow label="Demographic Fit" value={breakdown.demographic_fit} max={20} />
        </div>
      </div>
    </div>
  ) : null;
}

function BreakdownRow({ label, value, max }: { label: string; value: number; max: number }) {
  const percentage = Math.min(100, Math.round((value / max) * 100));

  return (
    <div>
      <div className="flex justify-between text-sm font-medium">
        <span>{label}</span>
        <span>
          {value}/{max}
        </span>
      </div>
      <div className="mt-1 h-2 rounded-full bg-slate-200">
        <div className="h-2 rounded-full bg-blue-500" style={{ width: `${percentage}%` }} />
      </div>
    </div>
  );
}

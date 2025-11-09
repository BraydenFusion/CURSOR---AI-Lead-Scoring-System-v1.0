import { useMemo, useState } from "react";
import { Cloud, CloudOff } from "lucide-react";

import { ScoreBreakdown } from "./ScoreBreakdown";
import type { Lead } from "../types";

type LeadCardProps = {
  lead: Lead;
};

export function LeadCard({ lead }: LeadCardProps) {
  const [open, setOpen] = useState(false);
  const crmStatus = useMemo(() => {
    const metadata = (lead.metadata as Record<string, any> | undefined) ?? {};
    const crmSync = (metadata.crm_sync as Record<string, Record<string, unknown>> | undefined) ?? {};
    return Object.entries(crmSync).map(([provider, info]) => {
      const status = (info?.status as string) ?? "unknown";
      const lastSync = (info?.last_sync as string) ?? null;
      return {
        provider,
        status,
        lastSync,
        title: `${provider.toUpperCase()} • ${status}${lastSync ? ` • ${new Date(lastSync).toLocaleString()}` : ""}`,
      };
    });
  }, [lead.metadata]);

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
          <div className="flex items-center gap-3">
            {crmStatus.length > 0 ? (
              <div className="flex gap-2">
                {crmStatus.map((item) => {
                  const Icon = item.status === "success" ? Cloud : CloudOff;
                  return (
                    <Icon
                      key={item.provider}
                      className={`h-4 w-4 ${item.status === "success" ? "text-emerald-500" : "text-slate-400"}`}
                      title={item.title}
                    />
                  );
                })}
              </div>
            ) : null}
            <div className="text-3xl font-bold text-slate-900">{lead.current_score}</div>
          </div>
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

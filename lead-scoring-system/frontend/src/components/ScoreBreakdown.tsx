import { Fragment } from "react";

import { useLeadScore } from "../hooks/useLeads";
import type { Factor } from "../types";
import { Badge } from "./ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "./ui/dialog";

type ScoreBreakdownProps = {
  leadId: string | null;
  leadName: string;
  classification: string;
  isOpen: boolean;
  onClose: () => void;
};

export function ScoreBreakdown({ leadId, leadName, classification, isOpen, onClose }: ScoreBreakdownProps) {
  const { data, isLoading } = useLeadScore(isOpen ? leadId : null);

  return (
    <Dialog
      open={isOpen}
      onOpenChange={(open) => {
        if (!open) onClose();
      }}
    >
      <DialogContent className="max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between gap-4">
            <span>Score Breakdown</span>
            {data && (
              <div className="flex items-center gap-2">
                <span className="text-3xl font-bold text-slate-900">{data.total_score}</span>
                <Badge className={classificationBadge(classification)}>
                  {classification.toUpperCase()}
                </Badge>
              </div>
            )}
          </DialogTitle>
          <DialogDescription>
            Detailed scoring factors for {leadName}
          </DialogDescription>
        </DialogHeader>

        {isLoading && <p className="py-6 text-sm text-slate-500">Loading score data...</p>}

        {data && (
          <div className="space-y-6">
            <CategoryBreakdown
              title="Engagement Signals"
              value={data.breakdown.engagement}
              max={40}
              variant="blue"
              factors={data.details.engagement_factors}
            />
            <CategoryBreakdown
              title="Buying Signals"
              value={data.breakdown.buying_signals}
              max={40}
              variant="green"
              factors={data.details.buying_factors}
            />
            <CategoryBreakdown
              title="Demographic Fit"
              value={data.breakdown.demographic_fit}
              max={20}
              variant="purple"
              factors={data.details.demographic_factors}
            />
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}

function CategoryBreakdown({
  title,
  value,
  max,
  variant,
  factors,
}: {
  title: string;
  value: number;
  max: number;
  variant: "blue" | "green" | "purple";
  factors: Factor[];
}) {
  const percentage = Math.round((value / max) * 100);
  const barColor = {
    blue: "bg-blue-500",
    green: "bg-green-500",
    purple: "bg-purple-500",
  }[variant];

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between text-sm font-semibold text-slate-700">
        <span>
          {title} ({value}/{max})
        </span>
        <span>{percentage}%</span>
      </div>
      <div className="h-2 rounded-full bg-slate-200">
        <div className={`h-2 rounded-full ${barColor}`} style={{ width: `${Math.min(percentage, 100)}%` }} />
      </div>
      <div className="space-y-2">
        {factors.map((factor, index) => (
          <Fragment key={`${factor.name}-${index}`}>
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-600">
                {factor.name}: <span className="font-medium text-slate-800">{factor.value}</span>
              </span>
              <span className="text-sm font-semibold text-slate-700">
                {factor.points}/{factor.max_points} pts
              </span>
            </div>
          </Fragment>
        ))}
      </div>
    </div>
  );
}

function classificationBadge(status: string) {
  switch (status) {
    case "hot":
      return "bg-red-500/10 text-red-600";
    case "warm":
      return "bg-yellow-500/10 text-yellow-600";
    case "cold":
    default:
      return "bg-blue-500/10 text-blue-600";
  }
}

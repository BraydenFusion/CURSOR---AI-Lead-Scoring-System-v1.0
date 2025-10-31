import type { Lead } from "../types";
import { cn } from "../lib/utils";
import { Badge } from "./ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";

interface LeadCardProps {
  lead: Lead;
  onClick?: () => void;
}

const classificationStyles: Record<Lead["classification"], string> = {
  hot: "bg-red-500/10 text-red-600",
  warm: "bg-yellow-500/10 text-yellow-600",
  cold: "bg-blue-500/10 text-blue-600",
};

const scoreStyles: Record<Lead["classification"], string> = {
  hot: "text-red-600",
  warm: "text-yellow-600",
  cold: "text-blue-600",
};

export function LeadCard({ lead, onClick }: LeadCardProps) {
  return (
    <Card
      className={cn("cursor-pointer transition-shadow hover:shadow-lg", onClick && "")}
      onClick={onClick}
    >
      <CardHeader className="space-y-2">
        <div className="flex items-start justify-between">
          <CardTitle className="text-lg font-semibold text-slate-900">
            {lead.name}
          </CardTitle>
          <Badge className={classificationStyles[lead.classification]}>
            {lead.classification.toUpperCase()}
          </Badge>
        </div>
        <p className="text-sm text-slate-500">{lead.email}</p>
        {lead.phone && <p className="text-sm text-slate-400">{lead.phone}</p>}
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-slate-600">Source</span>
          <span className="text-sm font-semibold text-slate-800">{lead.source}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-slate-600">Score</span>
          <span className={cn("text-3xl font-bold", scoreStyles[lead.classification])}>
            {lead.current_score}
          </span>
        </div>
        <p className="text-xs text-slate-400">
          Last updated {new Date(lead.updated_at).toLocaleString()}
        </p>
      </CardContent>
    </Card>
  );
}

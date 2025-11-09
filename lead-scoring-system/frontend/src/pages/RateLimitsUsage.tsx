import { useQuery } from "@tanstack/react-query";
import { formatDistanceToNow } from "date-fns";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { AlertTriangle, BarChart2 } from "lucide-react";

import { listApiKeyUsage } from "../services/developers";
import { APIKeyUsage } from "../types";

function formatTimestamp(value: string) {
  try {
    return new Date(value).toLocaleTimeString();
  } catch {
    return value;
  }
}

export function RateLimitsUsagePage() {
  const usageQuery = useQuery<APIKeyUsage[]>({
    queryKey: ["apiKeyUsage"],
    queryFn: listApiKeyUsage,
  });

  return (
    <div className="space-y-6">
      <header className="flex flex-col gap-2">
        <h1 className="text-2xl font-semibold text-slate-900">Rate Limits & Usage</h1>
        <p className="text-sm text-slate-500">
          Monitor API consumption per key. Limits reset every hour unless configured otherwise.
        </p>
      </header>

      <section className="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-3">
        {usageQuery.isLoading && (
          <div className="col-span-full rounded-lg border border-slate-200 bg-white p-6 text-center text-sm text-slate-500 shadow-sm">
            Loading usage statistics…
          </div>
        )}
        {usageQuery.data?.length === 0 && !usageQuery.isLoading && (
          <div className="col-span-full rounded-lg border border-slate-200 bg-white p-6 text-center text-sm text-slate-500 shadow-sm">
            No API usage recorded yet.
          </div>
        )}
        {usageQuery.data?.map((usage) => {
          const resetDate = new Date(usage.reset_epoch * 1000);
          const chartData = usage.samples.map((sample) => ({
            time: formatTimestamp(sample.timestamp),
            requests: sample.requests,
          }));
          const used = usage.hourly_limit - usage.remaining;
          const usagePercent = Math.min(Math.round((used / usage.hourly_limit) * 100), 100);

          return (
            <div key={usage.key_id} className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-sm font-semibold text-slate-900">Key {usage.key_preview}</h2>
                  <p className="text-xs text-slate-500">Hourly limit: {usage.hourly_limit.toLocaleString()} requests</p>
                </div>
                <div
                  className={`inline-flex items-center gap-2 rounded-full px-2.5 py-1 text-xs font-semibold ${
                    usagePercent >= 80 ? "bg-amber-100 text-amber-700" : "bg-emerald-100 text-emerald-700"
                  }`}
                >
                  <BarChart2 className="h-3.5 w-3.5" />
                  {usagePercent}% used
                </div>
              </div>

              <div className="mt-4">
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-semibold text-slate-900">{used.toLocaleString()}</span>
                  <span className="text-sm text-slate-500">requests this hour</span>
                </div>
                <p className="mt-1 text-xs text-slate-500">
                  Remaining: <span className="font-medium text-slate-700">{usage.remaining.toLocaleString()}</span>
                </p>
                <p className="mt-1 text-xs text-slate-500">
                  Resets {formatDistanceToNow(resetDate, { addSuffix: true })}
                </p>
              </div>

              {usagePercent >= 80 && (
                <div className="mt-3 flex items-center gap-2 rounded-md bg-amber-50 px-3 py-2 text-xs text-amber-700">
                  <AlertTriangle className="h-4 w-4" />
                  Approaching rate limit. Consider slowing down requests or increasing the limit.
                </div>
              )}

              <div className="mt-4 h-40">
                {chartData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={chartData}>
                      <defs>
                        <linearGradient id={`usage-${usage.key_id}`} x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#0284c7" stopOpacity={0.4} />
                          <stop offset="95%" stopColor="#0284c7" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                      <XAxis dataKey="time" tick={{ fontSize: 10, fill: "#64748b" }} />
                      <YAxis tick={{ fontSize: 10, fill: "#64748b" }} width={40} />
                      <Tooltip />
                      <Area
                        type="monotone"
                        dataKey="requests"
                        stroke="#0284c7"
                        fillOpacity={1}
                        fill={`url(#usage-${usage.key_id})`}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex h-full items-center justify-center text-xs text-slate-500">
                    No request history in this window.
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </section>
    </div>
  );
}


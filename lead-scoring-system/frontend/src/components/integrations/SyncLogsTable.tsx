import { useMemo } from "react";
import { Button } from "../ui/button";
import type { CRMSyncLog } from "../../types";

type SyncLogsTableProps = {
  logs: CRMSyncLog[];
  onExport: () => void;
  onSelectConflicts?: (log: CRMSyncLog) => void;
};

export function SyncLogsTable({ logs, onExport, onSelectConflicts }: SyncLogsTableProps) {
  const hasLogs = logs.length > 0;
  const csvContent = useMemo(() => {
    if (!hasLogs) return "";
    const rows = [
      ["Date", "Provider", "Direction", "Records", "Status", "Errors"].join(","),
      ...logs.map((log) =>
        [
          new Date(log.sync_started).toISOString(),
          log.provider,
          log.direction,
          log.records_synced,
          log.status,
          JSON.stringify(log.errors ?? []),
        ]
          .map((cell) => `"${String(cell).replace(/"/g, '""')}"`)
          .join(","),
      ),
    ];
    return rows.join("\n");
  }, [logs, hasLogs]);

  const handleExport = () => {
    if (!csvContent) return;
    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `crm-sync-logs-${Date.now()}.csv`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    onExport();
  };

  return (
    <div className="space-y-3 rounded-lg border bg-white p-4 shadow-sm">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">CRM Sync History</h3>
          <p className="text-sm text-muted-foreground">
            Review the most recent synchronization runs across Salesforce and HubSpot.
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={handleExport} disabled={!hasLogs}>
          Export CSV
        </Button>
      </div>

      {!hasLogs ? (
        <p className="text-sm text-muted-foreground">No CRM syncs have been recorded yet.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead>
              <tr className="border-b bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
                <th className="px-3 py-2">Date</th>
                <th className="px-3 py-2">Provider</th>
                <th className="px-3 py-2">Direction</th>
                <th className="px-3 py-2">Records</th>
                <th className="px-3 py-2">Status</th>
                <th className="px-3 py-2">Errors</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <tr key={log.id} className="border-b last:border-0">
                  <td className="px-3 py-2 text-slate-700">
                    {new Date(log.sync_started).toLocaleString()}
                  </td>
                  <td className="px-3 py-2 font-medium capitalize text-slate-700">{log.provider}</td>
                  <td className="px-3 py-2 capitalize text-slate-600">{log.direction.replace("_", " ")}</td>
                  <td className="px-3 py-2 text-slate-700">{log.records_synced}</td>
                  <td
                    className={`px-3 py-2 font-semibold ${
                      log.status === "success"
                        ? "text-emerald-600"
                        : log.status === "failed"
                          ? "text-red-600"
                          : "text-amber-600"
                    }`}
                  >
                    {log.status.toUpperCase()}
                  </td>
                  <td className="px-3 py-2 text-slate-600">
                    {log.errors && log.errors.length > 0 ? (
                      <Button
                        variant="link"
                        size="sm"
                        onClick={() => onSelectConflicts?.(log)}
                        className="px-0 text-amber-600"
                      >
                        View ({log.errors.length})
                      </Button>
                    ) : (
                      <span className="text-xs text-slate-400">None</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}


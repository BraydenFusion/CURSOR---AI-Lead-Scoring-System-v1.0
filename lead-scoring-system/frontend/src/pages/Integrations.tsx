import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import {
  Mail,
  RefreshCw,
  ShieldCheck,
  ToggleLeft,
  ToggleRight,
  Cloud,
  CloudCog,
} from "lucide-react";

import { Button } from "../components/ui/button";
import { Card } from "../components/ui/card";
import { Input } from "../components/ui/input";
import {
  EmailAccount,
  EmailProvider,
  CRMIntegration,
  CRMFieldMappingEntry,
  CRMSyncLog,
  CRMSyncDirection,
  CRMSyncFrequency,
} from "../types";
import {
  connectGmail,
  connectOutlook,
  disconnectGmail,
  disconnectOutlook,
  listEmailAccounts,
  manualSync,
  toggleAutoSync,
  connectPipedriveIntegration,
  fetchCRMIntegrations,
  fetchCRMSyncLogs,
  fetchPipedriveStatus,
  triggerPipedriveSync,
  resolveCRMConflicts,
} from "../services/integrations";
import { FieldMappingBuilder } from "../components/integrations/FieldMappingBuilder";
import { SyncLogsTable } from "../components/integrations/SyncLogsTable";

const providerLabels: Record<EmailProvider, string> = {
  gmail: "Gmail",
  outlook: "Outlook",
};

const providerDescriptions: Record<EmailProvider, string> = {
  gmail: "Sync conversations from your Google Workspace or Gmail account.",
  outlook: "Sync conversations from your Microsoft 365 or Outlook account.",
};

const CRM_LOCAL_FIELDS = ["name", "email", "phone", "source", "location"];
const PIPEDRIVE_REMOTE_FIELDS = ["name", "email", "phone", "organization", "status"];

const DEFAULT_PIPEDRIVE_MAPPING: CRMFieldMappingEntry[] = [
  { local_field: "name", remote_field: "name" },
  { local_field: "email", remote_field: "email" },
  { local_field: "phone", remote_field: "phone" },
  { local_field: "source", remote_field: "status" },
];

const directionOptions: { value: CRMSyncDirection; label: string }[] = [
  { value: "to_crm", label: "Push to CRM" },
  { value: "from_crm", label: "Pull from CRM" },
  { value: "bidirectional", label: "Bidirectional" },
];

const frequencyOptions: { value: CRMSyncFrequency; label: string }[] = [
  { value: "manual", label: "Manual" },
  { value: "hourly", label: "Hourly" },
  { value: "daily", label: "Daily" },
];

const conflictOptions = [
  { value: "manual", label: "Manual Review" },
  { value: "prefer_local", label: "Prefer Our Data" },
  { value: "prefer_crm", label: "Prefer CRM Data" },
];

function formatDate(value?: string | null) {
  if (!value) return "Never";
  return new Date(value).toLocaleString();
}

const IntegrationsPage = () => {
  const queryClient = useQueryClient();
  const [isSyncing, setIsSyncing] = useState<EmailProvider | "all" | "pipedrive" | null>(null);

  // Email integration queries
  const { data: accounts = [], isLoading: isLoadingEmails } = useQuery({
    queryKey: ["emailAccounts"],
    queryFn: listEmailAccounts,
  });

  // CRM integration queries
  const { data: crmIntegrations = [] } = useQuery({
    queryKey: ["crmIntegrations"],
    queryFn: fetchCRMIntegrations,
  });

  const { data: pipedriveStatus } = useQuery({
    queryKey: ["crmStatus", "pipedrive"],
    queryFn: fetchPipedriveStatus,
  });

  const { data: crmLogs = [] } = useQuery({
    queryKey: ["crmLogs"],
    queryFn: () => fetchCRMSyncLogs(50),
  });

  const gmailAccount = useMemo(
    () => accounts.find((account) => account.provider === "gmail"),
    [accounts],
  );
  const outlookAccount = useMemo(
    () => accounts.find((account) => account.provider === "outlook"),
    [accounts],
  );

  const pipedriveIntegration = useMemo(
    () => crmIntegrations.find((integration) => integration.provider === "pipedrive"),
    [crmIntegrations],
  );

  const [pipedriveCredentials, setPipedriveCredentials] = useState({
    api_token: "",
    base_url: "",
  });
  const [pipedriveDirection, setPipedriveDirection] = useState<CRMSyncDirection>("bidirectional");
  const [pipedriveFrequency, setPipedriveFrequency] = useState<CRMSyncFrequency>("hourly");
  const [pipedriveConflict, setPipedriveConflict] = useState<"manual" | "prefer_crm" | "prefer_local">("manual");
  const [pipedriveMappings, setPipedriveMappings] = useState<CRMFieldMappingEntry[]>(DEFAULT_PIPEDRIVE_MAPPING);

  useEffect(() => {
    if (pipedriveIntegration) {
      setPipedriveDirection(pipedriveIntegration.sync_direction);
      setPipedriveFrequency(pipedriveIntegration.sync_frequency);
      setPipedriveConflict(pipedriveIntegration.conflict_strategy as typeof pipedriveConflict);
      if (pipedriveIntegration.field_mappings?.length) {
        setPipedriveMappings(pipedriveIntegration.field_mappings);
      }
    }
  }, [pipedriveIntegration]);

  const connectEmailMutation = useMutation({
    mutationFn: async (provider: EmailProvider) => {
      if (provider === "gmail") {
        const data = await connectGmail();
        window.location.href = data.authorization_url;
      } else {
        const data = await connectOutlook();
        window.location.href = data.authorization_url;
      }
    },
  });

  const disconnectEmailMutation = useMutation({
    mutationFn: async (provider: EmailProvider) => {
      if (provider === "gmail") {
        await disconnectGmail();
      } else {
        await disconnectOutlook();
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["emailAccounts"] });
    },
  });

  const toggleEmailAutoSyncMutation = useMutation({
    mutationFn: ({ accountId, enabled }: { accountId: number; enabled: boolean }) =>
      toggleAutoSync(accountId, enabled),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["emailAccounts"] });
    },
  });

  const manualEmailSyncMutation = useMutation({
    mutationFn: async (provider: EmailProvider | "all") => {
      setIsSyncing(provider);
      try {
        return await manualSync(provider);
      } finally {
        setIsSyncing(null);
        queryClient.invalidateQueries({ queryKey: ["emailAccounts"] });
      }
    },
  });

  const connectPipedriveMutation = useMutation({
    mutationFn: connectPipedriveIntegration,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["crmIntegrations"] });
      queryClient.invalidateQueries({ queryKey: ["crmStatus", "pipedrive"] });
    },
  });

  const triggerPipedriveSyncMutation = useMutation({
    mutationFn: triggerPipedriveSync,
    onMutate: () => setIsSyncing("pipedrive"),
    onSettled: () => {
      setIsSyncing(null);
      queryClient.invalidateQueries({ queryKey: ["crmStatus", "pipedrive"] });
      queryClient.invalidateQueries({ queryKey: ["crmLogs"] });
    },
  });

  const resolveConflictsMutation = useMutation({
    mutationFn: ({ id, conflicts }: { id: number; conflicts: Parameters<typeof resolveCRMConflicts>[1] }) =>
      resolveCRMConflicts(id, conflicts),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["crmLogs"] });
      queryClient.invalidateQueries({ queryKey: ["crmStatus", "pipedrive"] });
    },
  });

  const [selectedLog, setSelectedLog] = useState<CRMSyncLog | null>(null);

  const handleConnectPipedrive = () => {
    connectPipedriveMutation.mutate({
      credentials: pipedriveCredentials,
      sync_direction: pipedriveDirection,
      sync_frequency: pipedriveFrequency,
      conflict_strategy: pipedriveConflict,
      field_mappings: pipedriveMappings,
    });
  };

  const handleResolveConflicts = (preferred_source: "local" | "remote") => {
    if (!selectedLog || !selectedLog.errors?.length) return;
    resolveConflictsMutation.mutate({
      id: selectedLog.integration_id,
      conflicts: selectedLog.errors.map((error) => ({
        record_id: String(error.record_id ?? ""),
        local_data: (error.local_data as Record<string, unknown>) ?? {},
        remote_data: (error.remote_data as Record<string, unknown>) ?? {},
        preferred_source,
      })),
    });
  };

  if (isLoadingEmails) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center text-muted-foreground">
        Loading integrations...
      </div>
    );
  }

  const renderEmailAccountCard = (provider: EmailProvider, account?: EmailAccount) => {
    const isConnected = Boolean(account);
    const toggleEnabled = account?.auto_sync_enabled ?? false;

    return (
      <Card className="flex flex-col gap-4 p-6">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-center gap-3">
            <Mail className="h-5 w-5 text-primary" />
            <div>
              <h3 className="text-lg font-semibold">{providerLabels[provider]}</h3>
              <p className="text-sm text-muted-foreground">{providerDescriptions[provider]}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span
              className={`rounded-full px-3 py-1 text-xs font-medium ${
                isConnected ? "bg-emerald-100 text-emerald-700" : "bg-slate-200 text-slate-600"
              }`}
            >
              {isConnected ? "Connected" : "Not connected"}
            </span>
          </div>
        </div>

        {isConnected ? (
          <div className="space-y-3 rounded-md bg-muted/60 p-4 text-sm">
            <div className="flex items-center justify-between">
              <span className="font-medium">Email</span>
              <span className="text-muted-foreground">{account?.email_address}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="font-medium">Connected</span>
              <span className="text-muted-foreground">{formatDate(account?.connected_at)}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="font-medium">Last sync</span>
              <span className="text-muted-foreground">{formatDate(account?.last_sync)}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="font-medium">Auto-sync</span>
              <button
                type="button"
                className="flex items-center gap-2 text-sm text-primary hover:text-primary/80"
                onClick={() =>
                  account &&
                  toggleEmailAutoSyncMutation.mutate({ accountId: account.id, enabled: !toggleEnabled })
                }
              >
                {toggleEnabled ? (
                  <>
                    <ToggleRight className="h-5 w-5" /> Enabled
                  </>
                ) : (
                  <>
                    <ToggleLeft className="h-5 w-5" /> Disabled
                  </>
                )}
              </button>
            </div>
          </div>
        ) : null}

        <div className="flex flex-wrap items-center justify-between gap-3">
          {isConnected ? (
            <Button
              variant="outline"
              onClick={() => disconnectEmailMutation.mutate(provider)}
              disabled={disconnectEmailMutation.isPending}
              className="border-red-200 text-red-600 hover:bg-red-50 hover:text-red-700"
            >
              Disconnect {providerLabels[provider]}
            </Button>
          ) : (
            <Button onClick={() => connectEmailMutation.mutate(provider)} disabled={connectEmailMutation.isPending}>
              Connect {providerLabels[provider]}
            </Button>
          )}
          {isConnected ? (
            <Button
              variant="outline"
              onClick={() => manualEmailSyncMutation.mutate(provider)}
              disabled={manualEmailSyncMutation.isPending && isSyncing !== provider}
            >
              <RefreshCw className={`mr-2 h-4 w-4 ${isSyncing === provider ? "animate-spin" : ""}`} />
              Manual Sync
            </Button>
          ) : null}
        </div>
      </Card>
    );
  };

  const renderPipedriveCard = () => {
    const connected = Boolean(pipedriveIntegration);
    const lastSync = pipedriveStatus?.integration?.last_sync ?? pipedriveIntegration?.last_sync ?? null;
    const lastLog = pipedriveStatus?.latest_log ?? null;
    const credentialFields: Array<{
      key: keyof typeof pipedriveCredentials;
      label: string;
      type: "password" | "text";
    }> = [
      { key: "api_token", label: "API Token", type: "password" },
      { key: "base_url", label: "Base URL (optional)", type: "text" },
    ];

    return (
      <Card className="space-y-5 p-6">
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <CloudCog className="h-5 w-5 text-primary" />
            <div>
              <h3 className="text-lg font-semibold">Pipedrive</h3>
              <p className="text-sm text-muted-foreground">
                Keep lead data synchronized with your Pipedrive workspace.
              </p>
            </div>
          </div>
          <span
            className={`rounded-full px-3 py-1 text-xs font-medium ${
              connected ? "bg-emerald-100 text-emerald-700" : "bg-slate-200 text-slate-600"
            }`}
          >
            {connected ? "Connected" : "Not connected"}
          </span>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-2">
            <label className="text-xs font-semibold uppercase text-slate-500">Sync Direction</label>
            <select
              className="w-full rounded border px-3 py-2 text-sm focus:border-primary focus:outline-none"
              value={pipedriveDirection}
              onChange={(event) => setPipedriveDirection(event.target.value as CRMSyncDirection)}
            >
              {directionOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          <div className="space-y-2">
            <label className="text-xs font-semibold uppercase text-slate-500">Sync Frequency</label>
            <select
              className="w-full rounded border px-3 py-2 text-sm focus:border-primary focus:outline-none"
              value={pipedriveFrequency}
              onChange={(event) => setPipedriveFrequency(event.target.value as CRMSyncFrequency)}
            >
              {frequencyOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          <div className="space-y-2">
            <label className="text-xs font-semibold uppercase text-slate-500">Conflict Strategy</label>
            <select
              className="w-full rounded border px-3 py-2 text-sm focus:border-primary focus:outline-none"
              value={pipedriveConflict}
              onChange={(event) =>
                setPipedriveConflict(event.target.value as "manual" | "prefer_crm" | "prefer_local")
              }
            >
              {conflictOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          <div className="space-y-2">
            <label className="text-xs font-semibold uppercase text-slate-500">Last Sync</label>
            <p className="rounded border px-3 py-2 text-sm text-slate-700">{formatDate(lastSync)}</p>
          </div>
        </div>

        <div className="grid gap-3 md:grid-cols-2">
          {credentialFields.map((field) => (
            <div key={field.key} className="space-y-1">
              <label className="text-xs font-semibold uppercase text-slate-500">{field.label}</label>
              <Input
                type={field.type}
                value={pipedriveCredentials[field.key] ?? ""}
                onChange={(event) => setPipedriveCredentials({ ...pipedriveCredentials, [field.key]: event.target.value })}
                placeholder={field.label}
              />
            </div>
          ))}
        </div>
        <p className="text-xs text-muted-foreground">
          Credentials are encrypted at rest. Updating settings requires valid credentials to refresh access tokens.
        </p>

        <FieldMappingBuilder
          title="Pipedrive Field Mapping"
          value={pipedriveMappings}
          onChange={setPipedriveMappings}
          localFields={CRM_LOCAL_FIELDS}
          remoteFields={PIPEDRIVE_REMOTE_FIELDS}
        />

        <div className="flex flex-wrap items-center justify-between gap-3">
          <Button onClick={handleConnectPipedrive} disabled={connectPipedriveMutation.isPending}>
            {connected ? "Update Connection" : "Connect Pipedrive"}
          </Button>
          <Button
            variant="outline"
            onClick={() => triggerPipedriveSyncMutation.mutate({ direction: pipedriveDirection })}
            disabled={triggerPipedriveSyncMutation.isPending}
          >
            <RefreshCw className={`mr-2 h-4 w-4 ${isSyncing === "pipedrive" ? "animate-spin" : ""}`} />
            Sync Now
          </Button>
        </div>

        {lastLog ? (
          <div className="rounded-md border bg-slate-50 p-3 text-xs">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-slate-600">Last sync result</span>
              <span
                className={`font-semibold ${
                  lastLog.status === "success"
                    ? "text-emerald-600"
                    : lastLog.status === "failed"
                      ? "text-red-600"
                      : "text-amber-600"
                }`}
              >
                {lastLog.status.toUpperCase()}
              </span>
            </div>
            <div className="mt-1 text-slate-600">
              {formatDate(lastLog.sync_started)} • {lastLog.records_synced} records • {lastLog.direction}
            </div>
            {lastLog.errors && lastLog.errors.length > 0 ? (
              <Button
                variant="ghost"
                size="sm"
                className="px-0 text-amber-600 hover:bg-transparent"
                onClick={() => setSelectedLog(lastLog)}
              >
                View conflicts ({lastLog.errors.length})
              </Button>
            ) : null}
          </div>
        ) : null}
      </Card>
    );
  };

  return (
    <div className="space-y-10">
      <header className="flex flex-col gap-2">
        <h1 className="text-2xl font-semibold tracking-tight">Integrations</h1>
        <p className="text-muted-foreground">
          Connect email inboxes and CRM systems to unify lead data and automate follow-ups.
        </p>
      </header>

      <section className="space-y-6">
        <h2 className="text-xl font-semibold">Email Accounts</h2>
        <div className="grid gap-6 lg:grid-cols-2">
          {renderEmailAccountCard("gmail", gmailAccount)}
          {renderEmailAccountCard("outlook", outlookAccount)}
        </div>
        <Card className="space-y-3 p-6">
          <div className="flex items-center gap-2">
            <RefreshCw className="h-5 w-5 text-primary" />
            <h3 className="text-lg font-semibold">Email Sync Settings</h3>
          </div>
          <p className="text-sm text-muted-foreground">
            Auto-sync runs every 15 minutes for connected accounts with auto-sync enabled. You can also trigger a sync
            manually at any time.
          </p>
          <div className="flex flex-wrap gap-3">
            <Button
              variant="outline"
              onClick={() => manualEmailSyncMutation.mutate("all")}
              disabled={manualEmailSyncMutation.isPending && isSyncing !== "all"}
            >
              <RefreshCw className={`mr-2 h-4 w-4 ${isSyncing === "all" ? "animate-spin" : ""}`} />
              Sync All Now
            </Button>
          </div>
          {manualEmailSyncMutation.data && manualEmailSyncMutation.data.processed >= 0 ? (
            <p className="text-xs text-muted-foreground">
              Last manual sync processed {manualEmailSyncMutation.data.processed} messages.
            </p>
          ) : null}
        </Card>
      </section>

      <section className="space-y-6">
        <h2 className="text-xl font-semibold">CRM Integrations</h2>
        <div className="grid gap-6 lg:grid-cols-1">
          {renderPipedriveCard()}
        </div>
      </section>

      <section className="space-y-4">
        <SyncLogsTable logs={crmLogs} onExport={() => void 0} onSelectConflicts={(log) => setSelectedLog(log)} />
      </section>

      {selectedLog && (
        <Card className="space-y-4 border-amber-300 bg-amber-50 p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-amber-700">Resolve Conflicts</h3>
              <p className="text-sm text-amber-700">
                Apply a resolution strategy to {selectedLog.errors?.length ?? 0} conflicting records from the{" "}
                {selectedLog.provider.toUpperCase()} sync on {formatDate(selectedLog.sync_started)}.
              </p>
            </div>
            <Button variant="ghost" onClick={() => setSelectedLog(null)}>
              Close
            </Button>
          </div>
          <div className="flex flex-wrap gap-3">
            <Button
              variant="outline"
              onClick={() => handleResolveConflicts("local")}
              disabled={resolveConflictsMutation.isPending}
            >
              Keep Our Data
            </Button>
            <Button
              variant="outline"
              onClick={() => handleResolveConflicts("remote")}
              disabled={resolveConflictsMutation.isPending}
            >
              Accept CRM Data
            </Button>
          </div>
          <pre className="overflow-x-auto rounded bg-white p-3 text-xs text-slate-700">
            {JSON.stringify(selectedLog.errors, null, 2)}
          </pre>
        </Card>
      )}

      <section className="grid gap-6 md:grid-cols-2">
        <Card className="space-y-4 p-6">
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-5 w-5 text-primary" />
            <h3 className="text-lg font-semibold">Email Matching Rules</h3>
          </div>
          <ul className="space-y-2 text-sm text-muted-foreground">
            <li>• Leads are matched by any email address found in the message participants.</li>
            <li>• Replies from leads automatically update engagement metrics (+5 points).</li>
            <li>• Opens and clicks contribute to scoring once tracking pixels are enabled.</li>
            <li>
              • Need help? Review our{" "}
              <Link to="/support/email-integrations" className="text-primary underline">
                email integration guide
              </Link>
              .
            </li>
          </ul>
        </Card>
        <Card className="space-y-4 p-6">
          <div className="flex items-center gap-2">
            <Cloud className="h-5 w-5 text-primary" />
            <h3 className="text-lg font-semibold">CRM Sync Tips</h3>
          </div>
          <ul className="space-y-2 text-sm text-muted-foreground">
            <li>• Use bidirectional sync to keep Pipedrive aligned with LeadScore AI.</li>
            <li>• Hourly syncing provides quick updates while respecting API rate limits.</li>
            <li>
              • Conflict resolution lets you choose whether our data or the CRM wins when changes collide.
            </li>
            <li>• Custom field mappings ensure both systems stay in the same format.</li>
          </ul>
        </Card>
      </section>
    </div>
  );
};

export default IntegrationsPage;

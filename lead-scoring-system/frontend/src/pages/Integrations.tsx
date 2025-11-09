import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { Mail, RefreshCw, ShieldCheck, ToggleLeft, ToggleRight } from "lucide-react";

import { Button } from "../components/ui/button";
import { Card } from "../components/ui/card";
import { EmailAccount, EmailProvider } from "../types";
import {
  connectGmail,
  connectOutlook,
  disconnectGmail,
  disconnectOutlook,
  listEmailAccounts,
  manualSync,
  toggleAutoSync,
} from "../services/integrations";

const providerLabels: Record<EmailProvider, string> = {
  gmail: "Gmail",
  outlook: "Outlook",
};

const providerDescriptions: Record<EmailProvider, string> = {
  gmail: "Sync conversations from your Google Workspace or Gmail account.",
  outlook: "Sync conversations from your Microsoft 365 or Outlook account.",
};

function formatDate(value?: string | null) {
  if (!value) return "Never";
  return new Date(value).toLocaleString();
}

const IntegrationsPage = () => {
  const queryClient = useQueryClient();
  const [isSyncing, setIsSyncing] = useState<EmailProvider | "all" | null>(null);

  const { data: accounts = [], isLoading } = useQuery({
    queryKey: ["emailAccounts"],
    queryFn: listEmailAccounts,
  });

  const gmailAccount = useMemo(
    () => accounts.find((account) => account.provider === "gmail"),
    [accounts]
  );
  const outlookAccount = useMemo(
    () => accounts.find((account) => account.provider === "outlook"),
    [accounts]
  );

  const connectMutation = useMutation({
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

  const disconnectMutation = useMutation({
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

  const toggleMutation = useMutation({
    mutationFn: ({ accountId, enabled }: { accountId: number; enabled: boolean }) =>
      toggleAutoSync(accountId, enabled),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["emailAccounts"] });
    },
  });

  const syncMutation = useMutation({
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

  if (isLoading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center text-muted-foreground">
        Loading integrations...
      </div>
    );
  }

  const renderAccountCard = (provider: EmailProvider, account?: EmailAccount) => {
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
                  toggleMutation.mutate({ accountId: account.id, enabled: !toggleEnabled })
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
              variant="secondary"
              onClick={() => disconnectMutation.mutate(provider)}
              disabled={disconnectMutation.isPending}
            >
              Disconnect {providerLabels[provider]}
            </Button>
          ) : (
            <Button
              onClick={() => connectMutation.mutate(provider)}
              disabled={connectMutation.isPending}
            >
              Connect {providerLabels[provider]}
            </Button>
          )}
          {isConnected ? (
            <Button
              variant="outline"
              onClick={() => syncMutation.mutate(provider)}
              disabled={syncMutation.isPending && isSyncing !== provider}
            >
              <RefreshCw
                className={`mr-2 h-4 w-4 ${isSyncing === provider ? "animate-spin" : ""}`}
              />
              Manual Sync
            </Button>
          ) : null}
        </div>
      </Card>
    );
  };

  return (
    <div className="space-y-8">
      <header className="flex flex-col gap-2">
        <h1 className="text-2xl font-semibold tracking-tight">Integrations</h1>
        <p className="text-muted-foreground">
          Connect your email accounts to track conversations with leads, sync engagement metrics,
          and send messages directly from the lead workspace.
        </p>
      </header>

      <section className="grid gap-6 lg:grid-cols-2">
        {renderAccountCard("gmail", gmailAccount)}
        {renderAccountCard("outlook", outlookAccount)}
      </section>

      <section className="grid gap-6 md:grid-cols-2">
        <Card className="space-y-3 p-6">
          <div className="flex items-center gap-2">
            <RefreshCw className="h-5 w-5 text-primary" />
            <h3 className="text-lg font-semibold">Email Sync Settings</h3>
          </div>
          <p className="text-sm text-muted-foreground">
            Auto-sync runs every 15 minutes for connected accounts with auto-sync enabled. You can
            also trigger a sync manually at any time.
          </p>
          <div className="flex flex-wrap gap-3">
            <Button
              variant="outline"
              onClick={() => syncMutation.mutate("all")}
              disabled={syncMutation.isPending && isSyncing !== "all"}
            >
              <RefreshCw className={`mr-2 h-4 w-4 ${isSyncing === "all" ? "animate-spin" : ""}`} />
              Sync All Now
            </Button>
          </div>
          {syncMutation.data && syncMutation.data.processed >= 0 ? (
            <p className="text-xs text-muted-foreground">
              Last manual sync processed {syncMutation.data.processed} messages.
            </p>
          ) : null}
        </Card>

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
      </section>
    </div>
  );
};

export default IntegrationsPage;

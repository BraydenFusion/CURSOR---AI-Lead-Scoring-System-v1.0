import apiClient from "./api";
import type {
  EmailAccount,
  EmailMessage,
  EmailSendPayload,
  EmailProvider,
  CRMIntegration,
  CRMSyncLog,
  CRMSyncStatusResponse,
  CRMFieldMappingEntry,
  CRMSyncDirection,
  CRMSyncFrequency,
  CRMConflictRecord,
} from "../types";

type OAuthConnectResponse = {
  authorization_url: string;
  state: string;
};

type ManualSyncResponse = {
  status: string;
  processed: number;
};

export type SalesforceConnectPayload = {
  credentials: {
    username: string;
    password: string;
    security_token: string;
    domain?: string;
  };
  sync_direction: CRMSyncDirection;
  sync_frequency: CRMSyncFrequency;
  field_mappings: CRMFieldMappingEntry[];
  conflict_strategy: "manual" | "prefer_crm" | "prefer_local";
};

export type HubSpotConnectPayload = {
  credentials: {
    access_token: string;
    refresh_token?: string;
    app_id?: string;
  };
  sync_direction: CRMSyncDirection;
  sync_frequency: CRMSyncFrequency;
  field_mappings: CRMFieldMappingEntry[];
  conflict_strategy: "manual" | "prefer_crm" | "prefer_local";
};

export type SyncTriggerPayload = {
  direction?: CRMSyncDirection;
  force_full_sync?: boolean;
};

export async function listEmailAccounts() {
  const { data } = await apiClient.get<EmailAccount[]>("/integrations/accounts");
  return data;
}

export async function connectGmail(): Promise<OAuthConnectResponse> {
  const { data } = await apiClient.get<OAuthConnectResponse>("/integrations/gmail/connect");
  return data;
}

export async function disconnectGmail() {
  await apiClient.post("/integrations/gmail/disconnect");
}

export async function connectOutlook(): Promise<OAuthConnectResponse> {
  const { data } = await apiClient.get<OAuthConnectResponse>("/integrations/outlook/connect");
  return data;
}

export async function disconnectOutlook() {
  await apiClient.post("/integrations/outlook/disconnect");
}

export async function toggleAutoSync(accountId: number, enabled: boolean) {
  const { data } = await apiClient.patch<EmailAccount>(
    `/integrations/accounts/${accountId}/auto-sync`,
    null,
    { params: { enabled } }
  );
  return data;
}

export async function manualSync(provider: EmailProvider | "all") {
  const { data } = await apiClient.post<ManualSyncResponse>(`/integrations/sync/${provider}`);
  return data;
}

export async function fetchLeadEmails(leadId: string) {
  const { data } = await apiClient.get<EmailMessage[]>(`/integrations/emails/${leadId}`);
  return data;
}

export async function sendEmail(payload: EmailSendPayload) {
  const { data } = await apiClient.post<EmailMessage>("/integrations/send-email", payload);
  return data;
}

export async function fetchCRMIntegrations() {
  const { data } = await apiClient.get<CRMIntegration[]>("/crm/integrations");
  return data;
}

export async function connectSalesforceIntegration(payload: SalesforceConnectPayload) {
  const { data } = await apiClient.post<CRMIntegration>("/crm/salesforce/connect", payload);
  return data;
}

export async function connectHubSpotIntegration(payload: HubSpotConnectPayload) {
  const { data } = await apiClient.post<CRMIntegration>("/crm/hubspot/connect", payload);
  return data;
}

export async function updateIntegrationDirection(integrationId: number, direction: CRMSyncDirection) {
  const { data } = await apiClient.patch<CRMIntegration>(`/crm/integrations/${integrationId}`, {
    direction,
  });
  return data;
}

export async function fetchSalesforceStatus() {
  const { data } = await apiClient.get<CRMSyncStatusResponse>("/crm/salesforce/status");
  return data;
}

export async function fetchHubSpotStatus() {
  const { data } = await apiClient.get<CRMSyncStatusResponse>("/crm/hubspot/status");
  return data;
}

export async function triggerSalesforceSync(payload: SyncTriggerPayload = {}) {
  const { data } = await apiClient.post<CRMSyncStatusResponse>("/crm/salesforce/sync", payload);
  return data;
}

export async function triggerHubSpotSync(payload: SyncTriggerPayload = {}) {
  const { data } = await apiClient.post<CRMSyncStatusResponse>("/crm/hubspot/sync", payload);
  return data;
}

export async function fetchCRMSyncLogs(limit = 50) {
  const { data } = await apiClient.get<CRMSyncLog[]>("/crm/sync-logs", { params: { limit } });
  return data;
}

export async function resolveCRMConflicts(integrationId: number, conflicts: CRMConflictRecord[]) {
  const { data } = await apiClient.post<{ applied: number }>(
    `/crm/integrations/${integrationId}/resolve-conflicts`,
    { conflicts },
  );
  return data;
}

import apiClient from "./api";
import type {
  EmailAccount,
  EmailMessage,
  EmailSendPayload,
  EmailProvider,
} from "../types";

type OAuthConnectResponse = {
  authorization_url: string;
  state: string;
};

type ManualSyncResponse = {
  status: string;
  processed: number;
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

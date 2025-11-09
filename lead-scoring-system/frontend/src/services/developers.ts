import apiClient from "./api";
import {
  APIKey,
  APIKeyListResponse,
  APIKeyPermission,
  APIKeySecretResponse,
  APIKeyUsage,
  Webhook,
  WebhookDeliveryListResponse,
  WebhookListResponse,
  WebhookSecretResponse,
  WebhookEvent,
} from "../types";

export type APIKeyCreatePayload = {
  name: string;
  permissions: APIKeyPermission[];
  rate_limit?: number;
};

export type APIKeyUpdatePayload = Partial<APIKeyCreatePayload> & {
  active?: boolean;
};

export async function fetchApiKeys(): Promise<APIKeyListResponse> {
  const { data } = await apiClient.get<APIKeyListResponse>("/api/api-keys");
  return data;
}

export async function createApiKey(payload: APIKeyCreatePayload): Promise<APIKeySecretResponse> {
  const { data } = await apiClient.post<APIKeySecretResponse>("/api/api-keys", {
    name: payload.name,
    permissions: payload.permissions,
    rate_limit: payload.rate_limit,
  });
  return data;
}

export async function updateApiKey(keyId: number, payload: APIKeyUpdatePayload): Promise<APIKey> {
  const { data } = await apiClient.put<APIKey>(`/api/api-keys/${keyId}`, payload);
  return data;
}

export async function revokeApiKey(keyId: number): Promise<APIKey> {
  const { data } = await apiClient.post<APIKey>(`/api/api-keys/${keyId}/revoke`);
  return data;
}

export async function deleteApiKey(keyId: number): Promise<void> {
  await apiClient.delete(`/api/api-keys/${keyId}`);
}

export async function getApiKeyUsage(keyId: number): Promise<APIKeyUsage> {
  const { data } = await apiClient.get<APIKeyUsage>(`/api/api-keys/${keyId}/usage`);
  return data;
}

export async function listApiKeyUsage(): Promise<APIKeyUsage[]> {
  const { data } = await apiClient.get<APIKeyUsage[]>("/api/api-keys/usage");
  return data;
}

export type WebhookPayload = {
  url: string;
  events: WebhookEvent[];
  secret?: string;
  active?: boolean;
};

export async function fetchWebhooks(): Promise<WebhookListResponse> {
  const { data } = await apiClient.get<WebhookListResponse>("/api/webhooks");
  return data;
}

export async function createWebhook(payload: WebhookPayload): Promise<WebhookSecretResponse> {
  const { data } = await apiClient.post<WebhookSecretResponse>("/api/webhooks", payload);
  return data;
}

export async function updateWebhook(webhookId: number, payload: WebhookPayload): Promise<Webhook> {
  const { data } = await apiClient.put<Webhook>(`/api/webhooks/${webhookId}`, payload);
  return data;
}

export async function deleteWebhook(webhookId: number): Promise<void> {
  await apiClient.delete(`/api/webhooks/${webhookId}`);
}

export async function testWebhook(webhookId: number, payload?: { event?: string; payload?: Record<string, unknown> }): Promise<Webhook> {
  const { data } = await apiClient.post<Webhook>(`/api/webhooks/${webhookId}/test`, payload ?? {});
  return data;
}

export async function fetchWebhookDeliveries(webhookId: number): Promise<WebhookDeliveryListResponse> {
  const { data } = await apiClient.get<WebhookDeliveryListResponse>(`/api/webhooks/${webhookId}/deliveries`);
  return data;
}


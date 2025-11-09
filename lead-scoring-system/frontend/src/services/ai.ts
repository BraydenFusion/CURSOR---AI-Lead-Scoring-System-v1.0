import apiClient from "./api";
import type {
  AIInsight,
  EmailTemplateRequestPayload,
  EmailTemplateResponsePayload,
  NextBestActionResponse,
} from "../types";

export async function fetchAIInsights(leadId: string) {
  const { data } = await apiClient.get<AIInsight>(`/ai/insights/${leadId}`);
  return data;
}

export async function fetchNextBestActions(leadId: string) {
  const { data } = await apiClient.post<NextBestActionResponse>(`/ai/next-best-action/${leadId}`);
  return data;
}

export async function generateEmailTemplate(payload: EmailTemplateRequestPayload) {
  const { data } = await apiClient.post<EmailTemplateResponsePayload>("/ai/email-template", payload);
  return data;
}

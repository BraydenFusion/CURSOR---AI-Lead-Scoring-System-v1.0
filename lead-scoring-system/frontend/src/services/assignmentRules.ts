import { apiClient } from "./api";
import type {
  AssignmentRule,
  AssignmentRuleApplyResult,
  AssignmentRuleTestResult,
  AssignmentRuleType,
  EligibleRep,
} from "../types";

export type AssignmentRulePayload = {
  name: string;
  description?: string | null;
  priority: number;
  active: boolean;
  rule_type: AssignmentRuleType;
  conditions: Record<string, unknown>;
  assignment_logic: Record<string, unknown>;
};

export type AssignmentRuleUpdatePayload = Partial<AssignmentRulePayload>;

export async function fetchAssignmentRules() {
  const { data } = await apiClient.get<AssignmentRule[]>("/assignment-rules");
  return data;
}

export async function fetchEligibleRepresentatives() {
  const { data } = await apiClient.get<EligibleRep[]>("/assignment-rules/eligible-reps");
  return data;
}

export async function createAssignmentRule(payload: AssignmentRulePayload) {
  const { data } = await apiClient.post<AssignmentRule>("/assignment-rules", payload);
  return data;
}

export async function updateAssignmentRule(ruleId: number, payload: AssignmentRuleUpdatePayload) {
  const { data } = await apiClient.put<AssignmentRule>(`/assignment-rules/${ruleId}`, payload);
  return data;
}

export async function deleteAssignmentRule(ruleId: number) {
  await apiClient.delete(`/assignment-rules/${ruleId}`);
}

export async function toggleAssignmentRule(ruleId: number, active: boolean) {
  const { data } = await apiClient.post<AssignmentRule>(`/assignment-rules/${ruleId}/toggle`, { active });
  return data;
}

export async function testAssignmentRule(ruleId: number, leadId: string) {
  const { data } = await apiClient.get<AssignmentRuleTestResult>(`/assignment-rules/${ruleId}/test`, {
    params: { lead_id: leadId },
  });
  return data;
}

export async function applyAssignmentRule(ruleId: number, leadId: string) {
  const { data } = await apiClient.post<AssignmentRuleApplyResult>(`/assignment-rules/${ruleId}/apply`, {
    lead_id: leadId,
  });
  return data;
}

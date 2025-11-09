export type Classification = "hot" | "warm" | "cold";

export type ScoreBreakdown = {
  engagement: number;
  buying_signals: number;
  demographic_fit: number;
};

export type Lead = {
  id: string;
  name: string;
  email: string;
  phone?: string | null;
  source: string;
  location?: string | null;
  current_score: number;
  classification: Classification;
  status?: string;
  created_at: string;
  updated_at: string;
  score_breakdown?: ScoreBreakdown;
  metadata?: Record<string, unknown>;
};

export type LeadListResponse = {
  items: Lead[];
  total: number;
  page: number;
  per_page: number;
};

export type ScoreDetails = {
  total_score: number;
  classification: Classification;
  breakdown: ScoreBreakdown;
  details: Record<string, number>;
};

export type AssignmentRuleType = "round_robin" | "territory" | "workload" | "score_based";

export type AssignmentRule = {
  id: number;
  name: string;
  description?: string | null;
  active: boolean;
  priority: number;
  rule_type: AssignmentRuleType;
  conditions: Record<string, unknown>;
  assignment_logic: Record<string, unknown>;
  created_by_id?: string | null;
  created_at: string;
  updated_at: string;
};

export type AssignmentRuleTestResult = {
  matches: boolean;
  rule_id?: number;
  lead_id?: string;
  assigned_user_id?: string | null;
  assigned_user_name?: string | null;
  reason?: string;
};

export type AssignmentRuleApplyResult = {
  success: boolean;
  assigned_user_id?: string | null;
  assigned_user_name?: string | null;
  message?: string | null;
};

export type EligibleRep = {
  id: string;
  full_name: string;
  email: string;
  active_assignments: number;
};

export type AIActionItem = {
  title: string;
  description: string;
  priority: number;
  time_estimate: string;
  done?: boolean;
};

export type AIConversionProbability = {
  level: "low" | "medium" | "high" | "unknown";
  confidence?: number | null;
  reasoning: string[];
  comparison_to_similar?: string | null;
};

export type AITalkingPoint = {
  title: string;
  details: string;
};

export type AIInsight = {
  lead_id: string;
  summary: string;
  summary_confidence?: number | null;
  recommended_actions: AIActionItem[];
  conversion_probability: AIConversionProbability;
  talking_points: AITalkingPoint[];
  generated_at: string;
  estimated_cost?: number | null;
};

export type EmailTemplateRequestPayload = {
  lead_id: string;
  email_type: "initial_outreach" | "follow_up" | "demo_invite" | "pricing_discussion";
};

export type EmailTemplateResponsePayload = {
  subject: string;
  body: string;
  call_to_action?: string | null;
  generated_at: string;
  estimated_cost?: number | null;
};

export type NextBestActionResponse = {
  lead_id: string;
  recommended_actions: AIActionItem[];
  generated_at: string;
};

export type EmailProvider = "gmail" | "outlook";

export type EmailAccount = {
  id: number;
  provider: EmailProvider;
  email_address: string;
  connected_at: string;
  last_sync?: string | null;
  auto_sync_enabled: boolean;
};

export type EmailMessage = {
  id: number;
  subject: string;
  sender: string;
  recipients: string[];
  body_text: string;
  sent_at: string;
  direction: "sent" | "received";
  read: boolean;
};

export type EmailSendPayload = {
  email_account_id: number;
  lead_id: string;
  subject: string;
  body: string;
  recipients?: string[];
};

export type CRMProvider = "salesforce" | "hubspot";
export type CRMSyncDirection = "to_crm" | "from_crm" | "bidirectional";
export type CRMSyncFrequency = "manual" | "hourly" | "daily";
export type CRMConflictStrategy = "manual" | "prefer_crm" | "prefer_local";
export type CRMSyncStatus = "running" | "success" | "partial" | "failed";

export type CRMFieldMappingEntry = {
  local_field: string;
  remote_field: string;
  transform?: string | null;
};

export type CRMIntegration = {
  id: number;
  provider: CRMProvider;
  sync_direction: CRMSyncDirection;
  sync_frequency: CRMSyncFrequency;
  field_mappings: CRMFieldMappingEntry[];
  conflict_strategy: CRMConflictStrategy;
  last_sync?: string | null;
  active: boolean;
  created_at: string;
  updated_at: string;
};

export type CRMSyncLog = {
  id: number;
  integration_id: number;
  sync_started: string;
  sync_completed?: string | null;
  records_synced: number;
  errors?: Array<Record<string, unknown>> | null;
  status: CRMSyncStatus;
  direction: CRMSyncDirection;
  provider: CRMProvider;
};

export type CRMConflictRecord = {
  record_id: string;
  local_data: Record<string, unknown>;
  remote_data: Record<string, unknown>;
  preferred_source: "local" | "remote";
};

export type CRMSyncStatusResponse = {
  integration: CRMIntegration | null;
  latest_log: CRMSyncLog | null;
};

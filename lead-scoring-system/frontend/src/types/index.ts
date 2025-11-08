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
  created_at: string;
  updated_at: string;
  score_breakdown?: ScoreBreakdown;
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

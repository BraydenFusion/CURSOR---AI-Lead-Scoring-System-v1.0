export type Classification = "hot" | "warm" | "cold";

export interface Lead {
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
  metadata?: Record<string, unknown>;
}

export interface LeadListResponse {
  leads: Lead[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface Activity {
  id: string;
  lead_id: string;
  activity_type: string;
  points_awarded: number;
  timestamp: string;
  metadata?: Record<string, unknown>;
}

export interface ScoreBreakdown {
  engagement: number;
  buying_signals: number;
  demographic_fit: number;
}

export interface Factor {
  name: string;
  value: string | number;
  points: number;
  max_points: number;
}

export interface ScoreDetails {
  engagement_factors: Factor[];
  buying_factors: Factor[];
  demographic_factors: Factor[];
}

export interface ScoreResponse {
  total_score: number;
  classification: Classification;
  breakdown: ScoreBreakdown;
  details: ScoreDetails;
}

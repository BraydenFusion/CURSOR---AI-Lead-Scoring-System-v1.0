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

-- Create enum type (drop first if exists)
DROP TYPE IF EXISTS lead_classification CASCADE;
CREATE TYPE lead_classification AS ENUM ('hot', 'warm', 'cold');

-- Create leads table
CREATE TABLE IF NOT EXISTS leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(50),
    source VARCHAR(100) NOT NULL,
    location VARCHAR(255),
    current_score INTEGER NOT NULL DEFAULT 0,
    classification lead_classification,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB NOT NULL DEFAULT '{}',
    CONSTRAINT chk_leads_score_range CHECK (current_score >= 0 AND current_score <= 100)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_leads_score ON leads(current_score DESC);
CREATE INDEX IF NOT EXISTS idx_leads_classification ON leads(classification);

-- Create lead_activities table
CREATE TABLE IF NOT EXISTS lead_activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    activity_type VARCHAR(100) NOT NULL,
    points_awarded INTEGER NOT NULL DEFAULT 0,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB NOT NULL DEFAULT '{}'
);

-- Create indexes for activities
CREATE INDEX IF NOT EXISTS idx_activities_lead_id ON lead_activities(lead_id);
CREATE INDEX IF NOT EXISTS idx_activities_timestamp ON lead_activities(timestamp DESC);

-- Create lead_scores_history table
CREATE TABLE IF NOT EXISTS lead_scores_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    old_score INTEGER,
    new_score INTEGER,
    old_classification VARCHAR(20),
    new_classification VARCHAR(20),
    trigger_activity_id UUID REFERENCES lead_activities(id),
    changed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create index for scores history
CREATE INDEX IF NOT EXISTS idx_scores_history_lead_id ON lead_scores_history(lead_id);


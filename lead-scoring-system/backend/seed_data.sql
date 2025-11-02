-- Clear existing data
TRUNCATE TABLE lead_scores_history, lead_activities, leads CASCADE;

-- Insert Lead 1: Jane Smith (HOT) - Score 92
INSERT INTO leads (id, name, email, source, location, current_score, classification, metadata) VALUES
('11111111-1111-1111-1111-111111111111', 'Jane Smith', 'jane@example.com', 'website', 'New York, NY', 92, 'hot', 
 '{"demographics": {"location_score": "same_city", "income_bracket": "high", "credit_score": "720+"}}'::jsonb);

-- Activities for Jane Smith
INSERT INTO lead_activities (id, lead_id, activity_type, points_awarded, metadata) VALUES
(gen_random_uuid(), '11111111-1111-1111-1111-111111111111', 'email_open', 0, '{}'::jsonb),
(gen_random_uuid(), '11111111-1111-1111-1111-111111111111', 'email_open', 0, '{}'::jsonb),
(gen_random_uuid(), '11111111-1111-1111-1111-111111111111', 'email_open', 0, '{}'::jsonb),
(gen_random_uuid(), '11111111-1111-1111-1111-111111111111', 'email_open', 0, '{}'::jsonb),
(gen_random_uuid(), '11111111-1111-1111-1111-111111111111', 'email_open', 0, '{}'::jsonb),
(gen_random_uuid(), '11111111-1111-1111-1111-111111111111', 'email_click', 0, '{}'::jsonb),
(gen_random_uuid(), '11111111-1111-1111-1111-111111111111', 'email_click', 0, '{}'::jsonb),
(gen_random_uuid(), '11111111-1111-1111-1111-111111111111', 'email_click', 0, '{}'::jsonb),
(gen_random_uuid(), '11111111-1111-1111-1111-111111111111', 'email_click', 0, '{}'::jsonb),
(gen_random_uuid(), '11111111-1111-1111-1111-111111111111', 'email_click', 0, '{}'::jsonb),
(gen_random_uuid(), '11111111-1111-1111-1111-111111111111', 'website_visit', 0, '{}'::jsonb),
(gen_random_uuid(), '11111111-1111-1111-1111-111111111111', 'website_visit', 0, '{}'::jsonb),
(gen_random_uuid(), '11111111-1111-1111-1111-111111111111', 'website_visit', 0, '{}'::jsonb),
(gen_random_uuid(), '11111111-1111-1111-1111-111111111111', 'website_visit', 0, '{}'::jsonb),
(gen_random_uuid(), '11111111-1111-1111-1111-111111111111', 'website_visit', 0, '{}'::jsonb),
(gen_random_uuid(), '11111111-1111-1111-1111-111111111111', 'pricing_page_view', 0, '{}'::jsonb),
(gen_random_uuid(), '11111111-1111-1111-1111-111111111111', 'pricing_page_view', 0, '{}'::jsonb),
(gen_random_uuid(), '11111111-1111-1111-1111-111111111111', 'pricing_page_view', 0, '{}'::jsonb),
(gen_random_uuid(), '11111111-1111-1111-1111-111111111111', 'pricing_page_view', 0, '{}'::jsonb),
(gen_random_uuid(), '11111111-1111-1111-1111-111111111111', 'pricing_page_view', 0, '{}'::jsonb),
(gen_random_uuid(), '11111111-1111-1111-1111-111111111111', 'test_drive_request', 0, '{}'::jsonb),
(gen_random_uuid(), '11111111-1111-1111-1111-111111111111', 'financing_calculator', 0, '{}'::jsonb),
(gen_random_uuid(), '11111111-1111-1111-1111-111111111111', 'financing_calculator', 0, '{}'::jsonb);

-- Insert Lead 2: Bob Johnson (WARM) - Score 67
INSERT INTO leads (id, name, email, source, location, current_score, classification, metadata) VALUES
('22222222-2222-2222-2222-222222222222', 'Bob Johnson', 'bob@example.com', 'referral', 'Boston, MA', 67, 'warm',
 '{"demographics": {"location_score": "nearby", "income_bracket": "medium", "credit_score": "650-719"}}'::jsonb);

-- Activities for Bob Johnson
INSERT INTO lead_activities (id, lead_id, activity_type, points_awarded, metadata) VALUES
(gen_random_uuid(), '22222222-2222-2222-2222-222222222222', 'email_open', 0, '{}'::jsonb),
(gen_random_uuid(), '22222222-2222-2222-2222-222222222222', 'email_open', 0, '{}'::jsonb),
(gen_random_uuid(), '22222222-2222-2222-2222-222222222222', 'email_open', 0, '{}'::jsonb),
(gen_random_uuid(), '22222222-2222-2222-2222-222222222222', 'email_click', 0, '{}'::jsonb),
(gen_random_uuid(), '22222222-2222-2222-2222-222222222222', 'email_click', 0, '{}'::jsonb),
(gen_random_uuid(), '22222222-2222-2222-2222-222222222222', 'email_click', 0, '{}'::jsonb),
(gen_random_uuid(), '22222222-2222-2222-2222-222222222222', 'website_visit', 0, '{}'::jsonb),
(gen_random_uuid(), '22222222-2222-2222-2222-222222222222', 'website_visit', 0, '{}'::jsonb),
(gen_random_uuid(), '22222222-2222-2222-2222-222222222222', 'website_visit', 0, '{}'::jsonb),
(gen_random_uuid(), '22222222-2222-2222-2222-222222222222', 'website_visit', 0, '{}'::jsonb),
(gen_random_uuid(), '22222222-2222-2222-2222-222222222222', 'pricing_page_view', 0, '{}'::jsonb),
(gen_random_uuid(), '22222222-2222-2222-2222-222222222222', 'pricing_page_view', 0, '{}'::jsonb),
(gen_random_uuid(), '22222222-2222-2222-2222-222222222222', 'pricing_page_view', 0, '{}'::jsonb),
(gen_random_uuid(), '22222222-2222-2222-2222-222222222222', 'financing_calculator', 0, '{}'::jsonb);

-- Insert Lead 3: Alice Brown (COLD) - Score 35
INSERT INTO leads (id, name, email, source, location, current_score, classification, metadata) VALUES
('33333333-3333-3333-3333-333333333333', 'Alice Brown', 'alice@example.com', 'social_media', 'Los Angeles, CA', 35, 'cold',
 '{"demographics": {"location_score": "other", "income_bracket": "low", "credit_score": "not_available"}}'::jsonb);

-- Activities for Alice Brown
INSERT INTO lead_activities (id, lead_id, activity_type, points_awarded, metadata) VALUES
(gen_random_uuid(), '33333333-3333-3333-3333-333333333333', 'email_open', 0, '{}'::jsonb),
(gen_random_uuid(), '33333333-3333-3333-3333-333333333333', 'email_open', 0, '{}'::jsonb),
(gen_random_uuid(), '33333333-3333-3333-3333-333333333333', 'website_visit', 0, '{}'::jsonb),
(gen_random_uuid(), '33333333-3333-3333-3333-333333333333', 'website_visit', 0, '{}'::jsonb);


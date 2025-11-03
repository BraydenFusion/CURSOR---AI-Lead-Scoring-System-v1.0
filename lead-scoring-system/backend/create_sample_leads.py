#!/usr/bin/env python3
"""Create 10 diverse sample leads for testing AI scoring.

This script creates leads across different scenarios:
- High-value enterprise leads
- Active engagement leads
- Cold leads
- Referral leads
- Various sources and locations
"""

import sys
import os
from datetime import datetime, timedelta
from uuid import uuid4

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app.models.lead import Lead, LeadStatus
from app.models.activity import LeadActivity
from app.models.ai_scoring import LeadEngagementEvent
from app.services.ai_scoring import calculate_overall_score


def create_sample_leads(db: Session):
    """Create 10 diverse sample leads."""
    
    leads_data = [
        # Lead 1: High-value enterprise lead (HOT)
        {
            "name": "Sarah Chen",
            "email": "sarah.chen@techcorp.com",
            "phone": "+1-555-0101",
            "source": "referral",
            "location": "San Francisco, CA",
            "metadata": {
                "company": "TechCorp Inc",
                "industry": "Technology",
                "company_size": "500-1000",
                "title": "VP of Sales",
                "budget": "$500K+",
                "timeframe": "Q1 2025",
            },
            "activities": [
                {"type": "demo_requested", "points": 20, "days_ago": 1},
                {"type": "pricing_inquiry", "points": 15, "days_ago": 2},
                {"type": "email_opened", "points": 5, "days_ago": 0},
            ],
            "engagement_events": [
                {"type": "email_open", "count": 5, "days_ago": 0},
                {"type": "website_visit", "count": 12, "days_ago": 0, "time_on_site": 45},
                {"type": "form_submit", "count": 2, "days_ago": 1},
            ],
        },
        
        # Lead 2: Active engagement lead (HOT)
        {
            "name": "Michael Rodriguez",
            "email": "m.rodriguez@startup.io",
            "phone": "+1-555-0102",
            "source": "organic_search",
            "location": "Austin, TX",
            "metadata": {
                "company": "StartupIO",
                "industry": "SaaS",
                "company_size": "50-100",
                "title": "Founder",
                "budget": "$100K-250K",
            },
            "activities": [
                {"type": "website_visit", "points": 10, "days_ago": 0},
                {"type": "email_clicked", "points": 8, "days_ago": 1},
                {"type": "form_submit", "points": 12, "days_ago": 2},
            ],
            "engagement_events": [
                {"type": "email_open", "count": 8, "days_ago": 0},
                {"type": "email_click", "count": 6, "days_ago": 0},
                {"type": "website_visit", "count": 20, "days_ago": 0, "time_on_site": 120},
            ],
        },
        
        # Lead 3: Referral lead (WARM)
        {
            "name": "Jennifer Park",
            "email": "jennifer.park@enterprise.com",
            "phone": "+1-555-0103",
            "source": "referral",
            "location": "New York, NY",
            "metadata": {
                "company": "Enterprise Solutions",
                "industry": "Enterprise",
                "company_size": "1000+",
                "title": "Director of Operations",
                "referred_by": "Sarah Chen",
            },
            "activities": [
                {"type": "referral_received", "points": 15, "days_ago": 5},
                {"type": "email_opened", "points": 5, "days_ago": 3},
            ],
            "engagement_events": [
                {"type": "email_open", "count": 3, "days_ago": 3},
                {"type": "website_visit", "count": 5, "days_ago": 5, "time_on_site": 15},
            ],
        },
        
        # Lead 4: Cold lead from paid ads (COLD)
        {
            "name": "Robert Thompson",
            "email": "r.thompson@gmail.com",
            "phone": "+1-555-0104",
            "source": "paid_ad",
            "location": "Chicago, IL",
            "metadata": {
                "company": "Unknown",
                "industry": "Unknown",
                "ad_campaign": "Q4 2024",
            },
            "activities": [
                {"type": "form_submit", "points": 8, "days_ago": 30},
            ],
            "engagement_events": [
                {"type": "website_visit", "count": 1, "days_ago": 30, "time_on_site": 2},
            ],
        },
        
        # Lead 5: High engagement, no buying signals (WARM)
        {
            "name": "Emily Watson",
            "email": "emily.watson@midmarket.com",
            "phone": "+1-555-0105",
            "source": "organic_search",
            "location": "Seattle, WA",
            "metadata": {
                "company": "MidMarket Solutions",
                "industry": "Retail",
                "company_size": "200-500",
                "title": "Marketing Manager",
            },
            "activities": [
                {"type": "website_visit", "points": 10, "days_ago": 2},
                {"type": "email_opened", "points": 5, "days_ago": 1},
                {"type": "blog_viewed", "points": 5, "days_ago": 3},
            ],
            "engagement_events": [
                {"type": "email_open", "count": 15, "days_ago": 0},
                {"type": "website_visit", "count": 8, "days_ago": 0, "time_on_site": 60},
            ],
        },
        
        # Lead 6: Strong buying signals (HOT)
        {
            "name": "David Kim",
            "email": "david.kim@growthco.com",
            "phone": "+1-555-0106",
            "source": "content_marketing",
            "location": "Los Angeles, CA",
            "metadata": {
                "company": "GrowthCo",
                "industry": "E-commerce",
                "company_size": "100-200",
                "title": "CTO",
                "budget": "$250K-500K",
                "timeframe": "Q2 2025",
            },
            "activities": [
                {"type": "demo_requested", "points": 20, "days_ago": 0},
                {"type": "pricing_inquiry", "points": 15, "days_ago": 1},
                {"type": "case_study_viewed", "points": 10, "days_ago": 2},
            ],
            "engagement_events": [
                {"type": "email_open", "count": 10, "days_ago": 0},
                {"type": "email_click", "count": 8, "days_ago": 0},
                {"type": "website_visit", "count": 15, "days_ago": 0, "time_on_site": 90},
                {"type": "form_submit", "count": 3, "days_ago": 0},
            ],
        },
        
        # Lead 7: Low engagement (COLD)
        {
            "name": "Lisa Anderson",
            "email": "lisa.anderson@smallbiz.com",
            "phone": "+1-555-0107",
            "source": "cold_email",
            "location": "Miami, FL",
            "metadata": {
                "company": "SmallBiz Inc",
                "industry": "Services",
                "company_size": "10-50",
            },
            "activities": [
                {"type": "email_opened", "points": 3, "days_ago": 45},
            ],
            "engagement_events": [
                {"type": "email_open", "count": 1, "days_ago": 45},
            ],
        },
        
        # Lead 8: Recent high activity (HOT)
        {
            "name": "James Wilson",
            "email": "james.wilson@enterprise2.com",
            "phone": "+1-555-0108",
            "source": "webinar",
            "location": "Boston, MA",
            "metadata": {
                "company": "Enterprise2",
                "industry": "Finance",
                "company_size": "500-1000",
                "title": "VP of Sales",
                "webinar": "Product Demo Q4 2024",
            },
            "activities": [
                {"type": "webinar_attended", "points": 15, "days_ago": 3},
                {"type": "demo_requested", "points": 20, "days_ago": 2},
                {"type": "email_clicked", "points": 8, "days_ago": 1},
            ],
            "engagement_events": [
                {"type": "email_open", "count": 12, "days_ago": 0},
                {"type": "email_click", "count": 10, "days_ago": 0},
                {"type": "website_visit", "count": 18, "days_ago": 0, "time_on_site": 150},
            ],
        },
        
        # Lead 9: Mid-level engagement (WARM)
        {
            "name": "Patricia Martinez",
            "email": "p.martinez@retailco.com",
            "phone": "+1-555-0109",
            "source": "social_media",
            "location": "Denver, CO",
            "metadata": {
                "company": "RetailCo",
                "industry": "Retail",
                "company_size": "200-500",
                "title": "Director of Marketing",
            },
            "activities": [
                {"type": "website_visit", "points": 10, "days_ago": 7},
                {"type": "email_opened", "points": 5, "days_ago": 5},
                {"type": "blog_viewed", "points": 5, "days_ago": 10},
            ],
            "engagement_events": [
                {"type": "email_open", "count": 6, "days_ago": 0},
                {"type": "website_visit", "count": 4, "days_ago": 0, "time_on_site": 25},
            ],
        },
        
        # Lead 10: Enterprise with buying signals (HOT)
        {
            "name": "Christopher Lee",
            "email": "chris.lee@bigcorp.com",
            "phone": "+1-555-0110",
            "source": "referral",
            "location": "San Jose, CA",
            "metadata": {
                "company": "BigCorp Industries",
                "industry": "Manufacturing",
                "company_size": "1000+",
                "title": "CEO",
                "budget": "$1M+",
                "timeframe": "Q1 2025",
                "referred_by": "Sarah Chen",
            },
            "activities": [
                {"type": "referral_received", "points": 15, "days_ago": 2},
                {"type": "demo_requested", "points": 20, "days_ago": 1},
                {"type": "pricing_inquiry", "points": 15, "days_ago": 1},
                {"type": "contract_review", "points": 25, "days_ago": 0},
            ],
            "engagement_events": [
                {"type": "email_open", "count": 20, "days_ago": 0},
                {"type": "email_click", "count": 15, "days_ago": 0},
                {"type": "website_visit", "count": 25, "days_ago": 0, "time_on_site": 180},
                {"type": "form_submit", "count": 5, "days_ago": 0},
            ],
        },
    ]
    
    created_leads = []
    
    for lead_data in leads_data:
        # Create lead
        lead = Lead(
            id=uuid4(),
            name=lead_data["name"],
            email=lead_data["email"],
            phone=lead_data["phone"],
            source=lead_data["source"],
            location=lead_data["location"],
            _metadata=lead_data["metadata"],
            current_score=0,
            classification=None,
            status=LeadStatus.NEW,
        )
        
        db.add(lead)
        db.flush()
        
        # Create activities
        now = datetime.utcnow()
        for activity_data in lead_data.get("activities", []):
            activity = LeadActivity(
                lead_id=lead.id,
                activity_type=activity_data["type"],
                points_awarded=activity_data["points"],
                timestamp=now - timedelta(days=activity_data["days_ago"]),
                _metadata={},
            )
            db.add(activity)
        
        # Create engagement events
        for event_data in lead_data.get("engagement_events", []):
            event_type = event_data["type"]
            count = event_data.get("count", 1)
            days_ago = event_data.get("days_ago", 0)
            
            for i in range(count):
                event = LeadEngagementEvent(
                    lead_id=lead.id,
                    event_type=event_type,
                    event_data={
                        "time_on_site_minutes": event_data.get("time_on_site", 0),
                        "sequence": i + 1,
                    } if event_type == "website_visit" else {},
                    created_at=now - timedelta(days=days_ago, hours=i),
                )
                db.add(event)
        
        db.flush()
        
        # Calculate AI score (will use OpenAI if available, otherwise fallback)
        try:
            # This will automatically use OpenAI if API key is set
            result = calculate_overall_score(lead.id, db, use_openai=True)
            db.refresh(lead)
            
            if os.getenv("OPENAI_API_KEY") and result.get("scoring_metadata", {}).get("openai_model"):
                print(f"✅ Created {lead.name} with OpenAI scoring: {result['overall_score']}/100 ({result['priority_tier']})")
            else:
                print(f"✅ Created {lead.name} with rule-based scoring: {lead.current_score}/100")
        except Exception as e:
            # Fallback to rule-based scoring
            print(f"⚠️  Scoring failed for {lead.name}, using rule-based fallback: {e}")
            try:
                calculate_overall_score(lead.id, db, use_openai=False)
                db.refresh(lead)
                print(f"✅ Created {lead.name} with rule-based scoring: {lead.current_score}/100")
            except Exception as e2:
                print(f"❌ Failed to score {lead.name}: {e2}")
        
        db.refresh(lead)
        created_leads.append(lead)
    
    db.commit()
    
    return created_leads


def main():
    """Main function to create sample leads."""
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    with get_db() as db:
        print("🚀 Creating 10 diverse sample leads...")
        print(f"📊 OpenAI API Key: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Not set (using rule-based scoring)'}")
        print()
        
        leads = create_sample_leads(db)
        
        print()
        print("=" * 60)
        print("✅ Successfully created 10 sample leads:")
        print("=" * 60)
        
        for lead in leads:
            classification_emoji = {
                "hot": "🔥",
                "warm": "🟡",
                "cold": "🔵",
            }.get(lead.classification or "cold", "⚪")
            
            print(f"{classification_emoji} {lead.name:30} | Score: {lead.current_score:3}/100 | {lead.classification or 'N/A':5} | Source: {lead.source:20}")
        
        print()
        print("📊 Summary:")
        hot_count = sum(1 for l in leads if l.classification == "hot")
        warm_count = sum(1 for l in leads if l.classification == "warm")
        cold_count = sum(1 for l in leads if l.classification == "cold")
        
        print(f"   🔥 HOT leads:   {hot_count}")
        print(f"   🟡 WARM leads:  {warm_count}")
        print(f"   🔵 COLD leads:  {cold_count}")
        print()
        print("💡 To enable OpenAI scoring, set OPENAI_API_KEY environment variable")
        print("   Example: export OPENAI_API_KEY='your-api-key-here'")


if __name__ == "__main__":
    main()


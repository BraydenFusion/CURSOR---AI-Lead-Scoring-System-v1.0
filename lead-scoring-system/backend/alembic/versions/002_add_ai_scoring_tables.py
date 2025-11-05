"""Add AI scoring tables: lead_scores, lead_engagement_events, lead_insights

Revision ID: 002_ai_scoring
Revises: a9c00044788a
Create Date: 2025-11-03 15:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID


# revision identifiers, used by Alembic.
revision: str = '002_ai_scoring'
down_revision: Union[str, None] = 'a9c00044788a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if leads table exists before creating foreign key
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()
    
    if 'leads' not in tables:
        # If leads table doesn't exist, skip this migration
        # It will be created by 000_initial migration
        print("⚠️  WARNING: leads table does not exist. Skipping lead_scores table creation.")
        print("⚠️  Run 000_initial migration first to create base tables.")
        return
    
    # Create lead_scores table
    op.create_table(
        'lead_scores',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('lead_id', UUID(as_uuid=True), sa.ForeignKey('leads.id', ondelete='CASCADE'), nullable=False),
        sa.Column('overall_score', sa.Integer(), sa.CheckConstraint('overall_score >= 0 AND overall_score <= 100'), nullable=False),
        sa.Column('engagement_score', sa.Integer(), sa.CheckConstraint('engagement_score >= 0 AND engagement_score <= 100'), nullable=False),
        sa.Column('buying_signal_score', sa.Integer(), sa.CheckConstraint('buying_signal_score >= 0 AND buying_signal_score <= 100'), nullable=False),
        sa.Column('demographic_score', sa.Integer(), sa.CheckConstraint('demographic_score >= 0 AND demographic_score <= 100'), nullable=False),
        sa.Column('priority_tier', sa.String(10), nullable=False),  # 'HOT', 'WARM', 'COLD'
        sa.Column('confidence_level', sa.Numeric(3, 2), sa.CheckConstraint('confidence_level >= 0.00 AND confidence_level <= 1.00'), nullable=False),
        sa.Column('scoring_metadata', JSONB(), nullable=True),
        sa.Column('scored_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
    )
    op.create_index('idx_lead_scores_lead_id', 'lead_scores', ['lead_id'])
    op.create_index('idx_lead_scores_overall_score', 'lead_scores', ['overall_score'])
    op.create_index('idx_lead_scores_priority_tier', 'lead_scores', ['priority_tier'])
    op.create_index('idx_lead_scores_scored_at', 'lead_scores', ['scored_at'])

    # Create lead_engagement_events table
    op.create_table(
        'lead_engagement_events',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('lead_id', UUID(as_uuid=True), sa.ForeignKey('leads.id', ondelete='CASCADE'), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),  # 'email_open', 'website_visit', 'form_submit', etc.
        sa.Column('event_data', JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
    )
    op.create_index('idx_engagement_events_lead_id', 'lead_engagement_events', ['lead_id'])
    op.create_index('idx_engagement_events_type', 'lead_engagement_events', ['event_type'])
    op.create_index('idx_engagement_events_created_at', 'lead_engagement_events', ['created_at'])

    # Create lead_insights table
    op.create_table(
        'lead_insights',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('lead_id', UUID(as_uuid=True), sa.ForeignKey('leads.id', ondelete='CASCADE'), nullable=False),
        sa.Column('insight_type', sa.String(50), nullable=False),  # 'talking_point', 'concern', 'opportunity'
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('confidence', sa.Numeric(3, 2), sa.CheckConstraint('confidence >= 0.00 AND confidence <= 1.00'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
    )
    op.create_index('idx_lead_insights_lead_id', 'lead_insights', ['lead_id'])
    op.create_index('idx_lead_insights_type', 'lead_insights', ['insight_type'])
    op.create_index('idx_lead_insights_created_at', 'lead_insights', ['created_at'])


def downgrade() -> None:
    op.drop_index('idx_lead_insights_created_at', table_name='lead_insights')
    op.drop_index('idx_lead_insights_type', table_name='lead_insights')
    op.drop_index('idx_lead_insights_lead_id', table_name='lead_insights')
    op.drop_table('lead_insights')
    
    op.drop_index('idx_engagement_events_created_at', table_name='lead_engagement_events')
    op.drop_index('idx_engagement_events_type', table_name='lead_engagement_events')
    op.drop_index('idx_engagement_events_lead_id', table_name='lead_engagement_events')
    op.drop_table('lead_engagement_events')
    
    op.drop_index('idx_lead_scores_scored_at', table_name='lead_scores')
    op.drop_index('idx_lead_scores_priority_tier', table_name='lead_scores')
    op.drop_index('idx_lead_scores_overall_score', table_name='lead_scores')
    op.drop_index('idx_lead_scores_lead_id', table_name='lead_scores')
    op.drop_table('lead_scores')


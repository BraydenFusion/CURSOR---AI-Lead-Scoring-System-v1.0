"""Add performance indexes

Revision ID: 001_performance_indexes
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_performance_indexes'
down_revision = None  # Will be set by actual latest revision
branch_labels = None
depends_on = None


def upgrade():
    # Indexes for leads table
    op.create_index(
        'idx_leads_classification_score',
        'leads',
        ['classification', 'current_score'],
        unique=False
    )
    op.create_index(
        'idx_leads_status',
        'leads',
        ['status'],
        unique=False
    )
    op.create_index(
        'idx_leads_created_at',
        'leads',
        ['created_at'],
        unique=False
    )
    
    # Indexes for lead_activities
    op.create_index(
        'idx_activities_lead_timestamp',
        'lead_activities',
        ['lead_id', 'timestamp'],
        unique=False
    )
    
    # Indexes for lead_assignments
    op.create_index(
        'idx_assignments_user_status',
        'lead_assignments',
        ['user_id', 'status'],
        unique=False
    )
    op.create_index(
        'idx_assignments_lead_status',
        'lead_assignments',
        ['lead_id', 'status'],
        unique=False
    )
    
    # Indexes for notifications
    op.create_index(
        'idx_notifications_user_read',
        'notifications',
        ['user_id', 'is_read'],
        unique=False
    )
    op.create_index(
        'idx_notifications_created',
        'notifications',
        ['created_at'],
        unique=False
    )
    
    # Indexes for lead_notes
    op.create_index(
        'idx_notes_lead_created',
        'lead_notes',
        ['lead_id', 'created_at'],
        unique=False
    )


def downgrade():
    op.drop_index('idx_leads_classification_score', table_name='leads')
    op.drop_index('idx_leads_status', table_name='leads')
    op.drop_index('idx_leads_created_at', table_name='leads')
    op.drop_index('idx_activities_lead_timestamp', table_name='lead_activities')
    op.drop_index('idx_assignments_user_status', table_name='lead_assignments')
    op.drop_index('idx_assignments_lead_status', table_name='lead_assignments')
    op.drop_index('idx_notifications_user_read', table_name='notifications')
    op.drop_index('idx_notifications_created', table_name='notifications')
    op.drop_index('idx_notes_lead_created', table_name='lead_notes')


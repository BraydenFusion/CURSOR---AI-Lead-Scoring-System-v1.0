"""Add performance indexes

Revision ID: 001_performance_indexes
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_performance_indexes'
down_revision = '000_initial'  # Depends on initial schema migration
branch_labels = None
depends_on = None


def upgrade():
    # Safely create indexes - check if tables exist first
    # This migration depends on 000_initial which creates the tables
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()
    
    # Indexes for leads table (only if table exists)
    if 'leads' in tables:
        # Use raw SQL to check if index exists before creating (PostgreSQL-specific)
        existing_indexes = [row[0] for row in connection.execute(sa.text(
            "SELECT indexname FROM pg_indexes WHERE tablename = 'leads'"
        )).fetchall()]
        
        if 'idx_leads_classification_score' not in existing_indexes:
            op.create_index('idx_leads_classification_score', 'leads', ['classification', 'current_score'], unique=False)
        
        if 'idx_leads_status' not in existing_indexes:
            op.create_index('idx_leads_status', 'leads', ['status'], unique=False)
        
        if 'idx_leads_created_at' not in existing_indexes:
            op.create_index('idx_leads_created_at', 'leads', ['created_at'], unique=False)
    
    # Indexes for lead_activities
    if 'lead_activities' in tables:
        existing_indexes = [row[0] for row in connection.execute(sa.text(
            "SELECT indexname FROM pg_indexes WHERE tablename = 'lead_activities'"
        )).fetchall()]
        
        if 'idx_activities_lead_timestamp' not in existing_indexes:
            op.create_index('idx_activities_lead_timestamp', 'lead_activities', ['lead_id', 'timestamp'], unique=False)
    
    # Indexes for lead_assignments
    if 'lead_assignments' in tables:
        existing_indexes = [row[0] for row in connection.execute(sa.text(
            "SELECT indexname FROM pg_indexes WHERE tablename = 'lead_assignments'"
        )).fetchall()]
        
        if 'idx_assignments_user_status' not in existing_indexes:
            op.create_index('idx_assignments_user_status', 'lead_assignments', ['user_id', 'status'], unique=False)
        
        if 'idx_assignments_lead_status' not in existing_indexes:
            op.create_index('idx_assignments_lead_status', 'lead_assignments', ['lead_id', 'status'], unique=False)
    
    # Indexes for notifications
    if 'notifications' in tables:
        existing_indexes = [row[0] for row in connection.execute(sa.text(
            "SELECT indexname FROM pg_indexes WHERE tablename = 'notifications'"
        )).fetchall()]
        
        if 'idx_notifications_user_read' not in existing_indexes:
            op.create_index('idx_notifications_user_read', 'notifications', ['user_id', 'is_read'], unique=False)
        
        if 'idx_notifications_created' not in existing_indexes:
            op.create_index('idx_notifications_created', 'notifications', ['created_at'], unique=False)
    
    # Indexes for lead_notes
    if 'lead_notes' in tables:
        existing_indexes = [row[0] for row in connection.execute(sa.text(
            "SELECT indexname FROM pg_indexes WHERE tablename = 'lead_notes'"
        )).fetchall()]
        
        if 'idx_notes_lead_created' not in existing_indexes:
            op.create_index('idx_notes_lead_created', 'lead_notes', ['lead_id', 'created_at'], unique=False)


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


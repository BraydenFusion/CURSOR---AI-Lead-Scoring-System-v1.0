"""Initial schema - create all core tables

Revision ID: 000_initial
Revises: 
Create Date: 2025-11-03 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID, ENUM


# revision identifiers, used by Alembic.
revision: str = '000_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE lead_classification AS ENUM ('hot', 'warm', 'cold');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE lead_status AS ENUM ('new', 'contacted', 'qualified', 'converted', 'lost');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE user_role AS ENUM ('admin', 'manager', 'sales_rep');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('username', sa.String(100), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('role', sa.Enum('admin', 'manager', 'sales_rep', name='user_role'), nullable=False, server_default='sales_rep'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('last_login', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_username', 'users', ['username'])
    
    # Create leads table
    op.create_table(
        'leads',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('source', sa.String(100), nullable=False),
        sa.Column('location', sa.String(255), nullable=True),
        sa.Column('current_score', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('classification', sa.Enum('hot', 'warm', 'cold', name='lead_classification'), nullable=True),
        sa.Column('status', sa.Enum('new', 'contacted', 'qualified', 'converted', 'lost', name='lead_status'), nullable=False, server_default='new'),
        sa.Column('contacted_at', sa.DateTime(), nullable=True),
        sa.Column('qualified_at', sa.DateTime(), nullable=True),
        sa.Column('closed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('metadata', JSONB(), nullable=False, server_default='{}'),
        sa.CheckConstraint('current_score >= 0 AND current_score <= 100', name='chk_leads_score_range'),
    )
    
    # Create lead_activities table
    op.create_table(
        'lead_activities',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('lead_id', UUID(as_uuid=True), sa.ForeignKey('leads.id', ondelete='CASCADE'), nullable=False),
        sa.Column('activity_type', sa.String(100), nullable=False),
        sa.Column('points_awarded', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('timestamp', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('metadata', JSONB(), nullable=False, server_default='{}'),
    )
    op.create_index('idx_activities_lead_id', 'lead_activities', ['lead_id'])
    op.create_index('idx_activities_timestamp', 'lead_activities', ['timestamp'], postgresql_ops={'timestamp': 'DESC'})
    
    # Create lead_score_history table
    op.create_table(
        'lead_score_history',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('lead_id', UUID(as_uuid=True), sa.ForeignKey('leads.id', ondelete='CASCADE'), nullable=False),
        sa.Column('old_score', sa.Integer(), nullable=True),
        sa.Column('new_score', sa.Integer(), nullable=True),
        sa.Column('old_classification', sa.String(20), nullable=True),
        sa.Column('new_classification', sa.String(20), nullable=True),
        sa.Column('trigger_activity_id', UUID(as_uuid=True), sa.ForeignKey('lead_activities.id'), nullable=True),
        sa.Column('changed_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
    )
    op.create_index('idx_scores_history_lead_id', 'lead_score_history', ['lead_id'])
    
    # Create lead_assignments table
    op.create_table(
        'lead_assignments',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('lead_id', UUID(as_uuid=True), sa.ForeignKey('leads.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('assigned_by', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('assigned_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='active'),
        sa.Column('notes', sa.String(500), nullable=True),
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default='true'),
    )
    
    # Create lead_notes table
    op.create_table(
        'lead_notes',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('lead_id', UUID(as_uuid=True), sa.ForeignKey('leads.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('note_type', sa.String(50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
    )
    
    # Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('related_lead_id', UUID(as_uuid=True), sa.ForeignKey('leads.id', ondelete='CASCADE'), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
    )
    op.create_index('idx_notifications_user_id', 'notifications', ['user_id'])
    op.create_index('idx_notifications_is_read', 'notifications', ['is_read'])


def downgrade() -> None:
    # Drop tables in reverse order (respecting foreign keys)
    op.drop_table('notifications')
    op.drop_table('lead_notes')
    op.drop_table('lead_assignments')
    op.drop_table('lead_score_history')
    op.drop_table('lead_activities')
    op.drop_table('leads')
    op.drop_table('users')
    
    # Drop enum types
    op.execute('DROP TYPE IF EXISTS lead_status CASCADE')
    op.execute('DROP TYPE IF EXISTS lead_classification CASCADE')
    op.execute('DROP TYPE IF EXISTS user_role CASCADE')


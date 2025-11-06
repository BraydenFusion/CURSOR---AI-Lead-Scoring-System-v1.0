"""Add lead ownership tracking (created_by field)

Revision ID: 003_lead_ownership
Revises: 002_ai_scoring
Create Date: 2025-11-04 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = '003_lead_ownership'
down_revision: Union[str, None] = '002_ai_scoring'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if leads table exists before adding column
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()
    
    if 'leads' not in tables:
        # If leads table doesn't exist, skip this migration
        print("⚠️  WARNING: leads table does not exist. Skipping created_by column addition.")
        print("⚠️  Run 000_initial migration first to create base tables.")
        return
    
    # Check if created_by column already exists
    columns = [col['name'] for col in inspector.get_columns('leads')]
    
    if 'created_by' in columns:
        print("ℹ️  created_by column already exists. Skipping column addition.")
        # Check if index exists, create if missing
        indexes = [idx['name'] for idx in inspector.get_indexes('leads')]
        if 'idx_leads_created_by' not in indexes:
            op.create_index('idx_leads_created_by', 'leads', ['created_by'])
        return
    
    # Add created_by field to track which sales rep created the lead
    op.add_column('leads', sa.Column('created_by', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True))
    op.create_index('idx_leads_created_by', 'leads', ['created_by'])


def downgrade() -> None:
    op.drop_index('idx_leads_created_by', table_name='leads')
    op.drop_column('leads', 'created_by')


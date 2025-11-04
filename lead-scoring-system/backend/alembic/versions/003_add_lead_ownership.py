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
    # Add created_by field to track which sales rep created the lead
    op.add_column('leads', sa.Column('created_by', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True))
    op.create_index('idx_leads_created_by', 'leads', ['created_by'])


def downgrade() -> None:
    op.drop_index('idx_leads_created_by', table_name='leads')
    op.drop_column('leads', 'created_by')


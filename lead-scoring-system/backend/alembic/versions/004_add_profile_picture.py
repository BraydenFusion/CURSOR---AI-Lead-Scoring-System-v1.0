"""Add profile_picture_url to users table

Revision ID: 004_profile_picture
Revises: 003_lead_ownership
Create Date: 2025-01-04 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004_profile_picture'
down_revision: Union[str, None] = '003_lead_ownership'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add profile_picture_url field to users table
    op.add_column('users', sa.Column('profile_picture_url', sa.String(500), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'profile_picture_url')


"""Add company_role to users table

Revision ID: 005_company_role
Revises: 004_profile_picture
Create Date: 2025-11-04 22:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '005_company_role'
down_revision: Union[str, None] = '004_profile_picture'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add company_role field to users table
    op.add_column('users', sa.Column('company_role', sa.String(100), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'company_role')


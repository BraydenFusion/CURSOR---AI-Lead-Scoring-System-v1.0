"""Add Phase 4 tables: users, assignments, notes, notifications

Revision ID: a9c00044788a
Revises: 001_performance_indexes
Create Date: 2025-11-02 12:17:08.635575

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a9c00044788a'
down_revision: Union[str, None] = '001_performance_indexes'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

"""Add CRM integration and sync log tables.

Revision ID: c261b1e2bd80
Revises: b8f5bba1c9a7
Create Date: 2025-11-08 16:30:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "c261b1e2bd80"
down_revision: Union[str, None] = "b8f5bba1c9a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "crm_integrations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider", sa.String(length=20), nullable=False),
        sa.Column("credentials", sa.Text(), nullable=False),
        sa.Column("sync_direction", sa.String(length=20), nullable=False, server_default="bidirectional"),
        sa.Column("field_mappings", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("sync_frequency", sa.String(length=20), nullable=False, server_default="manual"),
        sa.Column("last_sync", sa.DateTime(timezone=False), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("conflict_strategy", sa.String(length=20), nullable=False, server_default="manual"),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_crm_integrations_user_provider", "crm_integrations", ["user_id", "provider"], unique=True)

    op.create_table(
        "sync_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("integration_id", sa.Integer(), sa.ForeignKey("crm_integrations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sync_started", sa.DateTime(timezone=False), nullable=False, server_default=sa.func.now()),
        sa.Column("sync_completed", sa.DateTime(timezone=False), nullable=True),
        sa.Column("records_synced", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("errors", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="running"),
        sa.Column("direction", sa.String(length=20), nullable=False, server_default="bidirectional"),
    )
    op.create_index("ix_sync_logs_integration_id", "sync_logs", ["integration_id"])
    op.create_index("ix_sync_logs_status", "sync_logs", ["status"])


def downgrade() -> None:
    op.drop_index("ix_sync_logs_status", table_name="sync_logs")
    op.drop_index("ix_sync_logs_integration_id", table_name="sync_logs")
    op.drop_table("sync_logs")
    op.drop_index("ix_crm_integrations_user_provider", table_name="crm_integrations")
    op.drop_table("crm_integrations")

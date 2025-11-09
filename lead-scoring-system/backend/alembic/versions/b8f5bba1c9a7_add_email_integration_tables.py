"""Add email integration tables for connected accounts and messages.

Revision ID: b8f5bba1c9a7
Revises: b01f0ad7b5ac
Create Date: 2025-11-08 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "b8f5bba1c9a7"
down_revision: Union[str, None] = "b01f0ad7b5ac"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "email_accounts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider", sa.String(length=20), nullable=False),
        sa.Column("email_address", sa.String(length=255), nullable=False),
        sa.Column("access_token", sa.Text(), nullable=False),
        sa.Column("refresh_token", sa.Text(), nullable=True),
        sa.Column("token_expires_at", sa.DateTime(timezone=False), nullable=False),
        sa.Column("connected_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.func.now()),
        sa.Column("last_sync", sa.DateTime(timezone=False), nullable=True),
        sa.Column("auto_sync_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("ix_email_accounts_user_id", "email_accounts", ["user_id"])
    op.create_index("ix_email_accounts_user_provider", "email_accounts", ["user_id", "provider"])
    op.create_unique_constraint("uq_email_accounts_email_provider", "email_accounts", ["email_address", "provider"])

    op.create_table(
        "email_messages",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("email_account_id", sa.Integer(), sa.ForeignKey("email_accounts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("leads.id", ondelete="SET NULL"), nullable=True),
        sa.Column("message_id", sa.String(length=255), nullable=False),
        sa.Column("subject", sa.String(length=500), nullable=False),
        sa.Column("sender", sa.String(length=255), nullable=False),
        sa.Column("recipients", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("body_text", sa.Text(), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=False), nullable=False),
        sa.Column("direction", sa.String(length=20), nullable=False),
        sa.Column("read", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("ix_email_messages_account", "email_messages", ["email_account_id"])
    op.create_index("ix_email_messages_lead", "email_messages", ["lead_id"])
    op.create_index("ix_email_messages_message_id", "email_messages", ["message_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_email_messages_message_id", table_name="email_messages")
    op.drop_index("ix_email_messages_lead", table_name="email_messages")
    op.drop_index("ix_email_messages_account", table_name="email_messages")
    op.drop_table("email_messages")
    op.drop_constraint("uq_email_accounts_email_provider", "email_accounts", type_="unique")
    op.drop_index("ix_email_accounts_user_provider", table_name="email_accounts")
    op.drop_index("ix_email_accounts_user_id", table_name="email_accounts")
    op.drop_table("email_accounts")

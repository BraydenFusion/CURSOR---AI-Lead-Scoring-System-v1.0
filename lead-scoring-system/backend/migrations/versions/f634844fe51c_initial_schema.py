"""Initial schema

Revision ID: f634844fe51c
Revises: 
Create Date: 2025-10-31 21:30:32.045657

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'f634844fe51c'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    lead_classification = sa.Enum("hot", "warm", "cold", name="lead_classification")
    lead_classification.create(op.get_bind(), checkfirst=True)

    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    op.create_table(
        "leads",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("source", sa.String(length=100), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("current_score", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("classification", lead_classification, nullable=False, server_default=sa.text("'cold'::lead_classification")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.CheckConstraint("current_score >= 0 AND current_score <= 100", name="chk_leads_score_range"),
    )
    op.execute("CREATE INDEX idx_leads_score ON leads (current_score DESC)")
    op.create_index("idx_leads_classification", "leads", ["classification"])

    op.create_table(
        "lead_activities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("leads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("activity_type", sa.String(length=100), nullable=False),
        sa.Column("points_awarded", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("timestamp", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
    )
    op.create_index("idx_activities_lead_id", "lead_activities", ["lead_id"])
    op.execute("CREATE INDEX idx_activities_timestamp ON lead_activities (timestamp DESC)")

    op.create_table(
        "lead_scores_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("leads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("old_score", sa.Integer(), nullable=True),
        sa.Column("new_score", sa.Integer(), nullable=True),
        sa.Column("old_classification", sa.String(length=20), nullable=True),
        sa.Column("new_classification", sa.String(length=20), nullable=True),
        sa.Column("trigger_activity_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("lead_activities.id"), nullable=True),
        sa.Column("changed_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_scores_history_lead_id", "lead_scores_history", ["lead_id"])


def downgrade() -> None:
    op.drop_index("idx_scores_history_lead_id", table_name="lead_scores_history")
    op.drop_table("lead_scores_history")

    op.execute("DROP INDEX IF EXISTS idx_activities_timestamp")
    op.drop_index("idx_activities_lead_id", table_name="lead_activities")
    op.drop_table("lead_activities")

    op.drop_index("idx_leads_classification", table_name="leads")
    op.execute("DROP INDEX IF EXISTS idx_leads_score")
    op.drop_table("leads")

    lead_classification = sa.Enum("hot", "warm", "cold", name="lead_classification")
    lead_classification.drop(op.get_bind(), checkfirst=True)

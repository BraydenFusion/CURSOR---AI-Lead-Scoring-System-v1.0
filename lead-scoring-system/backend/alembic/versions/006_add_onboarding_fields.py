"""Add onboarding fields to users table

Revision ID: 006_add_onboarding_fields
Revises: 005_add_company_role
Create Date: 2025-01-06 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '006_add_onboarding_fields'
down_revision: Union[str, None] = '005_company_role'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if users table exists
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()
    
    if 'users' not in tables:
        print("⚠️  WARNING: users table does not exist. Skipping onboarding fields addition.")
        return
    
    # Check existing columns
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    # Add company_name if it doesn't exist
    if 'company_name' not in columns:
        op.add_column('users', sa.Column('company_name', sa.String(255), nullable=True))
        print("✅ Added company_name column")
    else:
        print("ℹ️  company_name column already exists")
    
    # Add payment_plan if it doesn't exist
    if 'payment_plan' not in columns:
        op.add_column('users', sa.Column('payment_plan', sa.String(50), nullable=True))
        print("✅ Added payment_plan column")
    else:
        print("ℹ️  payment_plan column already exists")
    
    # Add onboarding_completed if it doesn't exist
    if 'onboarding_completed' not in columns:
        op.add_column('users', sa.Column('onboarding_completed', sa.Boolean(), nullable=False, server_default='false'))
        print("✅ Added onboarding_completed column")
    else:
        print("ℹ️  onboarding_completed column already exists")


def downgrade() -> None:
    # Check if users table exists
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()
    
    if 'users' not in tables:
        return
    
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    if 'onboarding_completed' in columns:
        op.drop_column('users', 'onboarding_completed')
    
    if 'payment_plan' in columns:
        op.drop_column('users', 'payment_plan')
    
    if 'company_name' in columns:
        op.drop_column('users', 'company_name')


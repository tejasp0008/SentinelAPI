"""Initial migration — api_inventory and users tables.

Revision ID: 001_initial
Revises: None
Create Date: 2026-03-18
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "api_inventory",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("endpoint", sa.String(500), nullable=False, index=True),
        sa.Column("method", sa.String(10), nullable=False, server_default="GET"),
        sa.Column("status", sa.String(20), nullable=False, server_default="active", index=True),
        sa.Column("auth_type", sa.String(50), nullable=True),
        sa.Column("encryption", sa.String(50), nullable=True),
        sa.Column("dynamic_risk_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("last_used", sa.DateTime(), nullable=True),
        sa.Column("traffic_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("days_since_last_used", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("vulnerabilities", sa.Text(), nullable=True),
        sa.Column("metadata_hash", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("role", sa.String(20), nullable=False, server_default="viewer"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("users")
    op.drop_table("api_inventory")

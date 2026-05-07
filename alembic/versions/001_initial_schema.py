"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-05-06
"""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("phone_number", sa.String(20), nullable=True),
        sa.Column("pin_hash", sa.String(60), nullable=False),
        sa.Column("account_number", sa.String(20), nullable=False),
        sa.Column("voice_profile_id", sa.String(100), nullable=True),
        sa.Column("pin_attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_locked", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_id", "users", ["id"])

    op.create_table(
        "call_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("call_sid", sa.String(50), nullable=False, unique=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("auth_result", sa.JSON(), nullable=True),
        sa.Column("transcript", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("intent_log", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("biometric_score", sa.Integer(), nullable=True),
    )
    op.create_index("ix_call_logs_id", "call_logs", ["id"])
    op.create_index("ix_call_logs_call_sid", "call_logs", ["call_sid"])


def downgrade() -> None:
    op.drop_table("call_logs")
    op.drop_table("users")

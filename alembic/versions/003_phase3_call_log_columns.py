"""phase3 call log columns

Revision ID: 003
Revises: 002
Create Date: 2026-05-07
"""
from alembic import op
import sqlalchemy as sa

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("call_logs", sa.Column("sentiment_log", sa.JSON(), nullable=True))
    op.add_column("call_logs", sa.Column("language", sa.String(10), nullable=True, server_default="en"))
    op.add_column("call_logs", sa.Column("recording_url", sa.String(500), nullable=True))
    op.add_column("call_logs", sa.Column("duration_seconds", sa.Integer(), nullable=True))
    op.add_column("call_logs", sa.Column("escalated", sa.Boolean(), nullable=True, server_default="false"))


def downgrade() -> None:
    op.drop_column("call_logs", "escalated")
    op.drop_column("call_logs", "duration_seconds")
    op.drop_column("call_logs", "recording_url")
    op.drop_column("call_logs", "language")
    op.drop_column("call_logs", "sentiment_log")

"""rename s3 columns to generic storage columns

Revision ID: 002
Revises: 001
Create Date: 2026-08-15
"""
from typing import Sequence, Union
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # NOTE: 001_initial_schema.py already creates these columns under their
    # final names (storage_key, storage_backend, snapshot_storage_key,
    # snapshot_storage_backend), so there is nothing left to rename here.
    # This migration is kept as a no-op to preserve the revision history.
    pass


def downgrade() -> None:
    # No-op for the same reason as upgrade().
    pass

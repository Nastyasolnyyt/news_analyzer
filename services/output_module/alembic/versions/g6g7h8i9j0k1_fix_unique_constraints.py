"""Fix unique constraint on risks.article_id

Revision ID: g6g7h8i9j0k1
Revises: f5f6g7h8i9j0
Create Date: 2026-05-16 19:00:00.000000

This migration ensures the risks table has a proper UNIQUE constraint on article_id,
which is required for the ON CONFLICT clause in risk-classifier service.

The constraint may already exist in the schema definition but not in the actual database,
or it might have been created incorrectly. This migration adds it safely.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'g6g7h8i9j0k1'
down_revision: Union[str, None] = 'f5f6g7h8i9j0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add UNIQUE constraint on risks.article_id if it doesn't exist."""
    
    # First, check if the constraint already exists
    # Drop existing non-unique index if it exists
    try:
        op.drop_index('ix_risks_article_id', table_name='risks')
    except Exception:
        pass
    
    # Drop the old constraint if it exists (from earlier attempts)
    try:
        op.drop_constraint('risks_article_id_key', 'risks', type_='unique')
    except Exception:
        pass
    
    try:
        op.drop_constraint('uq_risks_article_id', 'risks', type_='unique')
    except Exception:
        pass
    
    # Create the proper UNIQUE constraint
    op.create_unique_constraint('uq_risks_article_id', 'risks', ['article_id'])


def downgrade() -> None:
    """Remove UNIQUE constraint on risks.article_id."""
    try:
        op.drop_constraint('uq_risks_article_id', 'risks', type_='unique')
    except Exception:
        pass

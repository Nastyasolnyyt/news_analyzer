"""make sentiment columns nullable

Revision ID: f5f6g7h8i9j0
Revises: e5f6g7h8i9j0
Create Date: 2025-03-24 01:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f5f6g7h8i9j0'
down_revision: Union[str, None] = 'e5f6g7h8i9j0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: make emotion, tonality, relevance nullable."""
    # Change NOT NULL constraints to allow NULL values for partial analysis results
    op.alter_column('post_analysis', 'emotion',
               existing_type=sa.Float(),
               nullable=True)
    op.alter_column('post_analysis', 'tonality',
               existing_type=sa.Float(),
               nullable=True)
    op.alter_column('post_analysis', 'relevance',
               existing_type=sa.Float(),
               nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('post_analysis', 'emotion',
               existing_type=sa.Float(),
               nullable=False)
    op.alter_column('post_analysis', 'tonality',
               existing_type=sa.Float(),
               nullable=False)
    op.alter_column('post_analysis', 'relevance',
               existing_type=sa.Float(),
               nullable=False)

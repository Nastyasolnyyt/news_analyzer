"""add sentiment table

Revision ID: c3d4e5f6g7h8
Revises: b2c3d4e5f6g7
Create Date: 2025-03-24 01:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6g7h8'
down_revision: Union[str, None] = 'b2c3d4e5f6g7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: add sentiment analysis table."""
    # Add sentiment columns to post_analysis if not exists
    # This allows sentiment_analysis service to store results
    
    # First check if post_analysis doesn't have these columns
    op.add_column('post_analysis', sa.Column('confidence', sa.Float(), nullable=True))
    op.add_column('post_analysis', sa.Column('sentiment_label', sa.String(length=50), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('post_analysis', 'sentiment_label')
    op.drop_column('post_analysis', 'confidence')

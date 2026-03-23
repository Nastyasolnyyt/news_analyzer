"""add unique constraint on post_id in post_analysis

Revision ID: e5f6g7h8i9j0
Revises: d4e5f6g7h8i9
Create Date: 2026-03-24 00:01:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e5f6g7h8i9j0'
down_revision = 'd4e5f6g7h8i9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Добавляем UNIQUE constraint на колонку post_id в таблице post_analysis
    op.create_unique_constraint('uq_post_analysis_post_id', 'post_analysis', ['post_id'])


def downgrade() -> None:
    # Удаляем UNIQUE constraint
    op.drop_constraint('uq_post_analysis_post_id', 'post_analysis', type_='unique')

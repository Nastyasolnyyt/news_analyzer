"""add unique constraint on link

Revision ID: d4e5f6g7h8i9
Revises: c3d4e5f6g7h8
Create Date: 2026-03-24 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd4e5f6g7h8i9'
down_revision = 'c3d4e5f6g7h8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Добавляем UNIQUE constraint на колонку link в таблице articles
    op.create_unique_constraint('uq_articles_link', 'articles', ['link'])


def downgrade() -> None:
    # Удаляем UNIQUE constraint
    op.drop_constraint('uq_articles_link', 'articles', type_='unique')

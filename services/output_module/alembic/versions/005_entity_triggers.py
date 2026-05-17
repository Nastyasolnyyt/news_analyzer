"""Add entity trigger support - make trigger_value searchable by name

Revision ID: 005_entity_triggers
Revises: 004_add_email_to_users
Create Date: 2026-05-17

Добавляет индекс на notification_triggers.trigger_value для быстрого поиска
по имени сущности, и обновляет тип тригерра на более универсальный "entity".
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '005_entity_triggers'
down_revision: Union[str, None] = '004_add_email_to_users'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Индекс для быстрого поиска триггеров по значению (имени сущности)
    op.create_index(
        'ix_notification_triggers_value',
        'notification_triggers',
        ['trigger_value'],
    )

    # Индекс для поиска триггеров по пользователю + тип
    op.create_index(
        'ix_notification_triggers_user_type',
        'notification_triggers',
        ['user_id', 'trigger_type', 'enabled'],
    )


def downgrade() -> None:
    op.drop_index('ix_notification_triggers_user_type', table_name='notification_triggers')
    op.drop_index('ix_notification_triggers_value', table_name='notification_triggers')

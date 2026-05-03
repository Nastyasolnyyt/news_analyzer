"""Add notification tables

Revision ID: 003_add_notifications
Revises: 
Create Date: 2026-05-03 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003_add_notifications'
down_revision = 'g8h9i0j1k2l3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create notification_settings table
    op.create_table(
        'notification_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('enabled', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('digest_frequency', sa.String(50), server_default='daily', nullable=False),
        sa.Column('quiet_hours_enabled', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('quiet_hours_start', sa.String(5), nullable=True),
        sa.Column('quiet_hours_end', sa.String(5), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
    )

    # Create notification_triggers table
    op.create_table(
        'notification_triggers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('trigger_type', sa.String(50), nullable=False),
        sa.Column('trigger_value', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('enabled', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    # Create notification_channels table
    op.create_table(
        'notification_channels',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('channel_type', sa.String(50), nullable=False),
        sa.Column('channel_address', sa.String(255), nullable=True),
        sa.Column('enabled', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('verified', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    # Create notification_sources table
    op.create_table(
        'notification_sources',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('source_type', sa.String(50), nullable=False),
        sa.Column('enabled', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    # Create notification_logs table
    op.create_table(
        'notification_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('trigger_id', sa.Integer(), nullable=True),
        sa.Column('channel_id', sa.Integer(), nullable=True),
        sa.Column('article_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(50), server_default='sent', nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['trigger_id'], ['notification_triggers.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['channel_id'], ['notification_channels.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )

    # Create trigger_channel_association table
    op.create_table(
        'trigger_channel_association',
        sa.Column('trigger_id', sa.Integer(), nullable=False),
        sa.Column('channel_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['trigger_id'], ['notification_triggers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['channel_id'], ['notification_channels.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('trigger_id', 'channel_id'),
    )


def downgrade() -> None:
    op.drop_table('trigger_channel_association')
    op.drop_table('notification_logs')
    op.drop_table('notification_sources')
    op.drop_table('notification_channels')
    op.drop_table('notification_triggers')
    op.drop_table('notification_settings')

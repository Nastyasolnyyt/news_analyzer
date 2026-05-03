from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from src.infrastructure.postgres.models.base import Base


class NotificationTrigger(Base):
    """Триггеры для отправки уведомлений (сущности, теги, события)"""
    __tablename__ = "notification_triggers"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)  # "Упоминание Газпром", "Санкции", и т.д.
    trigger_type = Column(String(50), nullable=False)  # "entity", "tag", "category"
    trigger_value = Column(String(255), nullable=False)  # значение триггера (имя сущности, тег и т.д.)
    description = Column(Text, nullable=True)
    enabled = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="notification_triggers")
    channels = relationship("NotificationChannel", secondary="trigger_channel_association", back_populates="triggers")
    logs = relationship("NotificationLog", back_populates="trigger")


class NotificationChannel(Base):
    """Каналы доставки уведомлений"""
    __tablename__ = "notification_channels"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    channel_type = Column(String(50), nullable=False)  # "app", "email", "telegram"
    channel_address = Column(String(255), nullable=True)  # email адрес или telegram username
    enabled = Column(Boolean, default=True, nullable=False)
    verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="notification_channels")
    triggers = relationship("NotificationTrigger", secondary="trigger_channel_association", back_populates="channels")
    logs = relationship("NotificationLog", back_populates="channel")


class NotificationSource(Base):
    """Источники данных для мониторинга"""
    __tablename__ = "notification_sources"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    source_type = Column(String(50), nullable=False)  # "telegram", "vk", "email"
    enabled = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="notification_sources")


class NotificationSettings(Base):
    """Общие настройки уведомлений пользователя"""
    __tablename__ = "notification_settings"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    enabled = Column(Boolean, default=True, nullable=False)
    digest_frequency = Column(String(50), default="daily", nullable=False)  # "instant", "daily", "weekly"
    quiet_hours_enabled = Column(Boolean, default=False, nullable=False)
    quiet_hours_start = Column(String(5), nullable=True)  # HH:MM
    quiet_hours_end = Column(String(5), nullable=True)  # HH:MM
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="notification_settings", uselist=False)


class NotificationLog(Base):
    """Логи отправленных уведомлений"""
    __tablename__ = "notification_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    trigger_id = Column(Integer, ForeignKey("notification_triggers.id", ondelete="SET NULL"), nullable=True)
    channel_id = Column(Integer, ForeignKey("notification_channels.id", ondelete="SET NULL"), nullable=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(50), default="sent", nullable=False)  # "sent", "failed", "read"
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User")
    trigger = relationship("NotificationTrigger", back_populates="logs")
    channel = relationship("NotificationChannel", back_populates="logs")
    article = relationship("Article")


# Association table для связи trigger и channel
from sqlalchemy import Table

trigger_channel_association = Table(
    'trigger_channel_association',
    Base.metadata,
    Column('trigger_id', Integer, ForeignKey('notification_triggers.id', ondelete='CASCADE'), primary_key=True),
    Column('channel_id', Integer, ForeignKey('notification_channels.id', ondelete='CASCADE'), primary_key=True),
)

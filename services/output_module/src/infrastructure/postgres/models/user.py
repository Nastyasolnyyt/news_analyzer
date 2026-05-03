from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship
from src.application.enums import UserRole
from src.infrastructure.postgres.connection import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    login = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default=UserRole.USER.value)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relationships
    notification_settings = relationship("NotificationSettings", back_populates="user", uselist=False)
    notification_triggers = relationship("NotificationTrigger", back_populates="user")
    notification_channels = relationship("NotificationChannel", back_populates="user")
    notification_sources = relationship("NotificationSource", back_populates="user")

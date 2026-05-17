from pydantic import BaseModel, EmailStr, ConfigDict
from typing import List, Optional
from datetime import datetime


class NotificationTriggerDTO(BaseModel):
    """Триггер для отправки уведомлений"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    trigger_type: str  # "entity", "tag", "category"
    trigger_value: str
    description: Optional[str] = None
    enabled: bool = True
    created_at: datetime
    updated_at: datetime


class NotificationChannelDTO(BaseModel):
    """Канал доставки уведомлений"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    channel_type: str  # "app", "email", "telegram"
    channel_address: Optional[str] = None
    enabled: bool = True
    verified: bool = False
    created_at: datetime
    updated_at: datetime


class NotificationSourceDTO(BaseModel):
    """Источник данных для мониторинга"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_type: str  # "telegram", "vk", "email"
    enabled: bool = True
    created_at: datetime
    updated_at: datetime


class NotificationSettingsDTO(BaseModel):
    """Общие настройки уведомлений"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    enabled: bool = True
    digest_frequency: str = "daily"  # "instant", "daily", "weekly"
    quiet_hours_enabled: bool = False
    quiet_hours_start: Optional[str] = None  # HH:MM
    quiet_hours_end: Optional[str] = None  # HH:MM
    created_at: datetime
    updated_at: datetime


class UserNotificationPreferencesUpdateDTO(BaseModel):
    """
    DTO для обновления основных предпочтений пользователя с фронтенда.
    Используется в ручке сохранения настроек на странице /notifications.
    """
    email: Optional[EmailStr] = None
    digest_frequency: Optional[str] = None  # "instant", "daily", "weekly"
    enabled: Optional[bool] = None


class NotificationSettingsUpdateDTO(BaseModel):
    """Обновление внутренних настроек уведомлений (расширенное)"""
    enabled: Optional[bool] = None
    digest_frequency: Optional[str] = None
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None


class NotificationTriggerCreateDTO(BaseModel):
    """Создание нового триггера"""
    name: str
    trigger_type: str  # "entity", "tag", "category"
    trigger_value: str
    description: Optional[str] = None
    enabled: bool = True


class NotificationTriggerUpdateDTO(BaseModel):
    """Обновление триггера"""
    name: Optional[str] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None

class NotificationChannelCreateDTO(BaseModel):
    """Создание нового канала"""
    channel_type: str  # "app", "email", "telegram"
    channel_address: Optional[str] = None
    enabled: bool = True


class NotificationChannelUpdateDTO(BaseModel):
    """Обновление канала"""
    channel_address: Optional[str] = None
    enabled: Optional[bool] = None
    verified: Optional[bool] = None

class NotificationSourceCreateDTO(BaseModel):
    """Создание нового источника"""
    source_type: str
    enabled: bool = True


class NotificationSourceUpdateDTO(BaseModel):
    """Обновление источника"""
    enabled: Optional[bool] = None


class NotificationLogDTO(BaseModel):
    """Логи отправленных уведомлений"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    trigger_id: Optional[int] = None
    channel_id: Optional[int] = None
    article_id: Optional[int] = None
    status: str  # "sent", "failed", "read"
    error_message: Optional[str] = None
    created_at: datetime


class NotificationConfigDTO(BaseModel):
    """Полная конфигурация уведомлений пользователя"""
    settings: NotificationSettingsDTO
    triggers: List[NotificationTriggerDTO]
    channels: List[NotificationChannelDTO]
    sources: List[NotificationSourceDTO]


# For dropdown/select options in UI
class NotificationTriggerOptionDTO(BaseModel):
    """Вариант триггера для UI"""
    id: str
    label: str
    description: Optional[str] = None


class NotificationChannelOptionDTO(BaseModel):
    """Вариант канала для UI"""
    id: str
    label: str


class NotificationSourceOptionDTO(BaseModel):
    """Вариант источника для UI"""
    id: str
    label: str
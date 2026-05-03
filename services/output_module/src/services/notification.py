from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, and_, func

from src.infrastructure.postgres.models import (
    NotificationTrigger,
    NotificationChannel,
    NotificationSource,
    NotificationSettings,
    NotificationLog,
    User,
)
from src.application.schemas.notification import (
    NotificationTriggerDTO,
    NotificationChannelDTO,
    NotificationSourceDTO,
    NotificationSettingsDTO,
    NotificationTriggerCreateDTO,
    NotificationTriggerUpdateDTO,
    NotificationChannelCreateDTO,
    NotificationChannelUpdateDTO,
    NotificationSourceCreateDTO,
    NotificationSourceUpdateDTO,
    NotificationSettingsUpdateDTO,
    NotificationConfigDTO,
    NotificationLogDTO,
)


class NotificationService:
    """Сервис для управления уведомлениями"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    # ===== SETTINGS =====
    
    async def get_user_settings(self, user_id: int) -> Optional[NotificationSettingsDTO]:
        """Получить настройки уведомлений пользователя"""
        stmt = select(NotificationSettings).where(NotificationSettings.user_id == user_id)
        result = await self.session.execute(stmt)
        settings = result.scalars().first()
        
        if not settings:
            # Создаем дефолтные настройки если их нет
            settings = NotificationSettings(user_id=user_id)
            self.session.add(settings)
            await self.session.flush()
        
        return NotificationSettingsDTO.from_orm(settings)
    
    async def update_user_settings(self, user_id: int, data: NotificationSettingsUpdateDTO) -> NotificationSettingsDTO:
        """Обновить настройки уведомлений"""
        stmt = select(NotificationSettings).where(NotificationSettings.user_id == user_id)
        result = await self.session.execute(stmt)
        settings = result.scalars().first()
        
        if not settings:
            settings = NotificationSettings(user_id=user_id)
            self.session.add(settings)
        
        # Обновляем поля
        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                setattr(settings, key, value)
        
        await self.session.flush()
        return NotificationSettingsDTO.from_orm(settings)
    
    # ===== TRIGGERS =====
    
    async def get_user_triggers(self, user_id: int) -> List[NotificationTriggerDTO]:
        """Получить все триггеры пользователя"""
        stmt = select(NotificationTrigger).where(
            NotificationTrigger.user_id == user_id
        ).order_by(NotificationTrigger.created_at.desc())
        result = await self.session.execute(stmt)
        triggers = result.scalars().all()
        return [NotificationTriggerDTO.from_orm(t) for t in triggers]
    
    async def get_trigger(self, trigger_id: int, user_id: int) -> Optional[NotificationTriggerDTO]:
        """Получить триггер по ID"""
        stmt = select(NotificationTrigger).where(
            and_(
                NotificationTrigger.id == trigger_id,
                NotificationTrigger.user_id == user_id
            )
        )
        result = await self.session.execute(stmt)
        trigger = result.scalars().first()
        return NotificationTriggerDTO.from_orm(trigger) if trigger else None
    
    async def create_trigger(self, user_id: int, data: NotificationTriggerCreateDTO) -> NotificationTriggerDTO:
        """Создать новый триггер"""
        trigger = NotificationTrigger(
            user_id=user_id,
            **data.dict()
        )
        self.session.add(trigger)
        await self.session.flush()
        return NotificationTriggerDTO.from_orm(trigger)
    
    async def update_trigger(self, trigger_id: int, user_id: int, data: NotificationTriggerUpdateDTO) -> Optional[NotificationTriggerDTO]:
        """Обновить триггер"""
        stmt = select(NotificationTrigger).where(
            and_(
                NotificationTrigger.id == trigger_id,
                NotificationTrigger.user_id == user_id
            )
        )
        result = await self.session.execute(stmt)
        trigger = result.scalars().first()
        
        if not trigger:
            return None
        
        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                setattr(trigger, key, value)
        
        await self.session.flush()
        return NotificationTriggerDTO.from_orm(trigger)
    
    async def delete_trigger(self, trigger_id: int, user_id: int) -> bool:
        """Удалить триггер"""
        stmt = select(NotificationTrigger).where(
            and_(
                NotificationTrigger.id == trigger_id,
                NotificationTrigger.user_id == user_id
            )
        )
        result = await self.session.execute(stmt)
        trigger = result.scalars().first()
        
        if trigger:
            await self.session.delete(trigger)
            await self.session.flush()
            return True
        return False
    
    # ===== CHANNELS =====
    
    async def get_user_channels(self, user_id: int) -> List[NotificationChannelDTO]:
        """Получить все каналы пользователя"""
        stmt = select(NotificationChannel).where(
            NotificationChannel.user_id == user_id
        ).order_by(NotificationChannel.created_at.desc())
        result = await self.session.execute(stmt)
        channels = result.scalars().all()
        return [NotificationChannelDTO.from_orm(c) for c in channels]
    
    async def get_channel(self, channel_id: int, user_id: int) -> Optional[NotificationChannelDTO]:
        """Получить канал по ID"""
        stmt = select(NotificationChannel).where(
            and_(
                NotificationChannel.id == channel_id,
                NotificationChannel.user_id == user_id
            )
        )
        result = await self.session.execute(stmt)
        channel = result.scalars().first()
        return NotificationChannelDTO.from_orm(channel) if channel else None
    
    async def create_channel(self, user_id: int, data: NotificationChannelCreateDTO) -> NotificationChannelDTO:
        """Создать новый канал"""
        channel = NotificationChannel(
            user_id=user_id,
            **data.dict()
        )
        self.session.add(channel)
        await self.session.flush()
        return NotificationChannelDTO.from_orm(channel)
    
    async def update_channel(self, channel_id: int, user_id: int, data: NotificationChannelUpdateDTO) -> Optional[NotificationChannelDTO]:
        """Обновить канал"""
        stmt = select(NotificationChannel).where(
            and_(
                NotificationChannel.id == channel_id,
                NotificationChannel.user_id == user_id
            )
        )
        result = await self.session.execute(stmt)
        channel = result.scalars().first()
        
        if not channel:
            return None
        
        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                setattr(channel, key, value)
        
        await self.session.flush()
        return NotificationChannelDTO.from_orm(channel)
    
    async def delete_channel(self, channel_id: int, user_id: int) -> bool:
        """Удалить канал"""
        stmt = select(NotificationChannel).where(
            and_(
                NotificationChannel.id == channel_id,
                NotificationChannel.user_id == user_id
            )
        )
        result = await self.session.execute(stmt)
        channel = result.scalars().first()
        
        if channel:
            await self.session.delete(channel)
            await self.session.flush()
            return True
        return False
    
    # ===== SOURCES =====
    
    async def get_user_sources(self, user_id: int) -> List[NotificationSourceDTO]:
        """Получить все источники пользователя"""
        stmt = select(NotificationSource).where(
            NotificationSource.user_id == user_id
        ).order_by(NotificationSource.created_at.desc())
        result = await self.session.execute(stmt)
        sources = result.scalars().all()
        return [NotificationSourceDTO.from_orm(s) for s in sources]
    
    async def create_source(self, user_id: int, data: NotificationSourceCreateDTO) -> NotificationSourceDTO:
        """Создать новый источник"""
        source = NotificationSource(
            user_id=user_id,
            **data.dict()
        )
        self.session.add(source)
        await self.session.flush()
        return NotificationSourceDTO.from_orm(source)
    
    async def update_source(self, source_id: int, user_id: int, data: NotificationSourceUpdateDTO) -> Optional[NotificationSourceDTO]:
        """Обновить источник"""
        stmt = select(NotificationSource).where(
            and_(
                NotificationSource.id == source_id,
                NotificationSource.user_id == user_id
            )
        )
        result = await self.session.execute(stmt)
        source = result.scalars().first()
        
        if not source:
            return None
        
        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                setattr(source, key, value)
        
        await self.session.flush()
        return NotificationSourceDTO.from_orm(source)
    
    # ===== CONFIG =====
    
    async def get_user_config(self, user_id: int) -> NotificationConfigDTO:
        """Получить полную конфигурацию уведомлений"""
        settings = await self.get_user_settings(user_id)
        triggers = await self.get_user_triggers(user_id)
        channels = await self.get_user_channels(user_id)
        sources = await self.get_user_sources(user_id)
        
        return NotificationConfigDTO(
            settings=settings,
            triggers=triggers,
            channels=channels,
            sources=sources,
        )

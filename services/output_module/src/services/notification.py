from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from src.infrastructure.postgres.models import (
    NotificationTrigger,
    NotificationChannel,
    NotificationSource,
    NotificationSettings,
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
)


def _settings_to_dto(s: NotificationSettings) -> NotificationSettingsDTO:
    return NotificationSettingsDTO(
        id=s.id,
        enabled=s.enabled,
        digest_frequency=s.digest_frequency,
        quiet_hours_enabled=s.quiet_hours_enabled,
        quiet_hours_start=s.quiet_hours_start,
        quiet_hours_end=s.quiet_hours_end,
        created_at=s.created_at,
        updated_at=s.updated_at,
    )


def _trigger_to_dto(t: NotificationTrigger) -> NotificationTriggerDTO:
    return NotificationTriggerDTO(
        id=t.id,
        name=t.name,
        trigger_type=t.trigger_type,
        trigger_value=t.trigger_value,
        description=t.description,
        enabled=t.enabled,
        created_at=t.created_at,
        updated_at=t.updated_at,
    )


def _channel_to_dto(c: NotificationChannel) -> NotificationChannelDTO:
    return NotificationChannelDTO(
        id=c.id,
        channel_type=c.channel_type,
        channel_address=c.channel_address,
        enabled=c.enabled,
        verified=c.verified,
        created_at=c.created_at,
        updated_at=c.updated_at,
    )


def _source_to_dto(s: NotificationSource) -> NotificationSourceDTO:
    return NotificationSourceDTO(
        id=s.id,
        source_type=s.source_type,
        enabled=s.enabled,
        created_at=s.created_at,
        updated_at=s.updated_at,
    )


class NotificationService:
    """Сервис для управления уведомлениями"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def _ensure_user_exists(self, user_id: int) -> bool:
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().first() is not None

    # ===== SETTINGS =====

    async def get_user_settings(self, user_id: int) -> Optional[NotificationSettingsDTO]:
        if not await self._ensure_user_exists(user_id):
            return None

        stmt = select(NotificationSettings).where(NotificationSettings.user_id == user_id)
        result = await self.session.execute(stmt)
        settings = result.scalars().first()

        if not settings:
            settings = NotificationSettings(user_id=user_id)
            self.session.add(settings)
            await self.session.commit()
            await self.session.refresh(settings)

        return _settings_to_dto(settings)

    async def update_user_settings(self, user_id: int, data: NotificationSettingsUpdateDTO) -> Optional[NotificationSettingsDTO]:
        if not await self._ensure_user_exists(user_id):
            return None

        stmt = select(NotificationSettings).where(NotificationSettings.user_id == user_id)
        result = await self.session.execute(stmt)
        settings = result.scalars().first()

        if not settings:
            settings = NotificationSettings(user_id=user_id)
            self.session.add(settings)

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                setattr(settings, key, value)

        await self.session.commit()
        await self.session.refresh(settings)
        return _settings_to_dto(settings)

    # ===== TRIGGERS =====

    async def get_user_triggers(self, user_id: int) -> List[NotificationTriggerDTO]:
        stmt = select(NotificationTrigger).where(
            NotificationTrigger.user_id == user_id
        ).order_by(NotificationTrigger.created_at.desc())
        result = await self.session.execute(stmt)
        triggers = result.scalars().all()
        return [_trigger_to_dto(t) for t in triggers]

    async def get_trigger(self, trigger_id: int, user_id: int) -> Optional[NotificationTriggerDTO]:
        stmt = select(NotificationTrigger).where(
            and_(
                NotificationTrigger.id == trigger_id,
                NotificationTrigger.user_id == user_id
            )
        )
        result = await self.session.execute(stmt)
        trigger = result.scalars().first()
        return _trigger_to_dto(trigger) if trigger else None

    async def create_trigger(self, user_id: int, data: NotificationTriggerCreateDTO) -> NotificationTriggerDTO:
        trigger = NotificationTrigger(user_id=user_id, **data.dict())
        self.session.add(trigger)
        await self.session.commit()
        await self.session.refresh(trigger)
        return _trigger_to_dto(trigger)

    async def update_trigger(self, trigger_id: int, user_id: int, data: NotificationTriggerUpdateDTO) -> Optional[NotificationTriggerDTO]:
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

        await self.session.commit()
        await self.session.refresh(trigger)
        return _trigger_to_dto(trigger)

    async def delete_trigger(self, trigger_id: int, user_id: int) -> bool:
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
            await self.session.commit()
            return True
        return False

    # ===== CHANNELS =====

    async def get_user_channels(self, user_id: int) -> List[NotificationChannelDTO]:
        stmt = select(NotificationChannel).where(
            NotificationChannel.user_id == user_id
        ).order_by(NotificationChannel.created_at.desc())
        result = await self.session.execute(stmt)
        channels = result.scalars().all()
        return [_channel_to_dto(c) for c in channels]

    async def get_channel(self, channel_id: int, user_id: int) -> Optional[NotificationChannelDTO]:
        stmt = select(NotificationChannel).where(
            and_(
                NotificationChannel.id == channel_id,
                NotificationChannel.user_id == user_id
            )
        )
        result = await self.session.execute(stmt)
        channel = result.scalars().first()
        return _channel_to_dto(channel) if channel else None

    async def create_channel(self, user_id: int, data: NotificationChannelCreateDTO) -> NotificationChannelDTO:
        channel = NotificationChannel(user_id=user_id, **data.dict())
        self.session.add(channel)
        await self.session.commit()
        await self.session.refresh(channel)
        return _channel_to_dto(channel)

    async def update_channel(self, channel_id: int, user_id: int, data: NotificationChannelUpdateDTO) -> Optional[NotificationChannelDTO]:
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

        await self.session.commit()
        await self.session.refresh(channel)
        return _channel_to_dto(channel)

    async def delete_channel(self, channel_id: int, user_id: int) -> bool:
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
            await self.session.commit()
            return True
        return False

    # ===== SOURCES =====

    async def get_user_sources(self, user_id: int) -> List[NotificationSourceDTO]:
        stmt = select(NotificationSource).where(
            NotificationSource.user_id == user_id
        ).order_by(NotificationSource.created_at.desc())
        result = await self.session.execute(stmt)
        sources = result.scalars().all()
        return [_source_to_dto(s) for s in sources]

    async def create_source(self, user_id: int, data: NotificationSourceCreateDTO) -> NotificationSourceDTO:
        source = NotificationSource(user_id=user_id, **data.dict())
        self.session.add(source)
        await self.session.commit()
        await self.session.refresh(source)
        return _source_to_dto(source)

    async def update_source(self, source_id: int, user_id: int, data: NotificationSourceUpdateDTO) -> Optional[NotificationSourceDTO]:
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

        await self.session.commit()
        await self.session.refresh(source)
        return _source_to_dto(source)

    # ===== CONFIG =====

    async def get_user_config(self, user_id: int) -> NotificationConfigDTO:
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
    
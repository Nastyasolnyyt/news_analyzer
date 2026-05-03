from typing import List
from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, HTTPException, Depends

from src.services.notification import NotificationService
from src.application.schemas.notification import (
    NotificationTriggerDTO,
    NotificationChannelDTO,
    NotificationSourceDTO,
    NotificationSettingsDTO,
    NotificationConfigDTO,
    NotificationTriggerCreateDTO,
    NotificationTriggerUpdateDTO,
    NotificationChannelCreateDTO,
    NotificationChannelUpdateDTO,
    NotificationSourceCreateDTO,
    NotificationSourceUpdateDTO,
    NotificationSettingsUpdateDTO,
)


ROUTER = APIRouter(prefix="/notifications", route_class=DishkaRoute)


# ===== SETTINGS ENDPOINTS =====

@ROUTER.get(
    "/settings",
    response_model=NotificationSettingsDTO,
    summary="Получить настройки уведомлений",
)
async def get_notification_settings(
    notification_service: FromDishka[NotificationService],
    user_id: int = 1,  # TODO: получить из authentication
) -> NotificationSettingsDTO:
    """Получить настройки уведомлений текущего пользователя"""
    settings = await notification_service.get_user_settings(user_id)
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")
    return settings


@ROUTER.put(
    "/settings",
    response_model=NotificationSettingsDTO,
    summary="Обновить настройки уведомлений",
)
async def update_notification_settings(
    notification_service: FromDishka[NotificationService],
    data: NotificationSettingsUpdateDTO,
    user_id: int = 1,  # TODO: получить из authentication
) -> NotificationSettingsDTO:
    """Обновить настройки уведомлений"""
    return await notification_service.update_user_settings(user_id, data)


# ===== TRIGGERS ENDPOINTS =====

@ROUTER.get(
    "/triggers",
    response_model=List[NotificationTriggerDTO],
    summary="Получить триггеры уведомлений",
)
async def get_triggers(
    notification_service: FromDishka[NotificationService],
    user_id: int = 1,  # TODO: получить из authentication
) -> List[NotificationTriggerDTO]:
    """Получить список всех триггеров пользователя"""
    return await notification_service.get_user_triggers(user_id)


@ROUTER.post(
    "/triggers",
    response_model=NotificationTriggerDTO,
    summary="Создать новый триггер",
)
async def create_trigger(
    notification_service: FromDishka[NotificationService],
    data: NotificationTriggerCreateDTO,
    user_id: int = 1,  # TODO: получить из authentication
) -> NotificationTriggerDTO:
    """Создать новый триггер для уведомлений"""
    return await notification_service.create_trigger(user_id, data)


@ROUTER.get(
    "/triggers/{trigger_id}",
    response_model=NotificationTriggerDTO,
    summary="Получить триггер по ID",
)
async def get_trigger(
    notification_service: FromDishka[NotificationService],
    trigger_id: int,
    user_id: int = 1,  # TODO: получить из authentication
) -> NotificationTriggerDTO:
    """Получить триггер по ID"""
    trigger = await notification_service.get_trigger(trigger_id, user_id)
    if not trigger:
        raise HTTPException(status_code=404, detail="Trigger not found")
    return trigger


@ROUTER.put(
    "/triggers/{trigger_id}",
    response_model=NotificationTriggerDTO,
    summary="Обновить триггер",
)
async def update_trigger(
    notification_service: FromDishka[NotificationService],
    trigger_id: int,
    data: NotificationTriggerUpdateDTO,
    user_id: int = 1,  # TODO: получить из authentication
) -> NotificationTriggerDTO:
    """Обновить триггер"""
    trigger = await notification_service.update_trigger(trigger_id, user_id, data)
    if not trigger:
        raise HTTPException(status_code=404, detail="Trigger not found")
    return trigger


@ROUTER.delete(
    "/triggers/{trigger_id}",
    summary="Удалить триггер",
)
async def delete_trigger(
    notification_service: FromDishka[NotificationService],
    trigger_id: int,
    user_id: int = 1,  # TODO: получить из authentication
) -> dict:
    """Удалить триггер"""
    success = await notification_service.delete_trigger(trigger_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Trigger not found")
    return {"message": "Trigger deleted"}


# ===== CHANNELS ENDPOINTS =====

@ROUTER.get(
    "/channels",
    response_model=List[NotificationChannelDTO],
    summary="Получить каналы уведомлений",
)
async def get_channels(
    notification_service: FromDishka[NotificationService],
    user_id: int = 1,  # TODO: получить из authentication
) -> List[NotificationChannelDTO]:
    """Получить список всех каналов пользователя"""
    return await notification_service.get_user_channels(user_id)


@ROUTER.post(
    "/channels",
    response_model=NotificationChannelDTO,
    summary="Создать новый канал",
)
async def create_channel(
    notification_service: FromDishka[NotificationService],
    data: NotificationChannelCreateDTO,
    user_id: int = 1,  # TODO: получить из authentication
) -> NotificationChannelDTO:
    """Создать новый канал доставки"""
    return await notification_service.create_channel(user_id, data)


@ROUTER.get(
    "/channels/{channel_id}",
    response_model=NotificationChannelDTO,
    summary="Получить канал по ID",
)
async def get_channel(
    notification_service: FromDishka[NotificationService],
    channel_id: int,
    user_id: int = 1,  # TODO: получить из authentication
) -> NotificationChannelDTO:
    """Получить канал по ID"""
    channel = await notification_service.get_channel(channel_id, user_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    return channel


@ROUTER.put(
    "/channels/{channel_id}",
    response_model=NotificationChannelDTO,
    summary="Обновить канал",
)
async def update_channel(
    notification_service: FromDishka[NotificationService],
    channel_id: int,
    data: NotificationChannelUpdateDTO,
    user_id: int = 1,  # TODO: получить из authentication
) -> NotificationChannelDTO:
    """Обновить канал"""
    channel = await notification_service.update_channel(channel_id, user_id, data)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    return channel


@ROUTER.delete(
    "/channels/{channel_id}",
    summary="Удалить канал",
)
async def delete_channel(
    notification_service: FromDishka[NotificationService],
    channel_id: int,
    user_id: int = 1,  # TODO: получить из authentication
) -> dict:
    """Удалить канал"""
    success = await notification_service.delete_channel(channel_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Channel not found")
    return {"message": "Channel deleted"}


# ===== SOURCES ENDPOINTS =====

@ROUTER.get(
    "/sources",
    response_model=List[NotificationSourceDTO],
    summary="Получить источники",
)
async def get_sources(
    notification_service: FromDishka[NotificationService],
    user_id: int = 1,  # TODO: получить из authentication
) -> List[NotificationSourceDTO]:
    """Получить список всех источников пользователя"""
    return await notification_service.get_user_sources(user_id)


@ROUTER.post(
    "/sources",
    response_model=NotificationSourceDTO,
    summary="Создать новый источник",
)
async def create_source(
    notification_service: FromDishka[NotificationService],
    data: NotificationSourceCreateDTO,
    user_id: int = 1,  # TODO: получить из authentication
) -> NotificationSourceDTO:
    """Создать новый источник"""
    return await notification_service.create_source(user_id, data)


@ROUTER.put(
    "/sources/{source_id}",
    response_model=NotificationSourceDTO,
    summary="Обновить источник",
)
async def update_source(
    notification_service: FromDishka[NotificationService],
    source_id: int,
    data: NotificationSourceUpdateDTO,
    user_id: int = 1,  # TODO: получить из authentication
) -> NotificationSourceDTO:
    """Обновить источник"""
    source = await notification_service.update_source(source_id, user_id, data)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return source


# ===== CONFIG ENDPOINTS =====

@ROUTER.get(
    "/config",
    response_model=NotificationConfigDTO,
    summary="Получить полную конфигурацию уведомлений",
)
async def get_notification_config(
    notification_service: FromDishka[NotificationService],
    user_id: int = 1,  # TODO: получить из authentication
) -> NotificationConfigDTO:
    """Получить полную конфигурацию (настройки, триггеры, каналы, источники)"""
    return await notification_service.get_user_config(user_id)

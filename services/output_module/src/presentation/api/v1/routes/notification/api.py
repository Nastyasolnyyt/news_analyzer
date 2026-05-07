from typing import List
from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, HTTPException, Depends, status

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
from src.presentation.api.v1.routes.auth_dependencies import get_current_user
from src.application.schemas.user import UserDTO


ROUTER = APIRouter(prefix="/notifications", route_class=DishkaRoute)


def get_current_user_id(current_user: UserDTO = Depends(get_current_user)) -> int:
    """Получает ID текущего пользователя из JWT токена"""
    return current_user.id


# ===== SETTINGS ENDPOINTS =====

@ROUTER.get(
    "/settings",
    response_model=NotificationSettingsDTO,
    summary="Получить настройки уведомлений",
)
async def get_notification_settings(
    notification_service: FromDishka[NotificationService],
    user_id: int = Depends(get_current_user_id),
) -> NotificationSettingsDTO:
    """Получить настройки уведомлений текущего пользователя"""
    settings = await notification_service.get_user_settings(user_id)
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id={user_id} not found or settings not initialized"
        )
    return settings


@ROUTER.put(
    "/settings",
    response_model=NotificationSettingsDTO,
    summary="Обновить настройки уведомлений",
)
async def update_notification_settings(
    notification_service: FromDishka[NotificationService],
    data: NotificationSettingsUpdateDTO,
    user_id: int = Depends(get_current_user_id),
) -> NotificationSettingsDTO:
    """Обновить настройки уведомлений"""
    settings = await notification_service.update_user_settings(user_id, data)
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id={user_id} not found"
        )
    return settings


# ===== TRIGGERS ENDPOINTS =====

@ROUTER.get(
    "/triggers",
    response_model=List[NotificationTriggerDTO],
    summary="Получить триггеры уведомлений",
)
async def get_triggers(
    notification_service: FromDishka[NotificationService],
    user_id: int = Depends(get_current_user_id),
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
    user_id: int = Depends(get_current_user_id),
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
    user_id: int = Depends(get_current_user_id),
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
    user_id: int = Depends(get_current_user_id),
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
    user_id: int = Depends(get_current_user_id),
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
    user_id: int = Depends(get_current_user_id),
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
    user_id: int = Depends(get_current_user_id),
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
    user_id: int = Depends(get_current_user_id),
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
    user_id: int = Depends(get_current_user_id),
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
    user_id: int = Depends(get_current_user_id),
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
    user_id: int = Depends(get_current_user_id),
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
    user_id: int = Depends(get_current_user_id),
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
    user_id: int = Depends(get_current_user_id),
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
    user_id: int = Depends(get_current_user_id),
) -> NotificationConfigDTO:
    """Получить полную конфигурацию (настройки, триггеры, каналы, источники)"""
    return await notification_service.get_user_config(user_id)


# ===== TEST ENDPOINTS =====

@ROUTER.post(
    "/test-email",
    response_model=dict,
    summary="Отправить тестовое email уведомление",
)
async def send_test_email(
    notification_service: FromDishka[NotificationService],
    user_id: int = Depends(get_current_user_id),
) -> dict:
    """
    Отправить тестовое email уведомление на адрес, 
    указанный в настройках пользователя
    """
    from src.services.email_service import get_email_service
    
    try:
        # Получаем email канал пользователя
        channels = await notification_service.get_user_channels(user_id)
        email_channel = next(
            (c for c in channels if c.channel_type == "email" and c.channel_address),
            None
        )
        
        if not email_channel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email channel not configured"
            )
        
        # Отправляем тестовое письмо
        email_service = get_email_service()
        success = await email_service.send_test_email(to_email=email_channel.channel_address)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send test email"
            )
        
        return {
            "message": "Test email sent successfully",
            "to": email_channel.channel_address,
            "status": "sent"
        }
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in send_test_email: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

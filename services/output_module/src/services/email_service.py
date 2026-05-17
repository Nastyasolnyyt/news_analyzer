"""
Email Service для отправки уведомлений через SMTP
ИСПРАВЛЕНО:
1. SMTP_ENABLED теперь по умолчанию True если заданы учётные данные
2. Улучшена диагностика ошибок (отдельное исключение для Auth)
3. Добавлен метод is_configured() для быстрой проверки
"""

import os
import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Сервис для отправки email уведомлений"""

    def __init__(
        self,
        smtp_host: str = None,
        smtp_port: int = None,
        smtp_username: str = None,
        smtp_password: str = None,
        from_email: str = None,
        from_name: str = None,
        enabled: bool = None,
    ):
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = smtp_username or os.getenv("SMTP_USERNAME", "")
        self.smtp_password = smtp_password or os.getenv("SMTP_PASSWORD", "")
        self.from_email = from_email or os.getenv("SMTP_FROM_EMAIL") or self.smtp_username
        self.from_name = from_name or os.getenv("SMTP_FROM_NAME", "Signal Desk")

        # ИСПРАВЛЕНО: enabled = True если есть логин/пароль, если явно не отключено
        smtp_enabled_env = os.getenv("SMTP_ENABLED", "true").lower()
        if enabled is not None:
            self.enabled = enabled
        else:
            self.enabled = smtp_enabled_env == "true"

        # Логируем статус при инициализации
        if self.is_configured():
            logger.info(
                f"EmailService инициализирован: host={self.smtp_host}:{self.smtp_port}, "
                f"user={self.smtp_username}, from={self.from_email}"
            )
        else:
            logger.warning(
                "EmailService: SMTP не настроен (нет SMTP_USERNAME или SMTP_PASSWORD)"
            )

    def is_configured(self) -> bool:
        """Проверяет, настроен ли SMTP корректно."""
        return bool(self.smtp_username and self.smtp_password and self.enabled)

    async def send_notification_email(
        self,
        to_email: str,
        subject: str,
        article_title: str,
        article_summary: str,
        article_link: str = None,
        entity_name: str = None,
        entity_type: str = None,
        risk_level: str = None,
        sentiment: str = None,
    ) -> bool:
        """
        Отправить email уведомление о новой статье.
        """
        if not self.enabled:
            logger.warning(f"Email сервис отключён (SMTP_ENABLED=false). Пропускаю письмо на {to_email}")
            return False

        if not self.smtp_username or not self.smtp_password:
            logger.error(
                "SMTP не настроен: отсутствует SMTP_USERNAME или SMTP_PASSWORD. "
                "Проверьте переменные окружения в .env файле."
            )
            return False

        if not to_email:
            logger.error("Не указан адрес получателя")
            return False

        try:
            html_content = self._generate_html_email(
                article_title=article_title,
                article_summary=article_summary,
                article_link=article_link,
                entity_name=entity_name,
                entity_type=entity_type,
                risk_level=risk_level,
                sentiment=sentiment,
            )

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self._send_smtp_email,
                to_email,
                subject,
                html_content,
            )

            logger.info(f"✅ Email отправлен на {to_email}: {subject}")
            return True

        except smtplib.SMTPAuthenticationError:
            logger.error(
                f"❌ SMTP аутентификация не удалась для {self.smtp_username}. "
                f"Проверьте пароль приложения Gmail (App Password)."
            )
            return False
        except Exception as e:
            logger.error(f"❌ Не удалось отправить email на {to_email}: {e}")
            return False

    def _send_smtp_email(self, to_email: str, subject: str, html_content: str):
        """Синхронная отправка email через SMTP"""
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{self.from_name} <{self.from_email}>"
        message["To"] = to_email

        html_part = MIMEText(html_content, "html", "utf-8")
        message.attach(html_part)

        with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(message)

        logger.debug(f"📧 SMTP сообщение успешно отправлено на {to_email}")

    def _generate_html_email(
        self,
        article_title: str,
        article_summary: str,
        article_link: str = None,
        entity_name: str = None,
        entity_type: str = None,
        risk_level: str = None,
        sentiment: str = None,
    ) -> str:
        """Генерирует HTML для письма"""

        risk_colors = {
            "high": "#f87171",
            "medium": "#fb923c",
            "low": "#86efac",
        }
        risk_color = risk_colors.get(risk_level, "#d1d5db")
        risk_label = {"high": "Высокий", "medium": "Средний", "low": "Низкий"}.get(
            risk_level, "Неизвестен"
        )

        sentiment_colors = {
            "positive": "#86efac",
            "negative": "#f87171",
            "neutral": "#d1d5db",
        }
        sentiment_color = sentiment_colors.get(sentiment, "#d1d5db")
        sentiment_label = {
            "positive": "Позитивная",
            "negative": "Негативная",
            "neutral": "Нейтральная",
        }.get(sentiment, "Не определена")

        entity_section = ""
        if entity_name and entity_type:
            entity_type_label = "Организация" if entity_type in ("organization", "ORG") else "Персона"
            entity_section = f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">
                    <strong>Отслеживаемая сущность:</strong> {entity_name} ({entity_type_label})
                </td>
            </tr>
            """

        link_section = ""
        if article_link:
            link_section = f"""
            <tr>
                <td style="padding: 12px; text-align: center;">
                    <a href="{article_link}" style="
                        background-color: #3b82f6;
                        color: white;
                        padding: 10px 20px;
                        text-decoration: none;
                        border-radius: 6px;
                        display: inline-block;
                    ">Читать полностью</a>
                </td>
            </tr>
            """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; background: #f9fafb; padding: 20px;">
                <div style="background: linear-gradient(120deg, #4f8aff, #1317ff); color: white; padding: 20px; border-radius: 12px 12px 0 0; text-align: center;">
                    <h1 style="margin: 0; font-size: 24px;">🔔 Signal Desk</h1>
                    <p style="margin: 8px 0 0; opacity: 0.9;">Уведомление о новой статье</p>
                </div>
                <div style="background: white; padding: 20px; border-radius: 0 0 12px 12px;">
                    <h2 style="margin-top: 0; margin-bottom: 16px; font-size: 20px; line-height: 1.4;">
                        {article_title}
                    </h2>
                    <p style="margin: 16px 0; color: #666;">
                        {article_summary}
                    </p>
                    <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">
                                <strong>Уровень риска:</strong>
                                <span style="background-color: {risk_color}; color: white; padding: 4px 10px; border-radius: 4px; display: inline-block; margin-left: 8px;">{risk_label}</span>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">
                                <strong>Тональность:</strong>
                                <span style="background-color: {sentiment_color}; color: white; padding: 4px 10px; border-radius: 4px; display: inline-block; margin-left: 8px;">{sentiment_label}</span>
                            </td>
                        </tr>
                        {entity_section}
                    </table>
                    {link_section}
                    <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
                    <p style="font-size: 12px; color: #999; text-align: center; margin: 0;">
                        Вы получили это письмо, потому что отслеживаете упоминания указанных организаций и персон.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        return html

    async def send_test_email(self, to_email: str) -> bool:
        """Отправить тестовое письмо"""
        if not self.is_configured():
            logger.error(
                "Невозможно отправить тестовое письмо: SMTP не настроен. "
                "Убедитесь что в .env заданы SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD."
            )
            return False

        return await self.send_notification_email(
            to_email=to_email,
            subject="✅ Тестовое письмо — Signal Desk уведомления работают!",
            article_title="Это тестовое письмо от Signal Desk",
            article_summary=(
                "Если вы видите это письмо, система уведомлений настроена корректно. "
                "Вы будете получать уведомления когда отслеживаемые вами сущности "
                "упоминаются в новых статьях."
            ),
            risk_level="low",
            sentiment="positive",
        )


# Глобальный синглтон
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """Получить экземпляр Email Service (синглтон)"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service


async def send_email(
    to_email: str,
    subject: str,
    article_title: str,
    article_summary: str,
    **kwargs,
) -> bool:
    """Удобная функция для отправки email"""
    service = get_email_service()
    return await service.send_notification_email(
        to_email=to_email,
        subject=subject,
        article_title=article_title,
        article_summary=article_summary,
        **kwargs,
    )
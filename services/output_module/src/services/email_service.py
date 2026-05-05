"""
Email Service для отправки уведомлений через SMTP
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
        enabled: bool = True,
    ):
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = smtp_username or os.getenv("SMTP_USERNAME", "")
        self.smtp_password = smtp_password or os.getenv("SMTP_PASSWORD", "")
        self.from_email = from_email or os.getenv("SMTP_FROM_EMAIL", "noreply@signaldesk.io")
        self.from_name = from_name or os.getenv("SMTP_FROM_NAME", "Signal Desk")
        self.enabled = enabled and os.getenv("SMTP_ENABLED", "true").lower() == "true"

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
        Отправить email уведомление о новой статье

        Args:
            to_email: Email адрес получателя
            subject: Тема письма
            article_title: Заголовок статьи
            article_summary: Краткое описание
            article_link: Ссылка на статью
            entity_name: Название сущности (организация/персона)
            entity_type: Тип сущности (organization/person)
            risk_level: Уровень риска (high/medium/low)
            sentiment: Тональность (positive/negative/neutral)

        Returns:
            True если отправлено успешно, False если ошибка
        """

        if not self.enabled:
            logger.warning(f"Email service disabled. Skipping email to {to_email}")
            return False

        if not self.smtp_username or not self.smtp_password:
            logger.error("SMTP credentials not configured")
            return False

        try:
            # Генерируем HTML письмо
            html_content = self._generate_html_email(
                article_title=article_title,
                article_summary=article_summary,
                article_link=article_link,
                entity_name=entity_name,
                entity_type=entity_type,
                risk_level=risk_level,
                sentiment=sentiment,
            )

            # Отправляем в отдельном потоке (неблокирующее)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self._send_smtp_email,
                to_email,
                subject,
                html_content,
            )

            logger.info(f"✅ Email sent to {to_email}: {subject}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to send email to {to_email}: {e}")
            return False

    def _send_smtp_email(self, to_email: str, subject: str, html_content: str):
        """Синхронная отправка email через SMTP"""
        try:
            # Создаем письмо
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email

            # HTML часть
            html_part = MIMEText(html_content, "html", "utf-8")
            message.attach(html_part)

            # Отправляем
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(message)

            logger.debug(f"📧 SMTP message sent successfully to {to_email}")

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP Authentication failed: {e}")
            raise
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error sending email: {e}")
            raise

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

        # Определяем цвета для уровня риска
        risk_colors = {
            "high": "#f87171",
            "medium": "#fb923c",
            "low": "#86efac",
        }
        risk_color = risk_colors.get(risk_level, "#d1d5db")
        risk_label = {"high": "Высокий", "medium": "Средний", "low": "Низкий"}.get(
            risk_level, "Неизвестен"
        )

        # Определяем цвета для тональности
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
            entity_type_label = "Организация" if entity_type == "organization" else "Персона"
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
                <!-- Header -->
                <div style="background: linear-gradient(120deg, #4f8aff, #1317ff); color: white; padding: 20px; border-radius: 12px 12px 0 0; text-align: center;">
                    <h1 style="margin: 0; font-size: 24px;">🔔 Signal Desk</h1>
                    <p style="margin: 8px 0 0; opacity: 0.9;">Уведомление о новой статье</p>
                </div>

                <!-- Content -->
                <div style="background: white; padding: 20px; border-radius: 0 0 12px 12px;">
                    <h2 style="margin-top: 0; margin-bottom: 16px; font-size: 20px; line-height: 1.4;">
                        {article_title}
                    </h2>

                    <p style="margin: 16px 0; color: #666;">
                        {article_summary}
                    </p>

                    <!-- Metrics Table -->
                    <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">
                                <strong>Уровень риска:</strong>
                                <span style="
                                    background-color: {risk_color};
                                    color: white;
                                    padding: 4px 10px;
                                    border-radius: 4px;
                                    display: inline-block;
                                    margin-left: 8px;
                                ">{risk_label}</span>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">
                                <strong>Тональность:</strong>
                                <span style="
                                    background-color: {sentiment_color};
                                    color: white;
                                    padding: 4px 10px;
                                    border-radius: 4px;
                                    display: inline-block;
                                    margin-left: 8px;
                                ">{sentiment_label}</span>
                            </td>
                        </tr>
                        {entity_section}
                    </table>

                    {link_section}

                    <!-- Footer -->
                    <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
                    <p style="font-size: 12px; color: #999; text-align: center; margin: 0;">
                        Вы получили это письмо, потому что отслеживаете упоминания указанных организаций и персон.
                        <br>
                        <a href="#" style="color: #3b82f6; text-decoration: none;">Управлять подписками</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        return html

    async def send_test_email(self, to_email: str) -> bool:
        """Отправить тестовое письмо"""
        return await self.send_notification_email(
            to_email=to_email,
            subject="Тестовое письмо - Signal Desk уведомления работают!",
            article_title="Это тестовое письмо",
            article_summary="Если вы видите это письмо, то система уведомлений работает корректно.",
            risk_level="low",
            sentiment="positive",
        )


# Глобальный экземпляр
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """Получить экземпляр Email Service"""
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

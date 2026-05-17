"""
Email Service — отправка через локальный Postfix relay (mailrelay:25).

Порт 587/465 на большинстве VPS заблокирован провайдером.
Postfix отправляет напрямую через MX-записи домена получателя по порту 25,
который открыт для исходящих соединений.

Никакой авторизации внутри Docker-сети не требуется.
"""

import asyncio
import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

logger = logging.getLogger(__name__)


class EmailService:
    """Сервис отправки email через локальный Postfix SMTP relay."""

    def __init__(self):
        # Хост Postfix-контейнера внутри Docker-сети
        self.smtp_host = os.getenv("SMTP_HOST", "mailrelay")
        self.smtp_port = int(os.getenv("SMTP_PORT", "25"))

        # От кого будут уходить письма
        self.from_email = os.getenv(
            "SMTP_FROM_EMAIL",
            f"noreply@{os.getenv('MAIL_DOMAIN', 'signal-desk.local')}"
        )
        self.from_name = os.getenv("SMTP_FROM_NAME", "Signal Desk")

        logger.info(
            "EmailService инициализирован: relay=%s:%s, from=%s",
            self.smtp_host, self.smtp_port, self.from_email,
        )

    def is_configured(self) -> bool:
        """Relay всегда доступен если контейнер запущен."""
        return True

    # ------------------------------------------------------------------
    # Публичные методы
    # ------------------------------------------------------------------

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
        if not to_email:
            logger.error("Не указан адрес получателя")
            return False

        html = self._build_html(
            article_title=article_title,
            article_summary=article_summary,
            article_link=article_link,
            entity_name=entity_name,
            entity_type=entity_type,
            risk_level=risk_level,
            sentiment=sentiment,
        )

        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self._send,
                to_email,
                subject,
                html,
            )
            logger.info("✅ Email отправлен на %s: %s", to_email, subject)
            return True
        except Exception as exc:
            logger.error("❌ Не удалось отправить email на %s: %s", to_email, exc)
            return False

    async def send_test_email(self, to_email: str) -> bool:
        return await self.send_notification_email(
            to_email=to_email,
            subject="✅ Тестовое письмо — Signal Desk",
            article_title="Система уведомлений работает!",
            article_summary=(
                "Если вы видите это письмо, Postfix relay настроен корректно. "
                "Уведомления об упоминаниях сущностей будут приходить на этот адрес."
            ),
            risk_level="low",
            sentiment="positive",
        )

    # ------------------------------------------------------------------
    # Внутренние методы
    # ------------------------------------------------------------------

    def _send(self, to_email: str, subject: str, html: str) -> None:
        """Синхронная отправка через локальный Postfix (без TLS, без авторизации)."""
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{self.from_name} <{self.from_email}>"
        msg["To"] = to_email
        msg.attach(MIMEText(html, "html", "utf-8"))

        # SMTP без шифрования — внутри Docker-сети это безопасно
        with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30) as server:
            server.send_message(msg)

        logger.debug("📧 SMTP сообщение принято relay: %s → %s", self.from_email, to_email)

    def _build_html(
        self,
        article_title: str,
        article_summary: str,
        article_link: str = None,
        entity_name: str = None,
        entity_type: str = None,
        risk_level: str = None,
        sentiment: str = None,
    ) -> str:
        risk_colors = {"high": "#f87171", "medium": "#fb923c", "low": "#86efac"}
        risk_labels = {"high": "Высокий", "medium": "Средний", "low": "Низкий"}
        sentiment_colors = {
            "positive": "#86efac",
            "negative": "#f87171",
            "neutral": "#d1d5db",
        }
        sentiment_labels = {
            "positive": "Позитивная",
            "negative": "Негативная",
            "neutral": "Нейтральная",
        }

        risk_color = risk_colors.get(risk_level, "#d1d5db")
        risk_label = risk_labels.get(risk_level, "Неизвестен")
        sentiment_color = sentiment_colors.get(sentiment, "#d1d5db")
        sentiment_label = sentiment_labels.get(sentiment, "Не определена")

        entity_row = ""
        if entity_name:
            type_label = "Организация" if entity_type in ("ORG", "organization") else "Персона"
            entity_row = f"""
            <tr>
              <td style="padding:8px;border-bottom:1px solid #e5e7eb;">
                <strong>Отслеживаемая сущность:</strong> {entity_name} ({type_label})
              </td>
            </tr>"""

        link_btn = ""
        if article_link:
            link_btn = f"""
            <tr>
              <td style="padding:12px;text-align:center;">
                <a href="{article_link}" style="background:#3b82f6;color:#fff;padding:10px 20px;
                   text-decoration:none;border-radius:6px;display:inline-block;">
                  Читать полностью
                </a>
              </td>
            </tr>"""

        return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
             line-height:1.6;color:#333;">
  <div style="max-width:600px;margin:0 auto;background:#f9fafb;padding:20px;">
    <div style="background:linear-gradient(120deg,#4f8aff,#1317ff);color:#fff;
                padding:20px;border-radius:12px 12px 0 0;text-align:center;">
      <h1 style="margin:0;font-size:24px;">🔔 Signal Desk</h1>
      <p style="margin:8px 0 0;opacity:.9;">Уведомление о новой статье</p>
    </div>
    <div style="background:#fff;padding:20px;border-radius:0 0 12px 12px;">
      <h2 style="margin-top:0;font-size:20px;line-height:1.4;">{article_title}</h2>
      <p style="color:#666;">{article_summary}</p>
      <table style="width:100%;border-collapse:collapse;margin:20px 0;">
        <tr>
          <td style="padding:8px;border-bottom:1px solid #e5e7eb;">
            <strong>Уровень риска:</strong>
            <span style="background:{risk_color};color:#fff;padding:4px 10px;
                         border-radius:4px;margin-left:8px;">{risk_label}</span>
          </td>
        </tr>
        <tr>
          <td style="padding:8px;border-bottom:1px solid #e5e7eb;">
            <strong>Тональность:</strong>
            <span style="background:{sentiment_color};color:#fff;padding:4px 10px;
                         border-radius:4px;margin-left:8px;">{sentiment_label}</span>
          </td>
        </tr>
        {entity_row}
      </table>
      {link_btn}
      <hr style="border:none;border-top:1px solid #e5e7eb;margin:20px 0;">
      <p style="font-size:12px;color:#999;text-align:center;margin:0;">
        Вы получили это письмо, потому что отслеживаете упоминания организаций и персон.
      </p>
    </div>
  </div>
</body>
</html>"""


# Синглтон
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
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
    return await get_email_service().send_notification_email(
        to_email=to_email,
        subject=subject,
        article_title=article_title,
        article_summary=article_summary,
        **kwargs,
    )

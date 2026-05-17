#!/bin/bash
# deploy_mailrelay.sh
# Запускать из корня проекта: bash deploy_mailrelay.sh
set -e

echo "=== Шаг 1: Создаём директорию для Postfix ==="
mkdir -p docker/mailrelay

echo "=== Шаг 2: Пишем Dockerfile для Postfix ==="
cat > docker/mailrelay/Dockerfile << 'DOCKERFILE'
FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    postfix \
    libsasl2-modules \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY main.cf /etc/postfix/main.cf

EXPOSE 25

CMD ["postfix", "start-fg"]
DOCKERFILE

echo "=== Шаг 3: Пишем конфиг Postfix ==="
cat > docker/mailrelay/main.cf << 'MAINCF'
myhostname = mailrelay
mydomain = localdomain
myorigin = $myhostname

inet_interfaces = all
inet_protocols = ipv4

mynetworks = 127.0.0.0/8, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16

mydestination =

maximal_queue_lifetime = 1h
bounce_queue_lifetime = 1h
maximal_backoff_time = 15m
minimal_backoff_time = 5m
queue_run_delay = 5m

message_size_limit = 26214400

maillog_file = /dev/stdout

smtp_address_preference = ipv4

smtp_tls_security_level = may
smtp_tls_loglevel = 1
MAINCF

echo "=== Шаг 4: Заменяем email_service.py ==="
cat > services/output_module/src/services/email_service.py << 'EMAILSERVICE'
"""
Email Service — отправка через локальный Postfix relay (mailrelay:25).

Порт 587/465 заблокирован провайдером.
Postfix отправляет напрямую через MX-записи домена получателя по порту 25.
Авторизация внутри Docker-сети не требуется.
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
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "mailrelay")
        self.smtp_port = int(os.getenv("SMTP_PORT", "25"))
        self.from_email = os.getenv("SMTP_FROM_EMAIL", "noreply@signal-desk.local")
        self.from_name = os.getenv("SMTP_FROM_NAME", "Signal Desk")

        logger.info(
            "EmailService инициализирован: relay=%s:%s, from=%s",
            self.smtp_host, self.smtp_port, self.from_email,
        )

    def is_configured(self) -> bool:
        return True

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
            await loop.run_in_executor(None, self._send, to_email, subject, html)
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

    def _send(self, to_email: str, subject: str, html: str) -> None:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{self.from_name} <{self.from_email}>"
        msg["To"] = to_email
        msg.attach(MIMEText(html, "html", "utf-8"))

        with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30) as server:
            server.send_message(msg)

        logger.debug("📧 Принято relay: %s → %s", self.from_email, to_email)

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
        sentiment_colors = {"positive": "#86efac", "negative": "#f87171", "neutral": "#d1d5db"}
        sentiment_labels = {"positive": "Позитивная", "negative": "Негативная", "neutral": "Нейтральная"}

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
<html><head><meta charset="UTF-8"></head>
<body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;line-height:1.6;color:#333;">
  <div style="max-width:600px;margin:0 auto;background:#f9fafb;padding:20px;">
    <div style="background:linear-gradient(120deg,#4f8aff,#1317ff);color:#fff;padding:20px;border-radius:12px 12px 0 0;text-align:center;">
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
            <span style="background:{risk_color};color:#fff;padding:4px 10px;border-radius:4px;margin-left:8px;">{risk_label}</span>
          </td>
        </tr>
        <tr>
          <td style="padding:8px;border-bottom:1px solid #e5e7eb;">
            <strong>Тональность:</strong>
            <span style="background:{sentiment_color};color:#fff;padding:4px 10px;border-radius:4px;margin-left:8px;">{sentiment_label}</span>
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
</body></html>"""


_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service


async def send_email(to_email, subject, article_title, article_summary, **kwargs) -> bool:
    return await get_email_service().send_notification_email(
        to_email=to_email, subject=subject,
        article_title=article_title, article_summary=article_summary, **kwargs,
    )
EMAILSERVICE

echo "=== Шаг 5: Обновляем .env ==="
# Убираем старые SMTP-учётные данные, добавляем нужные
if grep -q "SMTP_HOST" .env; then
    sed -i 's/^SMTP_HOST=.*/SMTP_HOST=mailrelay/' .env
    sed -i 's/^SMTP_PORT=.*/SMTP_PORT=25/' .env
    # Комментируем username/password — они не нужны для Postfix
    sed -i 's/^SMTP_USERNAME=/#SMTP_USERNAME=/' .env
    sed -i 's/^SMTP_PASSWORD=/#SMTP_PASSWORD=/' .env
else
    echo "" >> .env
    echo "# Postfix relay (локальный)" >> .env
    echo "SMTP_HOST=mailrelay" >> .env
    echo "SMTP_PORT=25" >> .env
fi

# Убедимся что FROM_EMAIL задан
if ! grep -q "SMTP_FROM_EMAIL" .env; then
    echo "SMTP_FROM_EMAIL=noreply@signal-desk.local" >> .env
fi
if ! grep -q "SMTP_FROM_NAME" .env; then
    echo "SMTP_FROM_NAME=Signal Desk" >> .env
fi

echo "=== Шаг 6: Обновляем docker-compose.yml ==="
python3 - << 'PYEOF'
import re

with open("docker-compose.yml", "r") as f:
    content = f.read()

# 1. Добавляем сервис mailrelay если его нет
if "mailrelay:" not in content:
    mailrelay_service = """
  mailrelay:
    build: ./docker/mailrelay
    container_name: mailrelay
    restart: always
    networks:
      - news_network

"""
    # Вставляем перед output_module
    content = content.replace("  output_module:", mailrelay_service + "  output_module:")
    print("✅ Добавлен сервис mailrelay")
else:
    print("ℹ️  mailrelay уже есть в compose")

# 2. В output_module: убираем dns блок, добавляем depends_on mailrelay
# Убираем dns-строки
content = re.sub(r'\s+dns:\s*\n(\s+-\s+\S+\s*\n)+', '\n', content)

# 3. В notification-consumer: меняем SMTP_* переменные
content = re.sub(
    r'(SMTP_HOST:\s*)\$\{SMTP_HOST\}',
    r'\1mailrelay',
    content
)
content = re.sub(
    r'(SMTP_PORT:\s*)\$\{SMTP_PORT\}',
    r'\1"25"',
    content
)
# Убираем SMTP_USERNAME и SMTP_PASSWORD из environment notification-consumer
lines = content.split('\n')
filtered = []
skip_smtp_creds = False
for line in lines:
    if re.match(r'\s+SMTP_USERNAME:', line) or re.match(r'\s+SMTP_PASSWORD:', line):
        continue  # пропускаем
    filtered.append(line)
content = '\n'.join(filtered)

with open("docker-compose.yml", "w") as f:
    f.write(content)

print("✅ docker-compose.yml обновлён")
PYEOF

echo "=== Шаг 7: Пересобираем и запускаем ==="
docker compose build mailrelay output_module notification-consumer

docker compose up -d mailrelay
sleep 3

docker compose up -d --force-recreate output_module notification-consumer

echo ""
echo "=== Шаг 8: Проверяем что Postfix поднялся ==="
sleep 5
docker compose logs mailrelay --tail=10

echo ""
echo "=== Шаг 9: Тестируем отправку напрямую из контейнера ==="
docker exec notification-consumer python3 -c "
import smtplib
try:
    s = smtplib.SMTP('mailrelay', 25, timeout=10)
    print('✅ Postfix relay доступен!')
    s.quit()
except Exception as e:
    print(f'❌ Ошибка: {e}')
" 2>/dev/null || docker exec output_module python3 -c "
import smtplib
try:
    s = smtplib.SMTP('mailrelay', 25, timeout=10)
    print('✅ Postfix relay доступен!')
    s.quit()
except Exception as e:
    print(f'❌ Ошибка: {e}')
"

echo ""
echo "=================================================="
echo "✅ Готово! Теперь:"
echo "  1. Зайдите на http://185.130.212.50:8003/docs"
echo "  2. Залогиньтесь и нажмите POST /api/v1/notifications/test-email"
echo "  3. Проверьте логи: docker compose logs notification-consumer -f"
echo "  4. Проверьте очередь Postfix: docker exec mailrelay mailq"
echo "=================================================="

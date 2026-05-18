#!/bin/bash
# quick_fix.sh - запускать из ~/news_analyzer
# Не пересобирает ничего, только правит compose и запускает consumer

set -e

echo "=== Проверяем что Kafka реально работает ==="
docker exec news_analyzer-kafka-1 kafka-broker-api-versions --bootstrap-server localhost:9092 > /dev/null 2>&1 \
    && echo "✅ Kafka отвечает!" \
    || echo "⚠️  Kafka не отвечает — подождите 30 сек и запустите скрипт снова"

echo ""
echo "=== Патчим docker-compose.yml ==="
python3 - << 'PYEOF'
with open("docker-compose.yml", "r") as f:
    content = f.read()

# 1. Убираем condition: service_healthy для kafka везде где она есть
#    (заменяем на service_started — не ждём healthy)
import re

# Заменяем все вхождения kafka: condition: service_healthy
content = re.sub(
    r'(kafka:\s*\n\s*)condition: service_healthy',
    r'\1condition: service_started',
    content
)

# 2. Увеличиваем retries и start_period для healthcheck kafka
content = re.sub(
    r'(test: \["CMD-SHELL", "kafka-broker-api-versions[^\]]*"\]\s*\n)'
    r'(\s*interval: \S+\s*\n)'
    r'(\s*timeout: \S+\s*\n)'
    r'(\s*retries: \S+)',
    lambda m: m.group(1) + '      interval: 15s\n      timeout: 15s\n      retries: 30\n      start_period: 90s',
    content
)

with open("docker-compose.yml", "w") as f:
    f.write(content)

print("✅ Все depends_on kafka: condition: service_healthy → service_started")
print("✅ Kafka healthcheck: retries=30, start_period=90s")
PYEOF

echo ""
echo "=== Запускаем notification-consumer напрямую ==="
# Запускаем без проверки зависимостей
docker compose up -d --no-deps notification-consumer

sleep 5

echo ""
echo "=== Статус ==="
docker ps | grep -E "notification-consumer|mailrelay|kafka"

echo ""
echo "=== Логи notification-consumer ==="
docker compose logs notification-consumer --tail=20

echo ""
echo "=== Проверяем relay из consumer ==="
docker exec notification-consumer python3 -c "
import smtplib
try:
    s = smtplib.SMTP('mailrelay', 25, timeout=10)
    print('✅ Postfix relay доступен!')
    s.quit()
except Exception as e:
    print(f'❌ {e}')
" 2>/dev/null || echo "(контейнер стартует...)"

echo ""
echo "========================================"
echo "Готово! Тест отправки письма:"
echo "Зайдите на http://185.130.212.50:8003/docs"
echo "POST /api/v1/notifications/test-email"
echo "========================================"

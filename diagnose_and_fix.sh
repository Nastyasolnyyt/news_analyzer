#!/bin/bash
# diagnose_and_fix.sh
set -e

echo "=== 1. Статус Postfix ==="
docker logs mailrelay --tail=20

echo ""
echo "=== 2. Проверяем порт 25 внутри контейнера mailrelay ==="
docker exec mailrelay bash -c "ss -tlnp | grep 25 || netstat -tlnp 2>/dev/null | grep 25 || echo 'нет данных'"

echo ""
echo "=== 3. Пробуем подключиться к Postfix изнутри самого mailrelay ==="
docker exec mailrelay bash -c "
python3 -c \"
import smtplib
try:
    s = smtplib.SMTP('localhost', 25, timeout=10)
    print('✅ localhost:25 работает')
    s.quit()
except Exception as e:
    print(f'❌ localhost:25: {e}')
\" 2>/dev/null || echo 'python3 недоступен в mailrelay'
"

echo ""
echo "=== 4. Пробуем telnet из notification-consumer ==="
docker exec notification-consumer bash -c "
timeout 5 bash -c 'echo QUIT | nc mailrelay 25' 2>/dev/null \
    && echo '✅ mailrelay:25 отвечает' \
    || echo '❌ mailrelay:25 не отвечает'
" 2>/dev/null || echo "(nc недоступен)"

echo ""
echo "=== 5. IP-адрес mailrelay в Docker сети ==="
docker inspect mailrelay --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'

echo ""
echo "=== 6. Пробуем по IP напрямую ==="
MAIL_IP=$(docker inspect mailrelay --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}')
echo "IP mailrelay: $MAIL_IP"
docker exec notification-consumer python3 -c "
import smtplib
try:
    s = smtplib.SMTP('$MAIL_IP', 25, timeout=10)
    print('✅ По IP работает!')
    s.quit()
except Exception as e:
    print(f'❌ {e}')
"

echo ""
echo "=== 7. Создаём топик articles_analyzed если нет ==="
docker exec news_analyzer-kafka-1 kafka-topics \
    --bootstrap-server localhost:9092 \
    --create --if-not-exists \
    --topic articles_analyzed \
    --partitions 1 \
    --replication-factor 1 \
    && echo "✅ Топик articles_analyzed создан/уже существует"

echo ""
echo "=== 8. Список топиков ==="
docker exec news_analyzer-kafka-1 kafka-topics \
    --bootstrap-server localhost:9092 --list | grep -E "articles_analyzed|notifications"

echo ""
echo "=== 9. Перезапускаем Postfix с отладкой ==="
docker restart mailrelay
sleep 5
docker logs mailrelay --tail=15

Шаг 1 — Собрать базовый ML-образ
 
**Это обязательный первый шаг.** Несколько сервисов (`sentiment_analysis`, `risk-classifier`, `risklevel-classifier`, `event-clustering`) наследуются от базового образа с PyTorch и Transformers. Если его не собрать первым — остальные сборки упадут с ошибкой.
 
```bash
docker compose build ml-base
```
 
Ожидаемое время: **10–30 минут** (скачивает PyTorch ~2 ГБ).
 
> **Почему так долго?** Базовый образ скачивает PyTorch и предзагружает токенизатор
> `blanchefort/rubert-base-cased-sentiment`. Это делается один раз и кешируется.
 
---
 
### Шаг 2 — Собрать все остальные образы
 
```bash
docker compose build
```
 
Ожидаемое время: **15–40 минут** при первой сборке.
 
---
 
### Шаг 3 — Запустить инфраструктуру (БД, Kafka, Redis)
 
Сначала поднимаем только базовые сервисы и ждём их готовности:
 
```bash
docker compose up -d db redis zookeeper kafka elasticsearch
```
 
Подождите ~60 секунд пока Kafka полностью запустится:
 
```bash
# Проверяем что Kafka готова
docker compose logs kafka --tail=20
# Ищем строку: "started (kafka.server.KafkaServer)"
```
 
---
 
### Шаг 4 — Применить миграции базы данных
 
```bash
docker compose run --rm output_module alembic upgrade head
```
 
Если команда падает с ошибкой о существующих таблицах — значит БД уже была
настроена ранее, это нормально.
 
---
 
### Шаг 5 — Запустить все сервисы
 
```bash
docker compose up -d
```
 
---
 
### Шаг 6 — Настроить Postfix (mailrelay)
 
Почтовый relay уже включён в docker-compose.yml и запустится автоматически.
Проверьте что он работает:
 
```bash
# Проверяем что Postfix поднялся
docker compose logs mailrelay --tail=20
 
# Проверяем доступность relay из контейнера приложения
docker exec output_module python3 -c "
import smtplib
s = smtplib.SMTP('mailrelay', 25, timeout=10)
print('OK — relay доступен')
s.quit()
"
```
 
Если relay недоступен — перезапустите:
```bash
docker compose restart mailrelay
sleep 5
docker compose restart output_module notification-consumer
```
 
---
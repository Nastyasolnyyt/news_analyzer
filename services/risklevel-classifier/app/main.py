"""
risklevel-classifier/app/main.py
ИСПРАВЛЕНО:
1. UPSERT не перезаписывает risk_type, установленный risk-classifier
2. Добавлено подробное логирование для диагностики
3. Добавлена проверка входящих сообщений
"""
import asyncio
import json
import logging
import os

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from sqlalchemy import create_engine, Column, Integer, String, Float, text as sql_text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import insert

from app.classifier import HFRiskClassifier

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
INPUT_TOPIC = os.getenv("KAFKA_TOPIC", "risk_types_done")
OUTPUT_TOPIC = os.getenv("OUTPUT_TOPIC", "risk_final_ready")
DATABASE_URL = os.getenv("DATABASE_URL")

Base = declarative_base()


class Risk(Base):
    __tablename__ = "risks"
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, nullable=False, unique=True)
    risk_type = Column(String, nullable=True)
    risk_type_confidence = Column(Float, nullable=True)
    risk_level = Column(String, nullable=True)
    risk_confidence = Column(Float, nullable=True)


async def consume_and_classify():
    logger.info("Инициализирую классификатор Hugging Face...")
    classifier = HFRiskClassifier()

    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    # Не создаём таблицу через metadata — она уже существует
    Session = sessionmaker(bind=engine)

    # Проверяем подключение к БД
    try:
        with engine.connect() as conn:
            conn.execute(sql_text("SELECT 1"))
        logger.info("Подключение к БД успешно")
    except Exception as e:
        logger.error(f"Ошибка подключения к БД: {e}")
        raise

    consumer = AIOKafkaConsumer(
        INPUT_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="risklevel-classifier-group",
        auto_offset_reset="earliest",
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )

    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda m: json.dumps(m, ensure_ascii=False).encode('utf-8')
    )

    await consumer.start()
    await producer.start()

    logger.info(f"Сервис запущен. Слушаю топик: {INPUT_TOPIC}")

    processed_count = 0

    try:
        async for message in consumer:
            try:
                article_data = message.value

                # Получаем ID статьи
                article_id = article_data.get('article_id') or article_data.get('id')
                if not article_id:
                    logger.warning("Пропускаю сообщение без article_id")
                    continue

                title = article_data.get('title', '')
                text = article_data.get('text', '')
                full_text = f"{title} {text}".strip()

                if not full_text:
                    logger.warning(f"Пустой текст для статьи {article_id}, пропускаю")
                    continue

                # Получаем risk_type из предыдущего классификатора
                risk_type_from_prev = article_data.get('risk_type', None)
                logger.info(
                    f"Обрабатываю статью {article_id} "
                    f"(risk_type от risk-classifier: {risk_type_from_prev})"
                )

                # Классифицируем УРОВЕНЬ риска
                result = classifier.classify(full_text)

                session = Session()
                try:
                    # ИСПРАВЛЕНО: используем INSERT ... ON CONFLICT DO UPDATE
                    # Если запись уже есть (создана risk-classifier), обновляем только
                    # поля risk_level и risk_confidence, НЕ трогая risk_type.
                    # Если записи нет — создаём новую со всеми полями.
                    stmt = insert(Risk).values(
                        article_id=article_id,
                        risk_level=result["risk_level"],
                        risk_confidence=result["confidence"],
                        # risk_type берём из предыдущего сервиса если есть
                        risk_type=risk_type_from_prev,
                    ).on_conflict_do_update(
                        index_elements=['article_id'],
                        set_={
                            # Обновляем только уровень риска
                            'risk_level': result["risk_level"],
                            'risk_confidence': result["confidence"],
                            # risk_type НЕ перезаписываем — он уже заполнен
                            # risk-classifier'ом через отдельный UPSERT
                        }
                    )
                    session.execute(stmt)
                    session.commit()

                    processed_count += 1
                    logger.info(
                        f"Статья {article_id}: "
                        f"risk_level={result['risk_level']}, "
                        f"confidence={result['confidence']:.2f} "
                        f"(всего обработано: {processed_count})"
                    )
                except Exception as db_err:
                    session.rollback()
                    logger.error(
                        f"Ошибка БД для статьи {article_id}: {db_err}",
                        exc_info=True
                    )
                    continue
                finally:
                    session.close()

                # Отправляем результат дальше
                output_message = {
                    **article_data,
                    'risk_level': result["risk_level"],
                    'risk_confidence': result["confidence"]
                }
                await producer.send_and_wait(OUTPUT_TOPIC, output_message)

            except Exception as e:
                logger.error(f"Ошибка обработки сообщения: {e}", exc_info=True)
                continue

    except KeyboardInterrupt:
        logger.info("Остановка сервиса...")
    finally:
        await consumer.stop()
        await producer.stop()
        logger.info(f"Сервис остановлен. Обработано статей: {processed_count}")


if __name__ == "__main__":
    asyncio.run(consume_and_classify())
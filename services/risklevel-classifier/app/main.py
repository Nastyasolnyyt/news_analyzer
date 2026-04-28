"""
risklevel-classifier/app/main.py
ИСПРАВЛЕНО:
1. UnknownMemberIdError — модель работает ~1 мин/статью, Kafka считает consumer мёртвым.
   Решение: session_timeout_ms=120s, max_poll_interval_ms=300s, ручной commit.
2. Дозаполнение при старте — статьи id 6-28 без risk_level заполнятся автоматически.
3. Защита от повторной обработки — проверяем risk_level в БД перед классификацией.
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


def save_risk_level(session, article_id: int, risk_level: str,
                    confidence: float, risk_type: str = None):
    """
    Сохраняет risk_level. При конфликте обновляет только уровень, не трогает risk_type.
    """
    stmt = insert(Risk).values(
        article_id=article_id,
        risk_level=risk_level,
        risk_confidence=confidence,
        risk_type=risk_type,
    ).on_conflict_do_update(
        index_elements=['article_id'],
        set_={
            'risk_level': risk_level,
            'risk_confidence': confidence,
        }
    )
    session.execute(stmt)
    session.commit()


def backfill_missing_risk_levels(engine, classifier: HFRiskClassifier):
    """
    При старте дозаполняет risk_level для статей у которых он пустой.
    Это исправит статьи id 6-28 и любые другие пропущенные.
    """
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        rows = session.execute(sql_text("""
            SELECT r.article_id, r.risk_type, a.title, a.text
            FROM risks r
            JOIN articles a ON a.id = r.article_id
            WHERE r.risk_type IS NOT NULL
              AND r.risk_level IS NULL
            ORDER BY r.article_id
        """)).fetchall()

        if not rows:
            logger.info("Дозаполнение: все статьи уже имеют risk_level")
            return

        logger.info(f"Дозаполнение: найдено {len(rows)} статей без risk_level")

        for i, row in enumerate(rows):
            article_id, risk_type, title, text = row
            full_text = f"{title or ''} {text or ''}".strip()

            if not full_text:
                logger.warning(f"  Статья {article_id}: пустой текст, пропускаю")
                continue

            try:
                result = classifier.classify(full_text)
                save_risk_level(
                    session, article_id,
                    result["risk_level"], result["confidence"],
                    risk_type=risk_type
                )
                logger.info(
                    f"  [{i+1}/{len(rows)}] Статья {article_id}: "
                    f"{result['risk_level']} ({result['confidence']:.2f})"
                )
            except Exception as e:
                session.rollback()
                logger.error(f"  Ошибка для статьи {article_id}: {e}")
                continue

        logger.info("Дозаполнение завершено")

    except Exception as e:
        logger.error(f"Ошибка при дозаполнении: {e}", exc_info=True)
    finally:
        session.close()


async def consume_and_classify():
    logger.info("Инициализирую классификатор Hugging Face...")
    classifier = HFRiskClassifier()

    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    Session = sessionmaker(bind=engine)

    try:
        with engine.connect() as conn:
            conn.execute(sql_text("SELECT 1"))
        logger.info("Подключение к БД успешно")
    except Exception as e:
        logger.error(f"Ошибка подключения к БД: {e}")
        raise

    # Дозаполняем старые статьи
    logger.info("Запускаю дозаполнение старых статей без risk_level...")
    backfill_missing_risk_levels(engine, classifier)

    consumer = AIOKafkaConsumer(
        INPUT_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="risklevel-classifier-group",
        auto_offset_reset="earliest",

        # КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ UnknownMemberIdError:
        # BART-large занимает ~60 сек/статью.
        # Kafka по умолчанию: session_timeout=10s, max_poll_interval=300s
        # Consumer не успевает отправить heartbeat → Kafka выгоняет его из группы
        # → offset не коммитится → статья обрабатывается снова и снова
        session_timeout_ms=120_000,    # 2 минуты — время до кика из группы
        heartbeat_interval_ms=15_000,  # heartbeat каждые 15 сек
        max_poll_interval_ms=600_000,  # 10 минут — макс пауза между poll()

        # Отключаем авто-коммит — коммитим вручную после успешной обработки
        enable_auto_commit=False,

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
            article_id = None
            try:
                article_data = message.value

                article_id = article_data.get('article_id') or article_data.get('id')
                if not article_id:
                    logger.warning("Пропускаю сообщение без article_id")
                    await consumer.commit()
                    continue

                # Защита от повторной обработки
                session = Session()
                try:
                    existing_level = session.execute(sql_text(
                        "SELECT risk_level FROM risks WHERE article_id = :aid"
                    ), {"aid": article_id}).scalar()
                finally:
                    session.close()

                if existing_level is not None:
                    logger.info(
                        f"Статья {article_id} уже обработана "
                        f"(risk_level={existing_level}), пропускаю"
                    )
                    await consumer.commit()
                    continue

                title = article_data.get('title', '')
                text = article_data.get('text', '')
                full_text = f"{title} {text}".strip()

                if not full_text:
                    logger.warning(f"Пустой текст для статьи {article_id}")
                    await consumer.commit()
                    continue

                risk_type_from_prev = article_data.get('risk_type')
                logger.info(
                    f"Классифицирую статью {article_id} "
                    f"(risk_type: {risk_type_from_prev})"
                )

                result = classifier.classify(full_text)

                session = Session()
                try:
                    save_risk_level(
                        session, article_id,
                        result["risk_level"], result["confidence"],
                        risk_type=risk_type_from_prev
                    )
                    processed_count += 1
                    logger.info(
                        f"Статья {article_id}: "
                        f"risk_level={result['risk_level']}, "
                        f"confidence={result['confidence']:.2f} "
                        f"(всего: {processed_count})"
                    )
                except Exception as db_err:
                    session.rollback()
                    logger.error(f"Ошибка БД для статьи {article_id}: {db_err}")
                    raise
                finally:
                    session.close()

                # Отправляем дальше
                output_message = {
                    **article_data,
                    'risk_level': result["risk_level"],
                    'risk_confidence': result["confidence"]
                }
                await producer.send_and_wait(OUTPUT_TOPIC, output_message)

                # Коммитим offset только после успешной обработки
                await consumer.commit()

            except Exception as e:
                logger.error(
                    f"Ошибка обработки статьи {article_id}: {e}",
                    exc_info=True
                )
                # Не коммитим offset — сообщение будет перечитано
                continue

    except KeyboardInterrupt:
        logger.info("Остановка сервиса...")
    finally:
        await consumer.stop()
        await producer.stop()
        logger.info(f"Сервис остановлен. Обработано: {processed_count}")


if __name__ == "__main__":
    asyncio.run(consume_and_classify())
import logging
from typing import Tuple

from transformers import pipeline

from .config import get_settings


logger = logging.getLogger(__name__)

_classifier = None


def _get_classifier():
    """Ленивая инициализация пайплайна sentiment-analysis."""

    global _classifier
    if _classifier is None:
        settings = get_settings()
        try:
            logger.info(
                "Loading sentiment model '%s'...", settings.sentiment_model_name
            )
            _classifier = pipeline(
                "sentiment-analysis",
                model=settings.sentiment_model_name,
            )
            logger.info(
                "Sentiment model '%s' successfully loaded",
                settings.sentiment_model_name,
            )
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "Failed to load sentiment model '%s': %s",
                settings.sentiment_model_name,
                exc,
                exc_info=True,
            )
            raise
    return _classifier


def init_model() -> None:
    """Явная инициализация модели при старте сервиса."""

    _get_classifier()


def analyze_sentiment(text: str) -> Tuple[str, float]:
    """
    Анализ тональности текста.

    Возвращает (sentiment_label, confidence_score), где
    sentiment_label ∈ {"positive", "negative", "neutral"}.
    """

    text = (text or "").strip()
    if not text:
        raise ValueError("Empty text passed to analyze_sentiment")

    classifier = _get_classifier()
    result = classifier(text)[0]

    raw_label = str(result.get("label", "")).lower().strip()
    score = float(result.get("score", 0.0))

    # Нормализация меток модели к трем значениям
    mapping = {
        "positive": "positive",
        "pos": "positive",
        "negative": "negative",
        "neg": "negative",
        "neutral": "neutral",
        "neu": "neutral",
    }

    sentiment_label = mapping.get(raw_label, raw_label)
    if sentiment_label not in {"positive", "negative", "neutral"}:
        # На всякий случай приводим всё, что не распознали, к neutral
        sentiment_label = "neutral"

    return sentiment_label, score



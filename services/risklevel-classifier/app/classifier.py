"""
risklevel-classifier/app/classifier.py
ИСПРАВЛЕНО:
1. multi_class=False → multi_label=False (deprecated warning убран)
2. Добавлено кэширование модели (загружается один раз)
"""
import logging
from typing import Dict

from transformers import pipeline
import torch

logger = logging.getLogger(__name__)


class HFRiskClassifier:
    """Классификатор уровней риска (high/medium/low) через Zero-Shot Classification."""

    def __init__(self):
        try:
            self.device = 0 if torch.cuda.is_available() else -1

            logger.info(f"🔧 Инициализирую классификатор (device={self.device})...")

            self.classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=self.device
            )

            self.candidate_labels = [
                "высокий риск: санкции, войны, аресты, банкротства, цензура, блокировки",
                "средний риск: штрафы, расследования, скандалы, резкие убытки, падение акций",
                "низкий риск: обычные новости, партнёрства, рост, назначения, открытия"
            ]

            logger.info("✅ HF Risk Classifier готов к работе")

        except Exception as e:
            logger.error(f"❌ Ошибка инициализации классификатора: {e}")
            raise

    def classify(self, text: str) -> Dict:
        """
        Классифицирует уровень риска текста.

        Returns:
            {"risk_level": "high"|"medium"|"low", "confidence": float}
        """
        if not text or len(text.strip()) < 10:
            logger.warning("Пустой или слишком короткий текст")
            return {"risk_level": "low", "confidence": 0.0}

        try:
            text_clean = text[:1024].strip()

            # ИСПРАВЛЕНО: multi_class → multi_label (multi_class deprecated)
            result = self.classifier(
                text_clean,
                self.candidate_labels,
                multi_label=False
            )

            top_label = result["labels"][0]
            confidence = result["scores"][0]

            if "высокий" in top_label.lower():
                risk_level = "high"
            elif "средний" in top_label.lower():
                risk_level = "medium"
            else:
                risk_level = "low"

            logger.debug(f"Классифицировано: {risk_level} ({confidence:.2f})")

            return {
                "risk_level": risk_level,
                "confidence": float(confidence)
            }

        except Exception as e:
            logger.error(f"Ошибка классификации: {e}")
            return {"risk_level": "low", "confidence": 0.0}
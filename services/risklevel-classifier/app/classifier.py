"""
Классификатор уровней риска на базе Hugging Face BART
Замена для OpenRouter - работает без лимитов
"""
import os
import logging
from typing import Optional, Dict
from transformers import pipeline
import torch

logger = logging.getLogger(__name__)

class HFRiskClassifier:
    """Классификатор уровней риска (high/medium/low) с помощью Zero-Shot Classification"""
    
    def __init__(self):
        """Инициализация модели"""
        try:
            # Выбираем device
            self.device = 0 if torch.cuda.is_available() else -1  # GPU или CPU
            
            logger.info(f"🔧 Инициализирую классификатор (device={self.device})...")
            
            # Загружаем модель
            self.classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",  # ✅ OPEN-SOURCE, БЕЗ ЛИМИТОВ
                device=self.device
            )
            
            # Кандидаты для классификации
            self.candidate_labels = [
                "высокий риск: санкции, войны, аресты, банкротства, цензура, блокировки",
                "средний риск: штрафы, расследования, скандалы, резкие убытки, падение акций",
                "низкий риск: обычные новости, партнёрства, рост, назначения, открытия"
            ]
            
            logger.info("✅ HF Risk Classifier готов к работе")
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации классификатора: {e}")
            raise
    
    def classify(self, text: str) -> Dict[str, any]:
        """
        Классифицирует риск текста
        
        Args:
            text: Текст для классификации (заголовок + описание)
        
        Returns:
            {
                "risk_level": "high" | "medium" | "low",
                "confidence": 0.0..1.0
            }
        """
        if not text or len(text.strip()) < 10:
            logger.warning("⚠️  Пустой или очень короткий текст")
            return {"risk_level": "low", "confidence": 0.0}
        
        try:
            # Обрезаем текст до разумного размера
            text_clean = text[:1024].strip()
            
            # Классифицируем
            result = self.classifier(text_clean, self.candidate_labels, multi_class=False)
            
            top_label = result["labels"][0]
            confidence = result["scores"][0]
            
            # Маппим на уровни
            if "высокий" in top_label.lower():
                risk_level = "high"
            elif "средний" in top_label.lower():
                risk_level = "medium"
            else:
                risk_level = "low"
            
            logger.debug(f"✅ Классифицирована: {risk_level} ({confidence:.2f})")
            
            return {
                "risk_level": risk_level,
                "confidence": float(confidence)
            }
        
        except Exception as e:
            logger.error(f"❌ Ошибка классификации: {e}")
            return {"risk_level": "low", "confidence": 0.0}


# Тест
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    classifier = HFRiskClassifier()
    
    test_texts = [
        "Газпром объявил о санкциях и остановке поставок газа в Европу",
        "Компания запустила новый продукт на рынке",
        "Центробанк изучает возможность повышения ключевой ставки",
    ]
    
    for text in test_texts:
        result = classifier.classify(text)
        print(f"Текст: {text[:50]}...")
        print(f"Результат: {result}\n")
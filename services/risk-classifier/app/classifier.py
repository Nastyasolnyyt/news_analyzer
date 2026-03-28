"""
services/risk-classifier/app/classifier.py
ИСПРАВЛЕННЫЙ: использует Hugging Face вместо OpenRouter
"""
import os
import logging
from typing import Optional
from transformers import pipeline
import torch

logger = logging.getLogger(__name__)

class RiskTypeClassifier:
    """Классификатор ТИПОВ риска (политический/экономический/социальный) на базе BART Zero-Shot"""
    
    def __init__(self):
        """Инициализация модели"""
        try:
            # Выбираем device
            self.device = 0 if torch.cuda.is_available() else -1
            
            logger.info(f"🔧 Инициализирую Risk Type Classifier (device={self.device})...")
            
            # Загружаем BART-large-mnli для zero-shot classification
            self.classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=self.device
            )
            
            # КАТЕГОРИИ: политический / экономический / социальный
            self.candidate_labels = [
                "политический",
                "экономический", 
                "социальный"
            ]
            
            # Расширенные описания для лучшей классификации
            self.label_descriptions = {
                "политический": "политика правительство международные отношения войны санкции выборы дипломатия парламент",
                "экономический": "экономика финансы бизнес компании банки рынки инвестиции торговля цены валюта",
                "социальный": "общество люди транспорт безопасность здоровье культура образование благоустройство"
            }
            
            logger.info("✅ Risk Type Classifier готов к работе")
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации классификатора: {e}")
            raise
    
    def classify(self, text: str):
        """
        Классифицирует тип риска текста
        
        Args:
            text: Текст для классификации (заголовок + описание)
        
        Returns:
            {
                "risk_type": "политический" | "экономический" | "социальный",
                "confidence": 0.0..1.0
            }
        """
        if not text or len(text.strip()) < 10:
            logger.warning("Пустой или очень короткий текст")
            return {"risk_type": "социальный", "confidence": 0.0}
        
        try:
            # Обрезаем текст до разумного размера
            text_clean = text[:512].strip()
            
            # Классифицируем с использованием гипотез
            result = self.classifier(
                text_clean,
                self.candidate_labels,
                multi_class=False,
                hypothesis_template="Этот текст о {}"
            )
            
            risk_type = result["labels"][0]  # Самая вероятная категория
            confidence = float(result["scores"][0])
            
            logger.debug(f"✅ Классифицирована: {risk_type} ({confidence:.2f})")
            
            return {
                "risk_type": risk_type,
                "confidence": confidence
            }
        
        except Exception as e:
            logger.error(f"❌ Ошибка классификации: {e}")
            return {"risk_type": "социальный", "confidence": 0.0}


class RiskResult:
    """Класс результата классификации"""
    def __init__(self, risk_type: str, confidence: float):
        self.risk_type = risk_type
        self.confidence = confidence
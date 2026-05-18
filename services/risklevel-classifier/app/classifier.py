import os
import logging
import re
from typing import Optional
from openai import OpenAI
from .models import RiskResult

logger = logging.getLogger(__name__)

class MistralNeuralClassifier:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is required")
        
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
            default_headers={
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "PulseSight_Analyzer"
            },
            timeout=30.0
        )
        self.model = "qwen/qwen3-8b:free"

    def classify(self, text: str) -> RiskResult:
        """Основной входной метод"""
        if not text or len(text.strip()) < 10:
            return RiskResult(risk_type="low", confidence=0.0)
        
        # Очистка текста от лишних символов перед отправкой
        clean_text = text.replace('\n', ' ').strip()
        return self._call_model(clean_text)

    def _create_mistral_prompt(self, text: str) -> str:
        return f"""Ты анализируешь риск новости для бизнеса и общества. 
        Верни ТОЛЬКО одно слово: high, medium или low.

        high — война, санкции, арест, банкротство, катастрофа, теракт, кризис, обвал
        medium — штраф, расследование, отставка, падение рынка, реформа, ограничения  
        low — обычные новости, партнёрство, рост, назначения

        Текст: {text[:1000]}

        УРОВЕНЬ РИСКА:"""

    def _call_model(self, text: str) -> RiskResult:
        try:
            prompt = self._create_mistral_prompt(text)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            raw_response = response.choices[0].message.content.strip().lower()
            risk_level, confidence = self._parse_risk_level(raw_response)
            
            return RiskResult(risk_type=risk_level, confidence=confidence)
        except Exception as e:
            logger.error(f"Error in Mistral API: {e}")
            return RiskResult(risk_type="low", confidence=0.0)

    def _parse_risk_level(self, response: str) -> tuple[str, float]:  # ← должен быть внутри класса
        response_clean = re.sub(r'[^a-z]', '', response.lower())
        if response_clean == "high":
            return "high", 0.95
        if response_clean == "medium":
            return "medium", 0.85
        if response_clean == "low":
            return "low", 0.85
        for level, conf in [("high", 0.9), ("medium", 0.8), ("low", 0.7)]:
            if level in response_clean:
                return level, conf
        return "low", 0.1
        
    # Если ответила длинно, берем по приоритету опасности
    for level, conf in [("high", 0.9), ("medium", 0.8), ("low", 0.7)]:
        if level in response_clean:
            return level, conf
            
    return "low", 0.1   

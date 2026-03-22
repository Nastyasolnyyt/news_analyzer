from .models import RiskResult
import os
import logging
from typing import Optional
import re
import time
from openai import OpenAI

logger = logging.getLogger(__name__)

class MistralNeuralClassifier:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            logger.error("OPENROUTER_API_KEY not found!")
            raise ValueError("OPENROUTER_API_KEY is required")
        
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
            timeout=30.0
        )
        
     
        self.model = "qwen/qwen3-next-80b-a3b-instruct:free"
        
        logger.info(f"Classifier initialized with model: {self.model}")
    
    def classify(self, text: str) -> RiskResult:
        try:
            if not text or not text.strip():
                return RiskResult(risk_type="ошибка_нейросети", confidence=0.0)
            
            clean_text = self._clean_text(text)
            return self._call_mistral_model(clean_text)
            
        except Exception as e:
            logger.error(f"Qwen model error: {type(e).__name__}: {str(e)}")
            return RiskResult(risk_type="ошибка_нейросети", confidence=0.0)
    
    def _call_mistral_model(self, text: str) -> RiskResult:
        prompt = self._create_mistral_prompt(text)
        logger.debug(f"Qwen request: {text[:50]}...")
        
        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "Ты - русскоязычный классификатор новостей. Отвечай только названием категории."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10,
                temperature=0.1,
                top_p=0.9
            )
            
            elapsed_time = time.time() - start_time
            answer = response.choices[0].message.content.strip().lower()
            logger.debug(f"Qwen response ({elapsed_time:.2f}s): {answer}")
            
            risk_type, confidence = self._parse_mistral_response(answer)
            return RiskResult(risk_type=risk_type, confidence=confidence)
            
        except Exception as e:
            logger.error(f"Qwen API call failed: {e}")
            return RiskResult(risk_type="ошибка_нейросети", confidence=0.0)
    
    def _create_mistral_prompt(self, text: str) -> str:
        return f"""Классифицируй этот новостной заголовок:

"{text}"

Категории:
- политический: политика, правительство, международные отношения, войны, санкции, выборы
- экономический: экономика, финансы, бизнес, компании, банки, рынки, инвестиции
- социальный: общество, люди, транспорт, безопасность, здоровье, культура, образование

Верни только одно слово: политический, экономический или социальный."""
    
    def _parse_mistral_response(self, response: str) -> tuple[str, float]:
        response_lower = response.lower().strip()
        response_lower = response_lower.replace('"', '').replace("'", "").replace('.', '').replace(',', '').strip()
        
        exact_matches = {
            "политический": ("политический", 0.96),
            "экономический": ("экономический", 0.96),
            "социальный": ("социальный", 0.96),
        }
        
        for key, (category, conf) in exact_matches.items():
            if response_lower == key:
                return category, conf
        
        if any(word in response_lower for word in ["политическ"]):
            return "политический", 0.92
        elif any(word in response_lower for word in ["экономическ", "финансов"]):
            return "экономический", 0.92
        elif any(word in response_lower for word in ["социальн"]):
            return "социальный", 0.92
        
        # Пытаемся найти категорию в тексте
        categories = ["политический", "экономический", "социальный"]
        for category in categories:
            if category in response_lower:
                return category, 0.88
        
        if any(word in response_lower for word in ["война", "президент", "правительство", "санкц", "выборы"]):
            return "политический", 0.85
        elif any(word in response_lower for word in ["банк", "экономик", "финанс", "рынок", "инвестиц"]):
            return "экономический", 0.85
        elif any(word in response_lower for word in ["общество", "люди", "транспорт", "безопасност", "здоровье"]):
            return "социальный", 0.85
        
        logger.warning(f"Qwen returned unclear response: '{response}'")
        return "неопределенный", 0.0
    
    def _clean_text(self, text: str) -> str:
        text = re.sub(r'<[^>]+>', ' ', text)
        text = text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        cleaned = ' '.join(text.split()).strip()
        
        if len(cleaned) > 1000:
            cleaned = cleaned[:997] + "..."
        
        return cleaned
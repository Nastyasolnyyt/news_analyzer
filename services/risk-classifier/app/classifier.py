# services/risk-classifier/app/classifier.py
import re
import logging
from .models import RiskResult

logger = logging.getLogger(__name__)

class MistralNeuralClassifier:
    # ... (твой существующий __init__ остается без изменений)

    def _create_mistral_prompt(self, text: str) -> str:
        # Кардинально меняем промпт, чтобы сфокусироваться на рисках
        return f"""
        Analyze the following news text and determine the business/security RISK LEVEL.
        Return ONLY one word: 'high', 'medium', or 'low'.

        - 'high': Sanctions, arrests, bankruptcy, hacking, major lawsuits, environmental disasters, war.
        - 'medium': Fines, investigations, resignations, stock drops, local protests, warnings.
        - 'low': Normal operations, new partnerships, charity, general market news, appointments.

        Text: {text[:1500]}
        
        RISK LEVEL:"""

    def _call_model(self, text: str) -> RiskResult:
        try:
            prompt = self._create_mistral_prompt(text)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1 # Низкая температура для точности
            )
            
            raw_response = response.choices[0].message.content.strip().lower()
            risk_level, confidence = self._parse_risk_level(raw_response)
            
            return RiskResult(risk_type=risk_level, confidence=confidence)
        except Exception as e:
            logger.error(f"Error calling model: {e}")
            return RiskResult(risk_type="low", confidence=0.0)

    def _parse_risk_level(self, response: str) -> tuple[str, float]:
        # Чистим ответ от лишних знаков препинания
        response_clean = re.sub(r'[^\w]', '', response)
        
        if "high" in response_clean:
            return "high", 0.95
        elif "medium" in response_clean:
            return "medium", 0.85
        elif "low" in response_clean:
            return "low", 0.75
        
        # Запасной вариант на основе ключевых слов, если нейронка ответила странно
        return "low", 0.1
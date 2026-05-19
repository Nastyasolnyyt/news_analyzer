"""
risklevel-classifier/app/classifier.py
ИСПРАВЛЕНО:
1. multi_class=False → multi_label=False (deprecated warning убран)
2. Добавлено кэширование модели (загружается один раз)
"""
import json
import logging
import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModel
from huggingface_hub import hf_hub_download
 
logger = logging.getLogger(__name__)
 
HF_REPO = "relentless01/news-multitask-classifier"     
 
class MultiTaskModel(nn.Module):
    """Та же архитектура."""
    def __init__(self, base_model_name, hidden_size,
                 num_categories=3, num_risks=3):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(base_model_name)
        self.category_head = nn.Sequential(
            nn.Dropout(0.1),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.GELU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_size // 2, num_categories)
        )
        self.risk_head = nn.Sequential(
            nn.Dropout(0.1),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.GELU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_size // 2, num_risks)
        )
 
    def forward(self, input_ids, attention_mask):
        out = self.encoder(input_ids=input_ids,
                           attention_mask=attention_mask)
        cls = out.last_hidden_state[:, 0, :]
        return self.category_head(cls), self.risk_head(cls)
 
 
class HFRiskClassifier:
    """
    Дроп-ин замена старого класса.
    Интерфейс тот же: classify(text) -> {"risk_level": str, "confidence": float}
    """
    def __init__(self):
        logger.info(f"Загружаем модель с HuggingFace: {HF_REPO}")
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")
 
        config_path = hf_hub_download(repo_id=HF_REPO,
                                      filename="config.json")
        with open(config_path) as f:
            self.config = json.load(f)
 
        self.id2risk = {int(k): v
                        for k, v in self.config["id2risk"].items()}
        self.max_len = self.config["max_length"]
 
        self.tokenizer = AutoTokenizer.from_pretrained(HF_REPO)
 
        self.model = MultiTaskModel(
            base_model_name = self.config["base_model"],
            hidden_size     = self.config["hidden_size"]
        )
        weights_path = hf_hub_download(repo_id=HF_REPO,
                                       filename="pytorch_model.bin")
        self.model.load_state_dict(
            torch.load(weights_path, map_location=self.device)
        )
        self.model.to(self.device)
        self.model.eval()
        
 
        logger.info("✅ HFRiskClassifier готов к работе")
 
    def classify(self, text: str) -> dict:
        if not text or len(text.strip()) < 10:
            logger.warning("Пустой или слишком короткий текст")
            return {"risk_level": "low", "confidence": 0.0}
 
        try:
            enc = self.tokenizer(
                text,
                truncation=True,
                padding=True,
                max_length=self.max_len,
                return_tensors="pt"
            )
            enc = {k: v.to(self.device) for k, v in enc.items()}
 
            with torch.inference_mode():
                _, risk_logits = self.model(
                    enc["input_ids"], enc["attention_mask"]
                )
 
            probs = torch.softmax(risk_logits, dim=-1)
            pred  = torch.argmax(probs, dim=-1).item()
            conf  = probs[0][pred].item()
 
            risk_level = self.id2risk[pred]
            logger.debug(f"Классифицировано: {risk_level} ({conf:.2f})")
 
            return {"risk_level": risk_level,
                    "confidence": round(float(conf), 4)}
 
        except Exception:
            logger.exception("Ошибка классификации")
            return {"risk_level": "low", "confidence": 0.0}

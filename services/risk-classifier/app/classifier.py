import json
import logging
import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModel
from huggingface_hub import hf_hub_download

torch.set_num_threads(1)

logger = logging.getLogger(__name__)
 
HF_REPO = "relentless01/news-multitask-classifier"
 
# Маппинг наших меток на русские названия которые ждёт storage.py
CAT_MAP = {
    "politics":  "политический",
    "economics": "экономический",
    "social":    "социальный"
}
 
 
class MultiTaskModel(nn.Module):
    """Архитектура должна совпадать с тем что обучали."""
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
 
 
class RiskTypeClassifier:
    """
    Дроп-ин замена старого класса.
    Интерфейс тот же: classify(text) -> {"risk_type": str, "confidence": float}
    """
    def __init__(self):
        logger.info(f"Загружаем модель с HuggingFace: {HF_REPO}")
        self.device = 0 if torch.cuda.is_available() else -1
 
        # Загружаем конфиг
        config_path = hf_hub_download(repo_id=HF_REPO,
                                      filename="config.json")
        with open(config_path) as f:
            self.config = json.load(f)
 
        self.id2cat  = {int(k): v
                        for k, v in self.config["id2cat"].items()}
        self.max_len = self.config["max_length"]
 
        # Токенизатор
        self.tokenizer = AutoTokenizer.from_pretrained(HF_REPO)
 
        # Модель
        self.model = MultiTaskModel(
            base_model_name = self.config["base_model"],
            hidden_size     = self.config["hidden_size"]
        )
        weights_path = hf_hub_download(repo_id=HF_REPO,
                                       filename="pytorch_model.bin")
        self.model.load_state_dict(
            torch.load(weights_path, map_location="cpu")
        )
        self.model.eval()
        if self.device == 0:
            self.model = self.model.cuda()
 
        logger.info("✅ RiskTypeClassifier готов к работе")
        self.classify("Тестовая новость")
 
    def classify(self, text: str) -> dict:
        if not text or len(text.strip()) < 10:
            logger.warning("Пустой или слишком короткий текст")
            return {"risk_type": "социальный", "confidence": 0.0}
 
        try:
            enc = self.tokenizer(
                text[:1024],
                truncation=True,
                padding=True,
                max_length=self.max_len,
                return_tensors="pt"
            )
            if self.device == 0:
                enc = {k: v.cuda() for k, v in enc.items()}
 
            with torch.inference_mode():
                cat_logits, _ = self.model(
                    enc["input_ids"], enc["attention_mask"]
                )
 
            probs = torch.softmax(cat_logits, dim=-1)
            pred  = torch.argmax(probs, dim=-1).item()
            conf  = probs[0][pred].item()
 
            category = CAT_MAP.get(self.id2cat[pred], "социальный")
            logger.debug(f"Классифицировано: {category} ({conf:.2f})")
 
            return {"risk_type": category, "confidence": round(conf, 4)}
 
        except Exception as e:
            logger.exception("Ошибка классификации")
            return {"risk_type": "социальный", "confidence": 0.0}
 

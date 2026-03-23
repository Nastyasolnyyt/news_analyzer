# services/telegram-parser-service/app/models.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Article(BaseModel):
    title: str
    link: str
    text: str
    pub_date: Optional[datetime]
    source: str

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
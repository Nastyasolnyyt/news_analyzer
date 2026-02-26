from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Article(BaseModel):
    id: Optional[int] = None
    title: str
    description: Optional[str] = None  # <--- БЫЛО 'text', ДОЛЖНО БЫТЬ 'description'
    link: str
    pub_date: Optional[datetime] = None # Желательно использовать datetime, Pydantic сам распарсит строку
    source: str
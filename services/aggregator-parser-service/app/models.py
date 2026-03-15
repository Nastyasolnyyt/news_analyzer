# models.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Article(BaseModel):
    id: Optional[int] = None 
    title: str
    description: Optional[str] = None
    link: str
    pub_date: Optional[datetime] = None
    source: str
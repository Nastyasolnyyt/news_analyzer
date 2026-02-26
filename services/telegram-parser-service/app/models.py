from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Article(BaseModel):
    title: str
    link: str
    text: str
    pub_date: Optional[datetime] = None
    source: str
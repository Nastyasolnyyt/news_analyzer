from datetime import datetime

from pydantic import BaseModel


class TopicDTO(BaseModel):
    id: int
    name: str
    created_at: datetime

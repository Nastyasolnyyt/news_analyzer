from pydantic import BaseModel


class PostEntityDTO(BaseModel):
    post_id: int
    entity_id: int

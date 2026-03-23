
# src/infrastructure/postgres/models/__init__.py

from .user import User
from .post import Article  # или Post, смотря как назван класс
from .post_analysis import PostAnalysis
from .post_entity import PostEntity
from .named_entity import NamedEntity
from .topic import Topic

# Теперь ты сможешь импортировать их красиво:
# from src.infrastructure.postgres.models import User, Topic

from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import declarative_base
import enum

Base = declarative_base()

class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    login = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)  
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, default=UserRole.USER.value)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, login='{self.login}', username='{self.username}')>"
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
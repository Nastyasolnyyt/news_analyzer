from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from src.application.enums import UserRole


class UserDTO(BaseModel):
    id: int
    login: str
    name: str
    role: UserRole
    created_at: datetime


class UserCreateDTO(BaseModel):
    login: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=6, max_length=255)
    name: str = Field(..., min_length=1, max_length=255)
    role: UserRole = UserRole.USER


class UserUpdateDTO(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    role: Optional[UserRole] = None
    password: Optional[str] = Field(None, min_length=6, max_length=255)


class TokenResponseDTO(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginRequestDTO(BaseModel):
    login: str
    password: str


class RefreshTokenRequestDTO(BaseModel):
    refresh_token: str


class UserListResponseDTO(BaseModel):
    items: list[UserDTO]
    total: int
    page: int
    page_size: int


class UserFilterDTO(BaseModel):
    role: Optional[UserRole] = None
    login: Optional[str] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)

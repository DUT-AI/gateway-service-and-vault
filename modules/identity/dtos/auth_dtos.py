from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """Schema for registering a new user."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    name: str | None = Field(None, max_length=255)


class UserLoginRequest(BaseModel):
    """Schema for authenticating a user."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema for JWT access token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """Schema for user profile responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str | None = None
    role: str
    avatar_url: str | None = None
    status: str
    created_at: datetime

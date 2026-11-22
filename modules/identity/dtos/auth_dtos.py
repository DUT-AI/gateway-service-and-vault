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
    role: str = "member"
    avatar_url: str | None = None
    status: str = "ACTIVE"
    role_names: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)
    created_at: datetime | None = None


class SsoLoginDataDTO(BaseModel):
    """DTO for the data payload returned by DUT-AI Manage /auth/login."""

    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    expires_in: int | None = None


class SsoUserDataDTO(BaseModel):
    """DTO for user data payload returned by DUT-AI Manage /auth/me."""

    id: int
    name: str | None = None
    email: str
    status: str = "ACTIVE"
    avatar_url: str | None = None
    role_names: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)
    zalo_bot_id: str | None = None
    is_deleted: bool = False

from pydantic import BaseModel, Field


class UserOptionResponse(BaseModel):
    id: int = Field(..., description="Unique user integer identifier")
    name: str
    email: str
    avatar_url: str | None = None


class UserDetailResponse(BaseModel):
    id: int = Field(..., description="Unique user integer identifier")
    name: str
    email: str
    phone_number: str | None = None
    status: str
    role_ids: list[int] = Field(default_factory=list)
    role_names: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)
    avatar_url: str | None = None
    discord_id: str | None = None
    zalo_bot_id: str | None = None
    check_in_card_code_configured: bool = False

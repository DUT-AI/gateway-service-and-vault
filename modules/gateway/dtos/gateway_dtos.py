from datetime import datetime

from pydantic import BaseModel, Field


class ProjectCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    slug: str = Field(..., min_length=2, max_length=100)
    description: str | None = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    slug: str
    description: str | None = None
    created_at: datetime


class RegisterClientRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    client_type: str = Field(default="USER_DEVICE")  # USER_DEVICE or APP_SERVER
    owner_id: str = Field(..., min_length=1, max_length=100)
    validity_days: int = Field(default=30, ge=1, le=365)


class RegisterClientResponse(BaseModel):
    id: str
    name: str
    client_type: str
    owner_id: str
    cert_fingerprint: str
    cert_serial: str
    cert_pem: str
    key_pem: str
    expires_at: datetime


class GenerateVirtualKeyRequest(BaseModel):
    client_id: str = Field(..., min_length=1)
    project_id: str = Field(..., min_length=1)


class GenerateVirtualKeyResponse(BaseModel):
    id: str
    client_id: str
    project_id: str
    virtual_key: str
    key_prefix: str
    status: str
    created_at: datetime


class VerifyBindingRequest(BaseModel):
    raw_virtual_key: str = Field(..., min_length=1)
    cert_fingerprint: str = Field(..., min_length=1)
    project_id: str = Field(..., min_length=1)


class VerifyBindingResponse(BaseModel):
    valid: bool
    message: str

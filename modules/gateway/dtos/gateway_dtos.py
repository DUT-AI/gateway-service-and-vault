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
    client_raw_cert: str | None = None
    project_id: str = Field(..., min_length=1)
    service_id: str | None = None
    service_slug: str | None = None


class VerifyBindingResponse(BaseModel):
    valid: bool
    message: str


class RevokeClientResponse(BaseModel):
    message: str
    client_id: str
    is_revoked: bool


class ClientSummaryResponse(BaseModel):
    id: str
    name: str
    client_type: str
    owner_id: str
    cert_fingerprint: str
    cert_serial: str
    expires_at: datetime
    is_revoked: bool
    created_at: datetime


class VirtualKeySummaryResponse(BaseModel):
    id: str
    client_id: str
    project_id: str
    key_prefix: str
    status: str
    created_at: datetime
    revoked_at: datetime | None = None


class UpstreamServiceCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    slug: str = Field(..., min_length=2, max_length=100)
    base_url: str = Field(..., min_length=5, max_length=255)
    auth_type: str = Field(default="BEARER_TOKEN")
    credential: str = Field(..., min_length=1)
    timeout_seconds: int = Field(default=30, ge=1, le=120)


class UpstreamServiceResponse(BaseModel):
    id: str
    name: str
    slug: str
    base_url: str
    auth_type: str
    timeout_seconds: int
    is_active: bool
    created_at: datetime


class ProjectAllowedServiceResponse(BaseModel):
    service_id: str
    service_name: str
    service_slug: str
    base_url: str
    auth_type: str
    is_service_active: bool
    rate_limit_rpm: int
    quota_daily: int
    is_quota_active: bool
    bound_at: datetime | None = None


class BindServiceToProjectRequest(BaseModel):
    service_id: str = Field(..., min_length=26, max_length=26)
    rate_limit_rpm: int = Field(default=60, ge=1, le=100000)
    quota_daily: int = Field(default=10000, ge=1, le=10000000)


class UpdateServiceQuotaRequest(BaseModel):
    rate_limit_rpm: int = Field(default=60, ge=1, le=100000)
    quota_daily: int = Field(default=10000, ge=1, le=10000000)

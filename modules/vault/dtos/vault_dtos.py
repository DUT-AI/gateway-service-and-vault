from datetime import datetime

from pydantic import BaseModel, Field


class CreateSecretRequest(BaseModel):
    scope_name: str = Field(..., min_length=1, max_length=50)
    key: str = Field(..., min_length=1, max_length=100)
    value: str = Field(..., min_length=1)


class SecretResponse(BaseModel):
    id: str
    project_id: str
    scope_id: str
    key: str
    version: int
    created_at: datetime


class GetSecretsResponse(BaseModel):
    project_id: str
    scopes: dict[str, dict[str, str]]


class SecretUpdateEventPayload(BaseModel):
    """Payload streamed over SSE when secrets change."""

    event_id: str
    project_id: str
    scope_name: str
    changed_keys: list[str]
    new_version: int
    actor: str = ""
    timestamp: str


class StreamPingPayload(BaseModel):
    """Periodic heartbeat payload to prevent connection timeouts."""

    timestamp: str


class GrantKeyPermissionRequest(BaseModel):
    identity_id: str = Field(..., min_length=1, max_length=100)
    identity_type: str = Field(default="client", pattern="^(client|user)$")
    secret_key: str = Field(..., min_length=1, max_length=100)


class RevokeKeyPermissionRequest(BaseModel):
    identity_id: str = Field(..., min_length=1, max_length=100)
    secret_key: str = Field(..., min_length=1, max_length=100)


class KeyPermissionResponse(BaseModel):
    id: str
    project_id: str
    identity_id: str
    identity_type: str
    secret_key: str
    granted_by: str
    created_at: datetime


class IdentityPermissionsResponse(BaseModel):
    project_id: str
    identity_id: str
    permitted_keys: list[str]


class ScopeResponse(BaseModel):
    id: str
    project_id: str
    name: str
    description: str | None = None
    created_at: datetime

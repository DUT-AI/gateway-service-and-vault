from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AuditEventResponse(BaseModel):
    id: str
    timestamp: datetime
    client_type: str
    actor_id: str
    project_id: str
    service_id: str | None = None
    action: str
    decision: str
    client_ip: str | None = None
    error_code: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AuditEventListResponse(BaseModel):
    items: list[AuditEventResponse]
    total: int
    limit: int
    offset: int


class SecurityAlertItemResponse(BaseModel):
    alert_id: str
    severity: str  # HIGH, MEDIUM, LOW
    anomaly_type: str  # REPEATED_IDENTITY_MISMATCH
    description: str
    actor_id: str | None = None
    client_ip: str | None = None
    event_count: int
    first_seen_at: datetime
    last_seen_at: datetime


class SecurityAlertsResponse(BaseModel):
    alerts: list[SecurityAlertItemResponse]
    total_active: int

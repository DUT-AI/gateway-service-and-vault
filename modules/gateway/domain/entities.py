from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ClientType(str, Enum):
    USER_DEVICE = "USER_DEVICE"
    APP_SERVER = "APP_SERVER"


class KeyStatus(str, Enum):
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"


@dataclass
class ProjectEntity:
    id: str
    name: str
    slug: str
    description: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class UpstreamServiceEntity:
    id: str
    name: str
    slug: str
    base_url: str
    auth_type: str  # BEARER_TOKEN, API_KEY, BASIC
    encrypted_credential: str
    timeout_seconds: int = 30
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RegisteredClientEntity:
    id: str
    client_type: ClientType
    name: str
    owner_id: str  # User ID from DUT AI SSO or Application Service Name
    cert_fingerprint: str  # SHA-256 fingerprint of the client x509 cert
    cert_serial: str
    expires_at: datetime
    is_revoked: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class VirtualAccessKeyEntity:
    id: str
    key_hash: str  # SHA-256 of the virtual key
    key_prefix: str  # First 8 chars for identification (e.g. vk_live_ab12...)
    client_id: str
    project_id: str
    status: KeyStatus = KeyStatus.ACTIVE
    last_used_at: datetime | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    revoked_at: datetime | None = None


@dataclass
class QuotaPolicyEntity:
    id: str
    project_id: str
    service_id: str
    client_id: str | None = None  # None = applies to all clients of the project
    rate_limit_rpm: int = 60  # Requests per minute
    quota_daily: int = 10000  # Requests per day
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AuditEventEntity:
    id: str
    timestamp: datetime
    client_type: ClientType
    actor_id: str
    project_id: str
    service_id: str | None
    action: str  # API_CALL, SECRET_READ, KEY_GENERATED, IDENTITY_MISMATCH
    decision: str  # ALLOW, DENY
    client_ip: str | None = None
    error_code: str | None = None
    metadata: dict = field(default_factory=dict)


@dataclass
class SecurityAlertEntity:
    alert_id: str
    severity: str  # HIGH, MEDIUM, LOW
    anomaly_type: str  # REPEATED_IDENTITY_MISMATCH
    description: str
    actor_id: str | None
    client_ip: str | None
    event_count: int
    first_seen_at: datetime
    last_seen_at: datetime

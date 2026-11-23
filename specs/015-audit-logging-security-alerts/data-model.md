# Data Model: Audit Logging & Security Alerts (Phase 3)

**Branch**: `015-audit-logging-security-alerts` | **Date**: 2026-11-23

## 1. Domain Entities (`modules/gateway/domain/entities.py`)

### `AuditEventEntity`
Represents an immutable record of an access attempt or security event.
```python
@dataclass
class AuditEventEntity:
    id: str
    timestamp: datetime
    client_type: ClientType  # USER_DEVICE, APP_SERVER
    actor_id: str  # Client ID, User ID, or "UNKNOWN"
    project_id: str  # Project ULID or "UNKNOWN"
    service_id: str | None  # Service ULID if targeting a service
    action: str  # GATEWAY_ACCESS, SSO_LOGIN, SECRET_READ, etc.
    decision: str  # ALLOW, DENY
    client_ip: str | None = None
    error_code: str | None = None  # IDENTITY_MISMATCH, DAILY_QUOTA_EXCEEDED, etc.
    metadata: dict = field(default_factory=dict)
```

### `SecurityAlertEntity`
Represents a synthesized anomaly alert computed from recent audit events.
```python
@dataclass
class SecurityAlertEntity:
    alert_id: str
    severity: str  # HIGH, MEDIUM, LOW
    anomaly_type: str  # REPEATED_IDENTITY_MISMATCH, RATE_LIMIT_BURST
    description: str
    actor_id: str | None
    client_ip: str | None
    event_count: int
    first_seen_at: datetime
    last_seen_at: datetime
```

---

## 2. Persistence Model (`modules/gateway/models/audit.py`)

Maps to PostgreSQL table `audit_events`:
```python
class AuditEventModel(Base, ULIDPrimaryKeyMixin):
    __tablename__ = "audit_events"

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        index=True,
        nullable=False,
    )
    client_type: Mapped[str] = mapped_column(String(20), nullable=False)
    actor_id: Mapped[str] = mapped_column(
        String(100), index=True, nullable=False
    )
    project_id: Mapped[str] = mapped_column(
        String(26), index=True, nullable=False
    )
    service_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    action: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    decision: Mapped[str] = mapped_column(String(10), nullable=False)
    client_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(
        "metadata", JSON, default=dict, nullable=False
    )
```

Indexes:
- `ix_audit_events_timestamp` on `timestamp`
- `ix_audit_events_actor_id` on `actor_id`
- `ix_audit_events_project_id` on `project_id`
- `ix_audit_events_action` on `action`

---

## 3. Data Transfer Objects (DTOs in `modules/gateway/dtos/audit_dtos.py`)

### `AuditEventResponse`
```python
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
```

### `AuditEventListResponse`
```python
class AuditEventListResponse(BaseModel):
    items: list[AuditEventResponse]
    total: int
    limit: int
    offset: int
```

### `SecurityAlertItemResponse`
```python
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
```

### `SecurityAlertsResponse`
```python
class SecurityAlertsResponse(BaseModel):
    alerts: list[SecurityAlertItemResponse]
    total_active: int
```

---

## 4. Repository Interface (`modules/gateway/domain/interfaces.py`)

```python
class IAuditEventRepository(ABC):
    @abstractmethod
    async def record_event(
        self,
        event: AuditEventEntity,
    ) -> AuditEventEntity:
        """Persist an immutable audit log record."""
        ...

    @abstractmethod
    async def list_events(
        self,
        project_id: str | None = None,
        client_type: str | None = None,
        decision: str | None = None,
        action: str | None = None,
        error_code: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[AuditEventEntity], int]:
        """Query audit events with filters and total count."""
        ...

    @abstractmethod
    async def get_security_alerts(
        self,
        window_minutes: int = 5,
        threshold: int = 3,
    ) -> list[SecurityAlertEntity]:
        """Detect real-time anomalies (e.g. repeated identity mismatches)."""
        ...
```

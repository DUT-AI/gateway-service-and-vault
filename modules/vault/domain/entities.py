import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class SecretScopeEntity:
    id: str
    project_id: str
    name: str  # e.g., Common, Financial, Auth-Core
    description: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class SecretItemEntity:
    id: str
    project_id: str
    scope_id: str
    key: str
    encrypted_value: str
    nonce: str
    auth_tag: str
    version: int = 1
    created_by: str = ""
    updated_by: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class SecretHistoryEntity:
    id: str
    secret_id: str
    version: int
    encrypted_value: str
    nonce: str
    auth_tag: str
    modified_by: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class ConfigChangeEvent:
    """Pure domain event emitted upon secret configuration changes."""

    project_id: str
    scope_name: str
    changed_keys: list[str]
    new_version: int
    actor: str = ""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "project_id": self.project_id,
            "scope_name": self.scope_name,
            "changed_keys": self.changed_keys,
            "new_version": self.new_version,
            "actor": self.actor,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class KeyPermissionEntity:
    """Pure domain entity for identity-to-key authorization grants."""

    id: str
    project_id: str
    identity_id: str
    secret_key: str
    identity_type: str = "client"  # "client" or "user"
    granted_by: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def is_wildcard(self) -> bool:
        return self.secret_key == "*"

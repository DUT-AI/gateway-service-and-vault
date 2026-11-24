"""Gateway SQL Repositories.

This module re-exports repository implementations for backward compatibility.
Direct imports from specific repository modules or package __init__ are preferred.
"""

from modules.gateway.repository.project_repository import SqlProjectRepository
from modules.gateway.repository.quota_policy_repository import SqlQuotaPolicyRepository
from modules.gateway.repository.registered_client_repository import (
    SqlRegisteredClientRepository,
)
from modules.gateway.repository.upstream_service_repository import (
    SqlUpstreamServiceRepository,
)
from modules.gateway.repository.virtual_access_key_repository import (
    SqlVirtualAccessKeyRepository,
)

__all__ = [
    "SqlProjectRepository",
    "SqlQuotaPolicyRepository",
    "SqlRegisteredClientRepository",
    "SqlUpstreamServiceRepository",
    "SqlVirtualAccessKeyRepository",
]

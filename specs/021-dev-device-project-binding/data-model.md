# Data Model: Dev Device Self-Registration & Project Key Binding

**Feature**: `021-dev-device-project-binding` | **Date**: 2026-11-25

No database schema changes required. Uses existing `registered_clients`, `project_members`, and `virtual_access_keys` tables.

- `IRegisteredClientRepository.list_by_owner_ids(owner_ids: list[str]) -> list[RegisteredClientEntity]`
- `ListVirtualKeysUseCase.execute(project_id: str, owner_id_filter: str | None = None)`

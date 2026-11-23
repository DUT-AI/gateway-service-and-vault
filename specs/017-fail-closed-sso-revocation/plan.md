# Implementation Plan: Fail-Closed Hardening & SSO Deactivation Sync (Phase 5)

**Branch**: `017-fail-closed-sso-revocation` | **Date**: 2026-11-23 | **Spec**: [specs/017-fail-closed-sso-revocation/spec.md](file:///Users/nguyenhuynh/Documents/projects/gateway-service-and-vault/specs/017-fail-closed-sso-revocation/spec.md)

## Summary
Implement automated revocation sync when central SSO users are deactivated and harden gateway fail-closed mechanisms:
1. Extend `IRegisteredClientRepository` with `list_by_owner_id(owner_id: str) -> list[RegisteredClientEntity]`.
2. Implement `SyncSsoUserRevocationUseCase` in `modules/identity/use_cases/sync_sso_user_revocation.py` to revoke all devices and virtual keys owned by a given user.
3. Expose endpoint `POST /api/v1/identity/users/{user_id}/sync-revocation` in `apps/api/routers/auth_router.py`.
4. Review and harden `apps/apisix/plugins/identity-binding-filter.lua` fail-closed error handling (returning `403` with `error: "CONTROL_PLANE_UNAVAILABLE"` on connection error or 5xx).
5. Create regression test suite `tests/integration/test_fail_closed.py`.

## Technical Context
- **Language/Version**: Python 3.12 (Backend), Lua 5.1 (APISIX OpenResty).
- **Primary Dependencies**: FastAPI, Dishka IoC, SQLAlchemy (asyncpg), Apache APISIX.
- **Testing**: `pytest`, `pytest-asyncio`, `httpx`.

## Constitution Check
- **V. Standardized DUT-AI SSO & Identity**: Integrates lifecycle synchronization with external SSO users identified by native integer IDs. (PASS)
- **VIII. Zero-Trust Identity Binding & Gateway**: Strictly enforces Fail-Closed policy: no traffic can pass to upstream if Control Plane verification fails. (PASS)

## Project Structure
```text
specs/017-fail-closed-sso-revocation/
├── spec.md
├── plan.md
└── tasks.md
```

## Architecture & Implementation Steps

### Phase 1: Repository Layer Extension
- Add `list_by_owner_id(owner_id: str) -> list[RegisteredClientEntity]` to `IRegisteredClientRepository` in `modules/gateway/domain/interfaces.py`.
- Implement in `SqlRegisteredClientRepository` (`modules/gateway/repository/gateway_repository.py`).

### Phase 2: SSO User Revocation Sync Use Case & API
- Create `SyncSsoUserRevocationUseCase` in `modules/identity/use_cases/sync_sso_user_revocation.py`.
- Bind in Dishka container (`modules/identity/di.py`).
- Expose endpoint `POST /api/v1/identity/users/{user_id}/sync-revocation` in `apps/api/routers/auth_router.py`.

### Phase 3: APISIX Fail-Closed Hardening
- In `apps/apisix/plugins/identity-binding-filter.lua`, distinguish between Control Plane network failure / 5xx (`CONTROL_PLANE_UNAVAILABLE`) and identity mismatch, while ensuring both return `403 Forbidden` (fail-closed).

### Phase 4: Integration Testing & Verification
- Create `tests/integration/test_fail_closed.py` covering:
  1. Revoking an SSO user automatically revokes all their clients and virtual keys.
  2. Simulated Control Plane timeout/500 fails closed with 403.
- Run full quality checks: `uv run ruff check .`, `uv run pytest tests/`, and `make test-e2e`.
- Update `docs/CHECKLIST_REMAINING_TASKS.md`.

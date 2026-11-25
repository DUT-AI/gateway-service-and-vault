# Research & Architectural Decisions: mTLS Client & Key UX + Ownership Scoping

**Feature**: `020-mtls-client-ux-scoping` | **Date**: 2026-11-25

## 1. Reuse Existing `registered_clients.owner_id` Column

- **Decision**: Leverage the existing `registered_clients.owner_id` (`String(100)`, indexed) and `IRegisteredClientRepository.list_by_owner_id(owner_id: str)` rather than adding a new column or migration.
- **Rationale**: `RegisteredClientModel` already stores `owner_id` and `SqlRegisteredClientRepository.list_by_owner_id` is already implemented in `modules/gateway/repository/registered_client_repository.py`.
- **Alternatives Considered**: Altering `owner_id` to `Integer`: Rejected because legacy machine/test fixtures may use string identifiers, and `str(user_ctx.user_id)` maps cleanly without breaking migrations.

## 2. Self-Issued Ownership Enforcement on `POST /clients`

- **Decision**: Override `owner_id = str(user_ctx.user_id)` inside `apps/api/routers/gateway/clients.py` for ALL authenticated callers (`ADMIN` and `PROJECT_DEVELOPER`), and make `RegisterClientRequest.owner_id` optional (`str | None = None`).
- **Rationale**: Satisfies the clarified rule that certificates/keys are strictly self-issued by the user themselves (nobody creates certificates on behalf of another user) and eliminates `owner_id` spoofing.

## 3. Clean Ownership Check in `RevokeClientUseCase`

- **Decision**: Add `ClientOwnershipDeniedError` to `modules/gateway/use_cases/exceptions.py` and enforce `if not is_admin and client.owner_id != caller_owner_id: raise ClientOwnershipDeniedError(...)` inside `RevokeClientUseCase.execute()`.
- **Rationale**: Keeps business authorization rules inside the Application Use Case layer per Constitution Principle I, while the router maps `ClientOwnershipDeniedError` to `HTTP 403 Forbidden`.

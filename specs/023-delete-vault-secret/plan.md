# Implementation Plan: Delete Vault Environment Variable

**Branch**: `023-delete-vault-secret` | **Date**: 2026-11-26 | **Spec**: [spec.md](file:///Users/nguyenhuynh/Documents/projects/gateway-service-and-vault/specs/023-delete-vault-secret/spec.md)

**Input**: Feature specification from `/specs/023-delete-vault-secret/spec.md`

## Summary

Implement end-to-end deletion of Vault environment variables (`DELETE /api/v1/vault/projects/{project_id}/secrets?scope_name=...&key=...`) via `DeleteSecretUseCase`, repository isolation (`ISecretRepository.delete_secret`), 3-tier RBAC + key-permission enforcement, SSE change broadcasting, OpenAPI type sync (`make api-types`), and a modular `DeleteSecretDialog` + row delete action in `SecretsTable`.

## Technical Context

**Language/Version**: Python 3.12+ (FastAPI, Dishka, SQLAlchemy 2.0 async) & TypeScript 5 / React 19 / Next.js 16  
**Primary Dependencies**: FastAPI, Dishka, SQLAlchemy asyncpg, Pydantic v2, TanStack React Query, Tailwind CSS v4, Radix UI  
**Storage**: PostgreSQL (`secrets`, `secret_versions`, `key_permissions`) + Redis Pub/Sub (SSE)  
**Testing**: `uv run pytest`, `uv run ruff check`, `make api-types`, `cd web && pnpm typecheck`, `npx eslint`  
**Target Platform**: Linux Docker / macOS local dev  
**Project Type**: Modular Monolith + Next.js Frontend  
**Performance Goals**: Single-query deletion + immediate SSE invalidation (<100ms API response)  
**Constraints**: Zero `session.commit()` in repositories; thin router (Dishka `DeleteSecretUseCase` only); `make api-types` synced  
**Scale/Scope**: Vault module (`domain`, `repository`, `use_cases`, `dtos`, `di`), API router (`apps/api/routers/vault/secrets.py`), Frontend (`web/src/features/vault/`)

## Constitution Check

- **I. Clean Architecture & Thin Presentation Layer**: Pass — router delegates exclusively to `FromDishka[DeleteSecretUseCase]`; `SqlSecretRepository.delete_secret` never calls `session.commit()`.
- **IV. Offline Contract & Type Synchronization**: Pass — `DeleteSecretResponse` defined in Pydantic and synced via `make api-types`.
- **V. Standardized 3-Tier RBAC**: Pass — uses `UserContext` / `RoleTier` + `ensure_project_access` + `IKeyPermissionRepository`.
- **VII. Real-Time Hot-Reload**: Pass — publishes `ConfigChangeEvent` via `IVaultBroadcaster`.

## Project Structure

### Source Code (repository root)

```text
modules/vault/
├── domain/interfaces.py               # Add ISecretRepository.delete_secret
├── dtos/vault_dtos.py                 # Add DeleteSecretResponse
├── repository/secret_repository.py    # Implement SqlSecretRepository.delete_secret
├── use_cases/delete_secret.py         # New DeleteSecretUseCase
├── use_cases/__init__.py              # Export DeleteSecretUseCase
└── di.py                              # Provide DeleteSecretUseCase

apps/api/routers/vault/secrets.py      # Add DELETE /projects/{project_id}/secrets

web/src/features/vault/
├── services/vault-service.ts          # Add deleteSecret(projectId, scopeName, key)
├── hooks/use-vault-queries.ts         # Add useDeleteSecretMutation(projectId)
└── components/
    ├── delete-secret-dialog.tsx       # Confirmation dialog component
    ├── secrets-table.tsx              # Add Delete action button per row
    └── vault-view.tsx                 # Wire deleteSecret state & DeleteSecretDialog

tests/integration/
└── test_delete_vault_secret.py        # Integration tests for 200, 403, 404
```

## Complexity Tracking

No constitution violations; no complexity exceptions required.

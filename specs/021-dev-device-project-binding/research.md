# Research & Architectural Decisions: Regular Dev Device & Project Key Binding

**Feature**: `021-dev-device-project-binding` | **Date**: 2026-11-25

## 1. Project-Scoped Available Clients Endpoint

- **Decision**: Add `GET /api/v1/gateway/projects/{project_id}/available-clients` backed by `ListProjectAvailableClientsUseCase`.
- **Rationale**:
  - Keeping `GET /gateway/clients` strictly scoped to `owner_id == str(user_ctx.user_id)` for non-admins prevents Developers from browsing random personal devices outside their project.
  - Inside an assigned project, `ListProjectAvailableClientsUseCase` queries `IProjectMemberRepository.list_members(project_id)`, collects `{str(m.user_id) for m in members}` (plus the caller's own ID), and calls `IRegisteredClientRepository.list_by_owner_ids(owner_ids)` returning only active (non-revoked, non-expired) clients.
  - For `ADMIN`, it returns all active clients across the system.
- **Alternatives Considered**: Returning all system clients in `GET /gateway/clients` to `PROJECT_DEVELOPER`: Rejected because it violates least-privilege and exposes devices of users not assigned to the project.

## 2. Read-Only Virtual Keys for `Tier 3` (`OTHER`)

- **Decision**: Allow `get_current_user_context` (any authenticated member of the project) on `GET /api/v1/gateway/projects/{project_id}/keys`. When `user_ctx.is_other`, `ListVirtualKeysUseCase` filters keys to those whose `client_id` is owned by `str(user_ctx.user_id)`.
- **Rationale**: Lets regular developers verify that their device has been bound to the project and check key status without exposing other members' keys or allowing key creation/revocation.

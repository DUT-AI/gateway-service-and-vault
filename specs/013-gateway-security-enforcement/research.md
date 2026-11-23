# Phase 0 Research & Technical Decisions: Core Security & Gateway Enforcement

**Feature Branch**: `013-gateway-security-enforcement`

---

## 1. APISIX Custom Lua Plugin Mounting & Execution Configuration

### Context & Challenge
The `identity-binding-filter.lua` script exists in `./apps/apisix/plugins/`, but the APISIX Docker container currently only mounts `./apps/apisix/conf/config.yaml`. Furthermore, `config.yaml` has not declared `extra_lua_path` or registered `identity-binding-filter` in its active plugins list. As a result, APISIX routes currently bypass hardware identity verification.

### Decision
1. **Container Volume Mount in `docker-compose.yml`**:
   Mount `./apps/apisix/plugins` as read-only volume inside the container:
   ```yaml
   apisix:
     image: apache/apisix:3.9.0-debian
     volumes:
       - ./apps/apisix/conf/config.yaml:/usr/local/apisix/conf/config.yaml:ro
       - ./apps/apisix/plugins:/usr/local/apisix/plugins:ro
   ```
2. **APISIX Plugin Registration in `apps/apisix/conf/config.yaml`**:
   Add `extra_lua_path` to the Lua module search path and append `identity-binding-filter` to the active plugins:
   ```yaml
   apisix:
     node_listen: 9080
     ssl:
       enable: true
       listen_port: 9443
     extra_lua_path: "/usr/local/apisix/plugins/?.lua"
   plugins:
     - proxy-rewrite
     - limit-count
     - identity-binding-filter
   ```

### Alternatives Considered
- *Baked Docker Image*: Building a custom Dockerfile extending `apache/apisix`. Rejected because volume mounting local plugin files simplifies development and dynamic testing without rebuild overhead.

---

## 2. Dynamic Service Slug Extraction & Scoping in Lua Filter

### Context & Challenge
Customer Requirement "Đúng dự án, đúng dịch vụ" (FR-10) requires that a client presenting a valid key for Project A cannot call Service B unless Project A has explicitly bound Service B in its allowlist. The existing `identity-binding-filter.lua` only sent `raw_virtual_key`, `cert_fingerprint`, and `project_id`, without informing the Control Plane which upstream service was being accessed.

### Decision
1. **URI Slug Extraction in Lua**:
   All upstream routes match `/services/{service_slug}/*`. In `_M.rewrite(conf, ctx)`:
   ```lua
   local service_slug = string.match(ngx.var.uri or "", "^/services/([^/]+)")
   ```
2. **Mandatory mTLS Certificate Check**:
   ```lua
   local cert_fingerprint = ngx.var.ssl_client_fingerprint
   if not cert_fingerprint or cert_fingerprint == "" then
       core.log.error("Client did not present a valid mTLS certificate")
       return 403, { error = "MTLS_REQUIRED", message = "Valid client certificate required" }
   end
   ```
3. **Payload Enhancement to Control Plane**:
   ```lua
   local payload = {
       raw_virtual_key = virtual_key,
       cert_fingerprint = cert_fingerprint,
       project_id = project_id,
       service_slug = service_slug,
   }
   ```
4. **Backend Resolution**:
   In `VerifyIdentityBindingUseCase`, if `service_slug` is provided:
   - Query `service_repo.get_by_slug(service_slug)`. If not found, raise `ServiceNotPermittedError`.
   - Call `project_repo.is_service_allowed(project_id, service.id)`. If `False`, raise `ServiceNotPermittedError`.

### Alternatives Considered
- *Passing `service_id` directly from APISIX route metadata*: Would require hardcoding internal ULIDs into APISIX route configurations. Using `service_slug` extracted from the public URL path `/services/{slug}/*` keeps APISIX routes decoupled from database primary keys.

---

## 3. Atomic Hardware Device Revocation (Revoke Client)

### Context & Challenge
Section 3.1 & 3.3 of `mo_ta.md` mandates that when a developer departs or a laptop/server is compromised, revoking the registered client must immediately invalidate the device certificate and all virtual keys associated with it.

### Decision
1. **Repository Method**:
   In `modules/gateway/repository/gateway_repository.py`:
   ```python
   async def revoke_client(self, client_id: str) -> bool:
       now = datetime.now(UTC)
       # 1. Mark client as revoked
       stmt_client = (
           update(RegisteredClientModel)
           .where(RegisteredClientModel.id == client_id)
           .values(is_revoked=True)
       )
       res = await self.session.execute(stmt_client)
       if res.rowcount == 0:
           return False
       
       # 2. Revoke all active virtual keys for this client
       stmt_keys = (
           update(VirtualAccessKeyModel)
           .where(
               VirtualAccessKeyModel.client_id == client_id,
               VirtualAccessKeyModel.status == KeyStatus.ACTIVE.value,
           )
           .values(status=KeyStatus.REVOKED.value, revoked_at=now)
       )
       await self.session.execute(stmt_keys)
       await self.session.commit()
       return True
   ```
2. **Use Case & API Router**:
   `RevokeClientUseCase` executes `client_repo.revoke_client(client_id)`.
   FastAPI exposes `POST /api/v1/gateway/clients/{client_id}/revoke`.
   When `VerifyIdentityBindingUseCase` encounters a client with `is_revoked == True`, it immediately raises `IdentityMismatchError("Client is not found or revoked")`.

---

## 4. Web UI Revocation Interaction & Optimistic Cache Invalidation

### Context & Challenge
Revoking a hardware client is a destructive security operation that permanently prevents the device from connecting. The UI must provide clear warnings and instantly reflect the new state.

### Decision
1. **Confirmation Dialog**:
   Use Radix UI `AlertDialog` prompting:
   - Title: "Xác nhận thu hồi thiết bị?"
   - Content: "Hành động này sẽ vô hiệu hóa vĩnh viễn chứng chỉ của thiết bị và thu hồi toàn bộ Virtual Keys đang hoạt động liên kết với thiết bị này."
2. **Cache Invalidation**:
   On mutation success:
   - Invalidate `['registered-clients']`
   - Invalidate `['virtual-keys']`
   - Invalidate `['projects']` (to refresh active key counts)
   - Show success toast: "Thiết bị đã được thu hồi thành công."
3. **Table Row Presentation**:
   - Status badge displays red `Đã thu hồi` (`REVOKED`).
   - The "Thu hồi" action button is disabled and replaced with a tooltip "Thiết bị đã bị vô hiệu hóa".

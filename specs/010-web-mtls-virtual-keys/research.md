# Research & Technical Decisions: Web Phase 4 - mTLS Device Management & Virtual Keys (Zero-Trust Gatekeeper)

**Feature Branch**: `010-web-mtls-virtual-keys`  
**Date**: 2026-11-23  
**Status**: Completed  

---

## 1. Client-Side X.509 Certificate & Private Key File Download

### Decision
Use native Web APIs (`Blob`, `URL.createObjectURL`, and programmatic `<a>` element triggering) to deliver generated X.509 certificates (`client.crt`) and private keys (`client.key`) directly to the user's local disk without third-party dependencies.

### Rationale
- **Zero Third-Party Dependency**: Eliminates external bundle overhead (such as `file-saver` or `jszip`) by using standard browser primitives supported in 100% of modern browsers.
- **Security & Zero-Disk Browser Retention**: The raw private key PEM (`key_pem`) and certificate PEM (`cert_pem`) reside in component state solely while the modal is open. Object URLs created via `URL.createObjectURL` are immediately revoked via `URL.revokeObjectURL` after triggering download. When the modal closes, React garbage-collects the state, ensuring private keys are never persisted in `localStorage`, `sessionStorage`, or IndexedDB.
- **Target MIME Types**:
  - `client.crt`: MIME type `application/x-x509-ca-cert`
  - `client.key`: MIME type `application/pkcs8` or `text/plain`

### Implementation Pattern
```typescript
export function triggerFileDownload(filename: string, content: string, mimeType: string) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
  URL.revokeObjectURL(url);
}
```

### Alternatives Considered
- *Zip Archive Generation (JSZip)*: Adds ~100KB to client bundle and complicates quick access on developer machines where users simply want individual files to put into `~/.dut-vault/`. Separate direct download buttons ("Tải client.crt" and "Tải client.key") plus a sequential "Tải cả hai tệp" action provide a superior and lightweight developer experience.

---

## 2. One-Time Virtual Access Key & Secret Display Guardrails

### Decision
Implement a strict two-stage modal workflow for key generation:
1. **Selection Stage**: User selects a project and active client device from a dropdown, then submits.
2. **Display & Copy Stage**: The full raw token (e.g., `vkey_dev_...`) is presented inside an amber-bordered alert with explicit "Chỉ hiển thị 1 lần duy nhất" warning, an interactive copy button with animated checkmark feedback, and a pre-formatted CLI execution snippet:
   ```bash
   dut-vault run --key=vkey_dev_... -- python main.py
   ```
Upon closing the modal, the full raw token is discarded and only the prefix (e.g., `vkey_dev_ab12...`) remains visible in subsequent queries.

### Rationale
- Complies with Zero-Trust best practices: raw tokens cannot be retrieved again from the backend.
- Prevents user error by offering one-click copy for both the raw key and the exact CLI command needed to execute code.

### Alternatives Considered
- *Persisting key in temporary session storage*: Rejected. Directly violates Principle VIII and security requirements.

---

## 3. Client Device Selection & Revocation Guardrails

### Decision
When generating Virtual Keys, the client device dropdown MUST:
1. Fetch all registered clients via `useClientsQuery` (`GET /api/v1/gateway/clients`).
2. Filter or disable clients that are revoked (`is_revoked === true`) or expired (`new Date(expires_at) < new Date()`).
3. Display clear status badges (`Developer PC` vs `Workload Server`) and truncated fingerprints so users can distinguish between multiple devices owned by the same user.

### Rationale
- A virtual key bound to a revoked or expired client certificate will always be rejected with `HTTP 403` by the APISIX `identity-binding-filter`. Preventing issuance in the frontend UI avoids broken deployments and operator confusion.

---

## 4. Virtual Key Revocation UX & Cache Invalidation

### Decision
Implement key revocation via a two-step confirmation pattern:
1. Clicking "Thu hồi" on any active virtual key triggers a Radix/Base UI confirmation modal detailing the key prefix and affected bound client.
2. Upon confirmation, execute `POST /api/v1/gateway/keys/{key_id}/revoke`.
3. Invalidate TanStack Query key `["projects", projectId, "keys"]`, causing immediate re-fetch.
4. Display a Sonner success toast and visually transition the key status badge from `ACTIVE` (emerald) to `REVOKED` (rose).

### Rationale
- Instant revocation prevents token misuse during security incidents.
- Confirmation dialog prevents accidental destruction of production or staging keys.

---

## 5. Clean Modular Architecture & Feature Separation

### Decision
Create two distinct feature directories in `web/src/features/`:
1. `web/src/features/clients/`:
   - `types/`: Domain models derived from `Schema<"ClientSummaryResponse">` and `Schema<"RegisterClientResponse">`.
   - `services/client-service.ts`: API client functions wrapping `/api/v1/gateway/clients`.
   - `hooks/use-clients-queries.ts`: TanStack Query hooks `useClientsQuery` and `useRegisterClientMutation`.
   - `components/clients-table.tsx`: Data table with search filter, badge statuses, and registration button.
   - `components/register-client-dialog.tsx`: Form dialog with Zod validation.
   - `components/cert-download-dialog.tsx`: Download view displaying cert fingerprint and download triggers.
2. `web/src/features/keys/`:
   - `types/`: Domain models derived from `Schema<"VirtualKeySummaryResponse">` and `Schema<"GenerateVirtualKeyResponse">`.
   - `services/key-service.ts`: API client functions for listing, generating, and revoking keys.
   - `hooks/use-keys-queries.ts`: `useProjectKeysQuery`, `useGenerateKeyMutation`, `useRevokeKeyMutation`.
   - `components/virtual-keys-table.tsx`: Data table listing keys, client binding, status, and revoke trigger.
   - `components/generate-key-modal.tsx`: Modal for generating keys and one-time display.
   - `components/virtual-keys-view.tsx`: Parent container component mounted inside `ProjectWorkspaceTabs`.

### Rationale
- Maintains strict feature encapsulation per frontend guidelines.
- Decouples client device inventory (system-wide `/clients`) from project-scoped key issuance (`/projects/[id]`).

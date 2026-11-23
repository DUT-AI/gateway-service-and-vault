# Data Model: Web Phase 4 - mTLS Device Management & Virtual Keys (Zero-Trust Gatekeeper)

**Feature Branch**: `010-web-mtls-virtual-keys`  
**Date**: 2026-11-23  
**Status**: Completed  

---

## 1. Domain Entities & Type Mappings

All frontend types strictly derive from the authoritative backend OpenAPI schemas via `Schema<T>` in `web/src/types/api.generated.d.ts`.

```
┌─────────────────────────────────┐                 ┌─────────────────────────────────┐
│             Client              │                 │           VirtualKey            │
│  (Device / Machine Identity)    │ 1             * │     (Zero-Trust Access Token)   │
├─────────────────────────────────┼─────────────────┼─────────────────────────────────┤
│ id: string (UUID)               │                 │ id: string (UUID)               │
│ name: string                    │                 │ client_id: string (FK)          │
│ client_type: USER_DEVICE | ...  │                 │ project_id: string (FK)         │
│ owner_id: string                │                 │ key_prefix: string              │
│ cert_fingerprint: string        │                 │ status: ACTIVE | REVOKED        │
│ cert_serial: string             │                 │ created_at: string (ISO 8601)   │
│ expires_at: string              │                 │ revoked_at?: string | null      │
│ is_revoked: boolean             │                 └─────────────────────────────────┘
│ created_at: string              │
└─────────────────────────────────┘
```

---

## 2. Client Domain Models (`web/src/features/clients/types/index.ts`)

### `Client` (Summary Model)
Represents a registered developer workstation or workload server in the inventory.
- **Backend Schema**: `Schema<"ClientSummaryResponse">`
- **Fields**:
  - `id`: `string` - Unique identifier for the client record.
  - `name`: `string` - Human-readable device name (e.g., "MacBook Pro M3", "Staging Runner 01").
  - `client_type`: `ClientType` - `"USER_DEVICE" | "APP_SERVER"`.
  - `owner_id`: `string` - User ID of the owner.
  - `cert_fingerprint`: `string` - SHA-256 fingerprint of the issued X.509 certificate.
  - `cert_serial`: `string` - Certificate serial number.
  - `expires_at`: `string` - Expiration date-time in ISO 8601 format.
  - `is_revoked`: `boolean` - Revocation status.
  - `created_at`: `string` - Registration timestamp in ISO 8601 format.

### `RegisterClientInput`
Form input payload sent when registering a new device.
- **Backend Schema**: `Schema<"RegisterClientRequest">`
- **Fields**:
  - `name`: `string` - Device name (2–64 characters).
  - `client_type`: `ClientType` - Defaults to `"USER_DEVICE"`.
  - `owner_id`: `string` - Authenticated user identity ID.
  - `validity_days`: `number` - Certificate validity in days (30, 90, 365; defaults to 30).

### `RegisterClientResult` (Certificate Bundle)
Returned **one time only** immediately after registration.
- **Backend Schema**: `Schema<"RegisterClientResponse">`
- **Fields**:
  - `id`: `string` - Client ID.
  - `name`: `string` - Device name.
  - `client_type`: `string` - Client type.
  - `owner_id`: `string` - Owner ID.
  - `cert_fingerprint`: `string` - SHA-256 certificate fingerprint.
  - `cert_serial`: `string` - Certificate serial number.
  - `cert_pem`: `string` - Full X.509 certificate in PEM format.
  - `key_pem`: `string` - Full private key in PKCS#8 PEM format (**One-Time Secret**).
  - `expires_at`: `string` - Expiration timestamp.

---

## 3. Virtual Key Domain Models (`web/src/features/keys/types/index.ts`)

### `VirtualKey` (Summary Model)
Represents an issued virtual key bound to a specific client and project.
- **Backend Schema**: `Schema<"VirtualKeySummaryResponse">`
- **Fields**:
  - `id`: `string` - Virtual key ID.
  - `client_id`: `string` - Bound client ID.
  - `project_id`: `string` - Project ID.
  - `key_prefix`: `string` - Obfuscated token prefix (e.g., `vkey_dev_9a4f...`).
  - `status`: `VirtualKeyStatus` - `"ACTIVE" | "REVOKED"`.
  - `created_at`: `string` - Issuance timestamp.
  - `revoked_at`: `string | null` - Revocation timestamp (or null if active).

### `GenerateKeyInput`
Form input payload for issuing a new virtual key.
- **Backend Schema**: `Schema<"GenerateVirtualKeyRequest">`
- **Fields**:
  - `client_id`: `string` - Target client device ID.
  - `project_id`: `string` - Target project ID.

### `GenerateKeyResult`
Returned **one time only** immediately after key creation.
- **Backend Schema**: `Schema<"GenerateVirtualKeyResponse">`
- **Fields**:
  - `id`: `string` - Virtual key ID.
  - `client_id`: `string` - Bound client ID.
  - `project_id`: `string` - Project ID.
  - `virtual_key`: `string` - Full raw unmasked key token (**One-Time Secret**).
  - `key_prefix`: `string` - Key prefix.
  - `status`: `string` - Initial status (`"ACTIVE"`).
  - `created_at`: `string` - Creation timestamp.

---

## 4. UI View Models & State Transitions

### Lifecycle State Machine: Virtual Key
```
[POST /keys] ──> ( ACTIVE ) ──[POST /keys/{id}/revoke]──> ( REVOKED ) [Terminal]
```

### Lifecycle State Machine: Device Certificate
```
[POST /clients] ──> ( ISSUED / ACTIVE ) ──> ( EXPIRED ) / ( REVOKED )
```

### UI View State Models

```typescript
// Client Filter State
export interface ClientFilterState {
  searchQuery: string;
  typeFilter: "ALL" | "USER_DEVICE" | "APP_SERVER";
}

// Certificate Download Dialog State
export interface CertDownloadDialogState {
  isOpen: boolean;
  bundle: RegisterClientResult | null;
}

// Generate Key Modal State
export interface GenerateKeyModalState {
  isOpen: boolean;
  step: "FORM" | "RESULT";
  result: GenerateKeyResult | null;
}
```

---

## 5. Client-Side Validation Rules (Zod)

### Device Registration Schema
```typescript
import { z } from "zod";

export const registerClientSchema = z.object({
  name: z
    .string()
    .min(2, "Tên thiết bị phải có ít nhất 2 ký tự")
    .max(64, "Tên thiết bị không vượt quá 64 ký tự")
    .regex(/^[a-zA-Z0-9\s._-]+$/, "Tên thiết bị chỉ chứa chữ cái, số, dấu cách, gạch nối và dấu gạch dưới"),
  client_type: z.enum(["USER_DEVICE", "APP_SERVER"]),
  validity_days: z.number().refine((val) => [30, 90, 365].includes(val), {
    message: "Thời hạn hợp lệ phải là 30, 90 hoặc 365 ngày",
  }),
});
```

### Virtual Key Generation Schema
```typescript
import { z } from "zod";

export const generateKeySchema = z.object({
  client_id: z.string().min(1, "Vui lòng chọn thiết bị được cấp phép"),
  project_id: z.string().min(1, "Thiếu thông tin dự án"),
});
```

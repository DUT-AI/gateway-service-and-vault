# Implementation Plan: Post-Registration Certificate Onboarding UX

**Branch**: `022-cert-post-register-ux` | **Date**: 2026-11-25 | **Spec**: [spec.md](file:///Users/nguyenhuynh/Documents/projects/gateway-service-and-vault/specs/022-cert-post-register-ux/spec.md)

**Input**: Feature specification from `/specs/022-cert-post-register-ux/spec.md`

## Summary

Upgrade the post-registration mTLS certificate modal (`CertDownloadDialog`) into a clear, 3-step guided onboarding workflow: (1) Download `client.crt` & `client.key` with live completion tracking and all-trigger loss-prevention guardrails, (2) OS/environment-tabbed (`macOS / Linux`, `Windows`, `Docker`) copyable setup commands using the exact sanitized downloaded filenames, and (3) Role-aware & client-type-aware next steps (`isOtherRole` handoff summary vs Project Developer/Admin `/projects` CTA & Docker Workload guide + quick verification snippet).

## Technical Context

**Language/Version**: TypeScript 5 / React 19 / Next.js 16 (App Router)  
**Primary Dependencies**: Tailwind CSS v4, Radix UI / shadcn Dialog & Button & Badge, `lucide-react`, `sonner`, `useAuth()`  
**Storage**: N/A (client-side UI workflow consuming existing `RegisterClientResult`)  
**Testing**: `cd web && pnpm typecheck` (`tsc --noEmit`), `npx eslint`  
**Target Platform**: Modern desktop/mobile browsers  
**Project Type**: Web frontend feature module (`web/src/features/clients`)  
**Performance Goals**: Instant modal rendering and clipboard copy feedback (<50ms)  
**Constraints**: Pure client-side UI change; zero backend/API changes; preserve modular component boundaries (<250 lines per file)  
**Scale/Scope**: 1 utility file + 3 modular client components under `web/src/features/clients/`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Clean Architecture & Thin Presentation Layer**: Pass — purely frontend presentation components inside `web/src/features/clients/`.
- **IV. Offline Contract & Type Synchronization**: Pass — reuses existing `RegisterClientResult` typed from `api.generated.d.ts`; no manual backend payload interfaces added.
- **V. Standardized DUT-AI SSO & 3-Tier RBAC**: Pass — uses `useAuth().isOtherRole` (derived from `RoleTier`) rather than hardcoded role string checks.
- **VI. Zero .env Files**: Pass — guides users to store mTLS certs in `~/.dut-vault/` with `chmod 600`, not plaintext `.env` secrets.
- **VIII. Zero-Trust Identity Binding**: Pass — reinforces 1-time private key security and mTLS + Virtual Key binding workflow.

## Project Structure

### Documentation (this feature)

```text
specs/022-cert-post-register-ux/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── cert-onboarding-ui.md
└── tasks.md             # Phase 2 output (/speckit-tasks command)
```

### Source Code (repository root)

```text
web/src/features/clients/
├── utils/
│   └── download-file.ts                 # Add getClientCertFilenames(deviceName)
└── components/
    ├── clients-table.tsx                # Pass key={downloadBundle?.id} to CertDownloadDialog
    ├── cert-download-dialog.tsx         # 3-step modal shell + download state + close guardrail
    ├── cert-install-instructions.tsx    # Step 2 OS/Docker tabbed setup commands
    └── cert-next-steps-card.tsx         # Step 3 role-aware next actions & verification snippet
```

**Structure Decision**: Keep all changes scoped to `web/src/features/clients/` following the repo's feature-based architecture and modular component decomposition.

## Complexity Tracking

No constitution violations; no complexity exceptions required.

# Feature Specification: Real-Time In-Memory Dynamic Configuration & SDK Hot-Reload

**Feature Branch**: `004-vault-hot-reload`

**Created**: 2026-11-23

**Status**: Draft

**Input**: User description: "triển khai chức năng này Redis Pub/Sub, FastAPI SSE Stream, SDK cập nhật RAM < 5s"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Real-Time Configuration Change Broadcast and Delivery (Priority: P1)

As an Application Operator or Tech Lead, I need secret and configuration changes made on the Centralized Control Plane to be broadcast instantly and delivered over live event streams to all running client application instances, so that rotated credentials or updated parameters propagate everywhere without manual intervention.

**Why this priority**: Immediate, reliable event delivery is the core pipeline that eliminates configuration drift and removes the need for human coordination during secret rotations.

**Independent Test**: Connect an SSE client to the Control Plane stream endpoint for Project A. Modify a configuration variable in Project A on the Control Plane. Verify the client receives the `secret_update` event within 1 second.

**Acceptance Scenarios**:

1. **Given** an authenticated client is connected to the live event stream for Project A, **When** an Administrator updates or revokes a secret in Project A on the Control Plane, **Then** the event stream delivers a `secret_update` notification within 1 second containing the project ID, scope, and changed key names.
2. **Given** multiple clients connected across different projects (Client 1 on Project A, Client 2 on Project B), **When** a secret in Project A is updated, **Then** Client 1 receives the change notification and Client 2 receives zero notifications (strict project isolation).
3. **Given** an idle event stream with no configuration changes, **When** 15 seconds elapse, **Then** the server transmits a lightweight heartbeat ping to prevent connection timeout.

---

### User Story 2 - In-Memory Configuration Injection and Hot-Reload without Files (Priority: P2)

As a Developer or Application Runtime, I need the client SDK / process runner to inject configuration variables directly into process memory (RAM) upon startup and atomically mutate them in memory when update events arrive, leaving zero plaintext files on disk and requiring zero application restarts.

**Why this priority**: Enforces the absolute security mandate of eliminating plaintext `.env` files on developer laptops and Docker containers while achieving zero-downtime credential hot-reloads.

**Independent Test**: Launch a sample application process using the SDK runner. Verify all variables are accessible in process memory and no `.env` file exists on disk. Update a secret on the Control Plane. Verify the running application process accesses the updated value in memory within 5 seconds without restarting.

**Acceptance Scenarios**:

1. **Given** an application launched via the SDK runner, **When** the process initializes, **Then** authorized secrets for its assigned scope are available in process memory (`os.environ` or config object), and zero plaintext `.env` or temporary files exist on the filesystem.
2. **Given** an application running with the SDK live-reload listener active, **When** a `secret_update` event is received, **Then** the SDK fetches the updated decrypted value and updates its in-memory variable store within 5 seconds without restarting the process.
3. **Given** an application that registers a callback hook for a specific key (e.g. `on_change("DATABASE_URL")`), **When** that key is modified, **Then** the callback is executed with the updated value so dependent resources (such as connection pools) can re-initialize smoothly.

---

### Edge Cases

- **Transient Network Dropping / Disconnection**: When the network drops between the client SDK and the Control Plane, the client application continues running normally using its existing in-memory variables. Upon reconnecting, the SDK automatically checks the latest configuration version and performs a delta sync.
- **Malformed Event Payload**: If an unexpected payload is received over the stream, the SDK logs a diagnostic warning, keeps existing in-memory configurations intact, and does not crash the host application.
- **Rapid Burst Updates**: If an Administrator performs multiple rapid edits within hundreds of milliseconds, the SDK handles the incoming notifications atomically to avoid partial or corrupted in-memory state.
- **Unauthorized Project Stream Request**: If a client attempts to subscribe to an event stream for a project it is not authorized to access, the Control Plane immediately rejects the connection with HTTP 403 Forbidden.

## Requirements *(mandatory)*

### Functional Requirements

#### Domain 1: Event Broadcasting & Streaming Infrastructure
- **FR-001**: System MUST publish an internal event immediately (< 1 second) across the event bus whenever a secret is created, modified, or revoked.
- **FR-002**: System MUST expose an HTTP Server-Sent Events (SSE) streaming endpoint that streams real-time configuration notifications to authenticated clients.
- **FR-003**: System MUST isolate event stream delivery by Project ID, strictly preventing clients from receiving notifications intended for other projects.
- **FR-004**: System MUST transmit periodic heartbeat ping events (every 15 seconds) over active SSE streams to keep connections alive through intermediate load balancers or proxies.

#### Domain 2: In-Memory Client Ingestion & Hot-Reload (SDK)
- **FR-005**: System MUST provide an application SDK / CLI runner that fetches authorized secrets into process memory (RAM) at startup without writing `.env` or plaintext files to the local disk.
- **FR-006**: Client SDK MUST maintain a non-blocking background connection to the SSE stream and atomically update in-memory variables within 5 seconds of receiving a change notification.
- **FR-007**: Client SDK MUST allow applications to register change callbacks for specific configuration keys to support programmatic resource re-initialization upon credential rotation.
- **FR-008**: Client SDK MUST automatically reconnect to the event stream with exponential backoff if the network connection is interrupted.
- **FR-009**: System MUST enforce a strict zero-disk-artifact invariant across all developer workstations and container environments.

### Key Entities

- **ConfigChangeEvent**: Represents a notification that configuration state has changed; contains `project_id`, `scope_name`, list of `changed_keys`, `new_version`, and `timestamp`.
- **StreamSubscription**: Represents an active, authenticated client connection listening for configuration events for a specific Project.
- **InMemoryConfigStore**: The client-side runtime key-value dictionary residing purely in RAM, providing thread-safe reads and atomic mutations.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Configuration changes saved on the Control Plane are reflected in running client application memory in under 5 seconds (target < 2 seconds).
- **SC-002**: 100% of loaded configurations and rotated credentials reside purely in process RAM; zero plaintext `.env` files or disk artifacts are created.
- **SC-003**: Disconnected event streams automatically reconnect and re-synchronize configuration state within 3 seconds of network restoration.
- **SC-004**: Active event streaming connections maintain stability over 24+ hours of continuous operation without memory leakage or socket exhaustion.

## Assumptions

- Client applications run in environments with persistent outbound HTTP/HTTPS connectivity to the Control Plane.
- Applications using the SDK have sufficient memory to store decrypted configuration dictionaries in RAM (typically < 100 KB).
- Ephemeral network interruptions are tolerable since running applications maintain their active in-memory configuration until the stream reconnects.

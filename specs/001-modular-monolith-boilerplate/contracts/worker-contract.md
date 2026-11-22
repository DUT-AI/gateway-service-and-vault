# Worker Task Contract (Redis + ARQ)

## Location
- Worker Definition: `apps/worker/main.py`
- Enqueue Helper: Injected ARQ Redis pool client

## Task Signatures

### 1. `send_welcome_email`
Enqueued upon successful user registration.

```python
async def send_welcome_email(ctx: dict, user_id: int, email: str) -> bool:
    """Send welcome email to newly registered user."""
    ...
```

**Parameters**:
- `user_id` (`int`): Target user's primary key identifier.
- `email` (`str`): Target email destination.

**Return**: `bool` indicating delivery success.

---

### 2. `process_outbox_events`
Scheduled recurring cron task or triggered job to deliver pending domain events.

```python
async def process_outbox_events(ctx: dict, batch_size: int = 50) -> int:
    """Read pending events from outbox_events table, publish to listeners, and mark as PROCESSED."""
    ...
```

**Parameters**:
- `batch_size` (`int`): Maximum number of pending events processed per batch.

**Return**: `int` count of processed events.

---

## ARQ Worker Configuration (`apps/worker/main.py`)

```python
from arq.connections import RedisSettings
from core.config import redis_settings

class WorkerSettings:
    functions = [send_welcome_email, process_outbox_events]
    redis_settings = RedisSettings.from_dsn(redis_settings.redis_url)
    max_jobs = 10
    job_timeout = 300
```

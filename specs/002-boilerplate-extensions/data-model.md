# Phase 1 Data Model: Boilerplate Advanced Capabilities

## 1. Pagination Schemas (`core/pagination/`)

### `PaginationParams`
```python
from pydantic import BaseModel, Field

class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number starting at 1")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page (max 100)")
    search: str | None = Field(default=None, max_length=100, description="Optional search term")
```

### `PaginatedResponse[T]`
```python
from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int
```

---

## 2. Outbox Processor Entities (`core/events/`)

### `OutboxEventModel` Statuses
- `PENDING`: Newly created event awaiting dispatch.
- `PROCESSED`: Successfully delivered to all registered handlers.
- `FAILED`: Execution failed after retries; stores `error_message`.

---

## 3. Frontend Authentication Types (`web/src/features/auth/types/index.ts`)

```typescript
export interface User {
  id: number;
  email: string;
  name: string | null;
  role: string;
  avatar_url: string | null;
  status: string;
  created_at: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  email: string;
  password: string;
  name?: string;
}

export interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  login: (data: LoginPayload) => Promise<void>;
  register: (data: RegisterPayload) => Promise<void>;
  logout: () => Promise<void>;
  refetchUser: () => void;
}
```

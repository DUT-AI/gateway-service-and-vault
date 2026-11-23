# Data Model: Gateway Quota & Rate Limiting (Phase 2)

## Entities & Schemas

### 1. Existing Relational Model (`quota_policies` table)
Defined in `modules/gateway/models/quota.py` and `modules/gateway/domain/entities.py`:
- `id`: ULID string (26 chars)
- `project_id`: FK `projects.id`
- `service_id`: FK `upstream_services.id`
- `client_id`: FK `registered_clients.id` (nullable)
- `rate_limit_rpm`: Integer (requests per minute, default 60)
- `quota_daily`: Integer (requests per day, default 10,000)
- `is_active`: Boolean

---

### 2. Redis Key Schema for Real-Time Usage
- **Key Pattern**: `gateway:quota:{project_id}:{service_id}:{YYYYMMDD}`
- **Value**: Integer (string representation of count)
- **TTL**: 172,800 seconds (48 hours)
- **Operations**:
  - `INCR key`: Increment by 1 upon successful verification.
  - `EXPIRE key 172800`: Set TTL on first increment (`if current == 1`).
  - `GET key`: Query current usage (returns `0` if key does not exist).

---

### 3. Data Transfer Objects (DTOs)

#### `QuotaUsageResponse`
```python
class QuotaUsageResponse(BaseModel):
    project_id: str
    service_id: str
    usage_today: int
    quota_daily: int
    rate_limit_rpm: int
    usage_percentage: float
    is_exhausted: bool
```

#### Updated `ProjectAllowedServiceResponse`
```python
class ProjectAllowedServiceResponse(BaseModel):
    service_id: str
    service_name: str
    service_slug: str
    base_url: str
    auth_type: str
    is_service_active: bool
    rate_limit_rpm: int
    quota_daily: int
    is_quota_active: bool
    usage_today: int = 0
    usage_percentage: float = 0.0
    bound_at: datetime | None = None
```

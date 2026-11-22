# =============================================================================
# Multi-stage Dockerfile for Background Task Worker & Outbox Processor
# Context: Root workspace directory (.)
# =============================================================================

# --- Stage 1: Build virtual environment with uv ---
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Install dependencies using uv
COPY pyproject.toml uv.lock* README.md* ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project || uv sync --no-dev --no-install-project

# --- Stage 2: Final Minimal Runtime Image ---
FROM python:3.12-slim-bookworm AS runner

WORKDIR /app

ENV TZ=Asia/Ho_Chi_Minh \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="/app" \
    PATH="/app/.venv/bin:$PATH"

# Create unprivileged system user for security
RUN groupadd --system --gid 1001 appuser && \
    useradd --system --uid 1001 --gid appuser --no-create-home appuser

# Copy virtual environment from builder
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Copy source code needed for background workers
COPY --chown=appuser:appuser core ./core
COPY --chown=appuser:appuser modules ./modules
COPY --chown=appuser:appuser apps ./apps

USER appuser

CMD ["python", "-m", "apps.worker.main"]

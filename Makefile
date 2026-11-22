.PHONY: help dev-api dev-web dev-worker docker-up docker-down migrate create-migration test install-hooks lint ruff check api-types

help:
	@echo "Available commands:"
	@echo "  make dev-api        - Start local FastAPI server (uvicorn)"
	@echo "  make dev-web        - Start frontend dev server (Next.js)"
	@echo "  make dev-worker     - Start background task worker (ARQ)"
	@echo "  make docker-up      - Start backing services (PostgreSQL, Redis, MinIO)"
	@echo "  make docker-down    - Stop and remove Docker Compose containers"
	@echo "  make migrate        - Run database migrations (alembic upgrade head)"
	@echo "  make create-migration DESC=\"msg\" - Create a new migration revision"
	@echo "  make test           - Run backend test suite"
	@echo "  make ruff           - Format and fix python code with ruff"
	@echo "  make check          - Run static type checking (mypy)"
	@echo "  make api-types      - Regenerate web API types from backend DTOs (offline)"
	@echo "  make install-hooks  - Install git pre-commit hooks"
	@echo "  make lint           - Run all formatting, linting, and tests"

dev-api:
	uv run uvicorn apps.api.main:app --host 0.0.0.0 --port 8000 --reload

dev-web:
	cd ./web && pnpm dev

dev-worker:
	uv run python -m apps.worker.main

docker-up:
	docker compose up -d

docker-down:
	docker compose down

migrate:
	uv run alembic upgrade head

create-migration:
	@if [ -z "$(DESC)" ]; then echo "Error: Please specify DESC, e.g., make create-migration DESC=\"add new table\""; exit 1; fi
	uv run alembic revision --autogenerate -m "$(DESC)"

test:
	uv run pytest tests/

ruff:
	uv run ruff format .
	uv run ruff check --fix .

check:
	uv run mypy core modules apps

api-types:
	cd ./web && pnpm run sync:api

install-hooks:
	mkdir -p .git/hooks
	cp .githooks/pre-commit .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit
	@echo "Git pre-commit hooks installed successfully!"

lint:
	./.githooks/pre-commit

.PHONY: help dev-api dev-web dev-worker docker-up docker-down migrate create-migration test test-e2e install-hooks lint ruff check api-types publish-sdk

help:
	@echo "Available commands:"
	@echo "  make dev-api        - Start local FastAPI server (uvicorn)"
	@echo "  make dev-web        - Start frontend dev server (Next.js)"
	@echo "  make dev-worker     - Start background task worker (ARQ)"
	@echo "  make docker-up      - Start Docker Compose stack"
	@echo "  make docker-down    - Stop and remove Docker Compose containers"
	@echo "  make migrate        - Run database migrations (alembic upgrade head)"
	@echo "  make create-migration DESC=\"msg\" - Create a new migration revision"
	@echo "  make test           - Run backend test suite"
	@echo "  make test-e2e       - Run live gateway mTLS E2E tests against APISIX"
	@echo "  make ruff           - Format and fix python code with ruff"
	@echo "  make check          - Run static type checking (mypy)"
	@echo "  make api-types      - Regenerate web API types from backend DTOs (offline)"
	@echo "  make publish-sdk    - Build and publish dut-vault-sdk to PyPI (uses PYPI_TOKEN from .env)"
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

test-e2e:
	uv run pytest tests/integration/test_gateway_live_e2e.py -v

ruff:
	uv run ruff format .
	uv run ruff check --fix .

check:
	uv run mypy core modules apps

api-types:
	cd ./web && pnpm run sync:api

publish-sdk:
	@set -a && [ -f .env ] && . ./.env && set +a && \
	if [ -z "$$UV_PUBLISH_TOKEN" ] && [ -z "$$PYPI_TOKEN" ]; then \
		echo "Error: PYPI_TOKEN or UV_PUBLISH_TOKEN is not set in .env or environment"; exit 1; \
	fi; \
	export UV_PUBLISH_TOKEN="$${UV_PUBLISH_TOKEN:-$$PYPI_TOKEN}"; \
	cd packages/dut-vault-sdk && rm -rf dist && uv build && uv publish

install-hooks:
	mkdir -p .git/hooks
	cp .githooks/pre-commit .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit
	@echo "Git pre-commit hooks installed successfully!"

lint:
	./.githooks/pre-commit

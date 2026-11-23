import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.api.di import setup_di
from apps.api.routers.auth_router import router as auth_router
from apps.api.routers.gateway_router import router as gateway_router
from apps.api.routers.health_router import router as health_router
from apps.api.routers.user_router import router as user_router
from apps.api.routers.vault_router import router as vault_router
from core.config import settings
from core.exceptions import setup_exception_handlers

logger = logging.getLogger("apisix_sync")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager that synchronizes routes to APISIX on startup."""
    try:
        from core.database.session import AsyncSessionLocal
        from modules.gateway.client.apisix_client import ApisixAdminClient
        from modules.gateway.repository.gateway_repository import (
            SqlUpstreamServiceRepository,
        )

        client = ApisixAdminClient()
        # 1. Sync unified control plane backend route (/api/*)
        await client.sync_control_plane_route()

        # 2. Sync all active upstream services (/services/{slug}/*)
        async with AsyncSessionLocal() as session:
            repo = SqlUpstreamServiceRepository(session)
            services = await repo.list_all()
            for s in services:
                if s.is_active:
                    await client.sync_upstream_service_route(
                        service_slug=s.slug,
                        upstream_base_url=s.base_url,
                        upstream_auth_type=s.auth_type,
                        upstream_credential=s.encrypted_credential,
                    )
        logger.info(
            "Successfully synchronized APISIX routes for unified gateway entrypoint."
        )
    except Exception as e:
        logger.warning("Could not synchronize APISIX routes on startup: %s", e)

    yield


app = FastAPI(
    title="Modular Monolith Backend API",
    description="Scalable Modular Monolith Backend with Clean Architecture & Dishka DI",
    version="0.1.0",
    lifespan=lifespan,
)

# 1. Setup global exception handlers
setup_exception_handlers(app)

# 2. Setup Dishka Dependency Injection Container
setup_di(app)


class AppCORSMiddleware(CORSMiddleware):
    """Enhanced CORS Middleware supporting local development ports."""

    def is_allowed_origin(self, origin: str) -> bool:
        if super().is_allowed_origin(origin):
            return True
        return origin.startswith(
            ("http://localhost:", "http://127.0.0.1:", "http://[::1]:")
        ) or origin in ("http://localhost", "http://127.0.0.1", "http://[::1]")


# 3. Configure CORS
app.add_middleware(
    AppCORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Include Routers
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(gateway_router)
app.include_router(vault_router)

if __name__ == "__main__":
    uvicorn.run(
        "apps.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )

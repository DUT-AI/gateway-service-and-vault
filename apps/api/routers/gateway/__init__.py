from fastapi import APIRouter

from apps.api.routers.gateway.audit import router as audit_router
from apps.api.routers.gateway.clients import router as clients_router
from apps.api.routers.gateway.keys import router as keys_router
from apps.api.routers.gateway.projects import router as projects_router
from apps.api.routers.gateway.services import router as services_router

router = APIRouter(prefix="/api/v1/gateway", tags=["Gateway"])
router.include_router(projects_router)
router.include_router(clients_router)
router.include_router(keys_router)
router.include_router(services_router)
router.include_router(audit_router)

__all__ = ["router"]

from fastapi import APIRouter

from apps.api.routers.vault.permissions import router as permissions_router
from apps.api.routers.vault.secrets import router as secrets_router
from apps.api.routers.vault.stream import router as stream_router

router = APIRouter(prefix="/api/v1/vault", tags=["Vault"])
router.include_router(secrets_router)
router.include_router(permissions_router)
router.include_router(stream_router)

__all__ = ["router"]

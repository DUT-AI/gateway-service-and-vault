import httpx
from fastapi import HTTPException, status
from loguru import logger

from core.config.auth import auth_settings
from modules.identity.dtos.auth_dtos import SsoLoginDataDTO, SsoUserDataDTO


class DutAiSsoService:
    """External service client for DUT-AI SSO (Manage IdP)."""

    def __init__(self) -> None:
        self.base_url = auth_settings.sso_dutai_base_url.rstrip("/")
        self.timeout = auth_settings.sso_timeout

    @property
    def auth_url(self) -> str:
        return f"{self.base_url}/api/v1/auth/login"

    @property
    def me_url(self) -> str:
        return f"{self.base_url}/api/v1/auth/me"

    async def login(self, email: str, password: str) -> SsoLoginDataDTO:
        """Authenticate user against DUT-AI SSO IdP with credentials.

        Returns strongly-typed SsoLoginDataDTO model.
        """
        payload = {"email": email, "password": password}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(self.auth_url, json=payload)
        except httpx.ConnectError as exc:
            logger.error(f"[SSO] Cannot connect to IdP at {self.auth_url}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Không thể kết nối tới máy chủ SSO DUT-AI. Vui lòng kiểm tra lại mạng.",
            ) from exc
        except httpx.TimeoutException as exc:
            logger.error(f"[SSO] Timeout connecting to IdP at {self.auth_url}")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Máy chủ SSO DUT-AI phản hồi quá lâu. Vui lòng thử lại sau.",
            ) from exc

        if res.status_code in (400, 401, 422):
            err_body = res.json() if res.content else {}
            msg = err_body.get("message") or "Email hoặc mật khẩu SSO không chính xác."
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=msg,
            )

        res.raise_for_status()
        body = res.json()
        if not body.get("is_success") or "data" not in body or not body["data"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=body.get("message", "Đăng nhập SSO không thành công"),
            )

        return SsoLoginDataDTO.model_validate(body["data"])

    async def get_current_user(self, token: str) -> SsoUserDataDTO | None:
        """Fetch verified user profile from DUT-AI SSO IdP /api/v1/auth/me."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.get(
                    self.me_url,
                    headers={"Authorization": f"Bearer {token}"},
                )
                if res.status_code == 200:
                    body = res.json()
                    if body.get("is_success") and "data" in body and body["data"]:
                        return SsoUserDataDTO.model_validate(body["data"])
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            logger.warning(f"[SSO] Failed to verify token with SSO IdP: {exc}")
            return None

        return None


# Global default SSO service instance
sso_dutai_service = DutAiSsoService()

import httpx
from fastapi import HTTPException, status
from loguru import logger

from core.config.auth import auth_settings
from modules.identity.domain.entities import (
    ExternalUserDetailEntity,
    ExternalUserOptionEntity,
)


class ExternalUserDirectoryService:
    """Service client delegating user directory queries to DUT-AI Manage IdP."""

    def __init__(self, base_url: str | None = None, timeout: float = 10.0) -> None:
        self.base_url = (base_url or auth_settings.sso_dutai_base_url).rstrip("/")
        self.timeout = timeout

    def _build_headers(self, auth_token: str | None) -> dict[str, str]:
        headers: dict[str, str] = {"Accept": "application/json"}
        if auth_token:
            headers["Authorization"] = (
                f"Bearer {auth_token}"
                if not auth_token.startswith("Bearer ")
                else auth_token
            )
            headers["Cookie"] = f"access_token={auth_token}"
        return headers

    async def get_user_options(
        self, auth_token: str | None = None
    ) -> list[ExternalUserOptionEntity]:
        """Fetch all user options from central directory (GET /api/v1/users/options)."""
        url = f"{self.base_url}/api/v1/users/options"
        headers = self._build_headers(auth_token)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.get(url, headers=headers)
        except httpx.ConnectError as exc:
            logger.error(f"[ExternalUserDirectory] ConnectError to {url}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Không thể kết nối tới dịch vụ người dùng DUT-AI.",
            ) from exc
        except httpx.TimeoutException as exc:
            logger.error(f"[ExternalUserDirectory] Timeout to {url}")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Dịch vụ người dùng DUT-AI phản hồi quá lâu.",
            ) from exc

        if res.status_code == 401:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Xác thực SSO không hợp lệ hoặc đã hết hạn.",
            )

        res.raise_for_status()
        body = res.json()
        raw_items = body.get("data", [])

        result: list[ExternalUserOptionEntity] = []
        for item in raw_items:
            # Enforce native integer ID directly from payload
            user_id = item.get("id")
            if not isinstance(user_id, int):
                continue
            result.append(
                ExternalUserOptionEntity(
                    id=user_id,
                    name=item.get("name", ""),
                    email=item.get("email", ""),
                    avatar_url=item.get("avatar_url"),
                )
            )
        return result

    async def get_user_by_id(
        self, user_id: int, auth_token: str | None = None
    ) -> ExternalUserDetailEntity | None:
        """Fetch user details by integer ID from central directory (GET /api/v1/users/{id})."""
        url = f"{self.base_url}/api/v1/users/{user_id}"
        headers = self._build_headers(auth_token)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.get(url, headers=headers)
        except httpx.ConnectError as exc:
            logger.error(f"[ExternalUserDirectory] ConnectError to {url}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Không thể kết nối tới dịch vụ người dùng DUT-AI.",
            ) from exc
        except httpx.TimeoutException as exc:
            logger.error(f"[ExternalUserDirectory] Timeout to {url}")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Dịch vụ người dùng DUT-AI phản hồi quá lâu.",
            ) from exc

        if res.status_code == 404:
            return None

        if res.status_code == 401:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Xác thực SSO không hợp lệ hoặc đã hết hạn.",
            )

        res.raise_for_status()
        body = res.json()
        data = body.get("data")
        if not data:
            return None

        raw_id = data.get("id")
        resolved_id = raw_id if isinstance(raw_id, int) else int(raw_id)

        return ExternalUserDetailEntity(
            id=resolved_id,
            name=data.get("name", ""),
            email=data.get("email", ""),
            status=data.get("status", "ACTIVE"),
            phone_number=data.get("phone_number"),
            role_ids=data.get("role_ids", []),
            role_names=data.get("role_names", []),
            permissions=data.get("permissions", []),
            avatar_url=data.get("avatar_url"),
            discord_id=data.get("discord_id"),
            zalo_bot_id=data.get("zalo_bot_id"),
            check_in_card_code_configured=data.get(
                "check_in_card_code_configured", False
            ),
        )

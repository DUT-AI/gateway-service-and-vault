import json
from dataclasses import asdict

import httpx
import redis.asyncio as aioredis
from fastapi import HTTPException, status
from loguru import logger

from core.config import redis_settings
from core.config.auth import auth_settings
from modules.identity.domain.entities import (
    ExternalUserDetailEntity,
    ExternalUserOptionEntity,
)


class ExternalUserDirectoryService:
    """Service client delegating user directory queries to DUT-AI Manage IdP with Redis caching."""

    CACHE_KEY_OPTIONS = "identity:users:options"
    CACHE_KEY_USER_PREFIX = "identity:users:detail:"
    CACHE_TTL_SECONDS = 300  # 5 minutes TTL

    def __init__(self, redis_client: aioredis.Redis | None = None) -> None:
        self.base_url = auth_settings.sso_dutai_base_url.rstrip("/")
        self.timeout = 10.0  # 10 seconds
        self._redis = redis_client

    @property
    def redis(self) -> aioredis.Redis:
        if self._redis is None:
            self._redis = redis_settings.get_async_client()
        return self._redis

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
        """Fetch all user options from central directory (GET /api/v1/users/options) with Redis caching."""
        # 1. Attempt to read from Redis cache
        try:
            cached_data = await self.redis.get(self.CACHE_KEY_OPTIONS)
            if cached_data:
                logger.debug("[ExternalUserDirectory] Cache HIT for user options")
                raw_list = json.loads(cached_data)
                return [
                    ExternalUserOptionEntity(
                        id=item["id"],
                        name=item.get("name", ""),
                        email=item.get("email", ""),
                        avatar_url=item.get("avatar_url"),
                    )
                    for item in raw_list
                ]
        except Exception as exc:
            logger.warning(
                f"[ExternalUserDirectory] Redis read failed (fail-open): {exc}"
            )

        # 2. Fetch from remote IdP
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

        # 3. Cache results in Redis (fail-open)
        try:
            serialized = json.dumps([asdict(item) for item in result])
            await self.redis.set(
                self.CACHE_KEY_OPTIONS, serialized, ex=self.CACHE_TTL_SECONDS
            )
            logger.debug(
                f"[ExternalUserDirectory] Cached {len(result)} user options in Redis"
            )
        except Exception as exc:
            logger.warning(
                f"[ExternalUserDirectory] Redis write failed (fail-open): {exc}"
            )

        return result

    async def get_user_by_id(
        self, user_id: int, auth_token: str | None = None
    ) -> ExternalUserDetailEntity | None:
        """Fetch user details by integer ID from central directory with Redis caching."""
        cache_key = f"{self.CACHE_KEY_USER_PREFIX}{user_id}"

        # 1. Attempt to read from Redis cache
        try:
            cached_data = await self.redis.get(cache_key)
            if cached_data:
                logger.debug(f"[ExternalUserDirectory] Cache HIT for user {user_id}")
                data = json.loads(cached_data)
                return ExternalUserDetailEntity(**data)
        except Exception as exc:
            logger.warning(
                f"[ExternalUserDirectory] Redis read failed (fail-open): {exc}"
            )

        # 2. Fetch from remote IdP
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

        user_entity = ExternalUserDetailEntity(
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

        # 3. Cache user profile in Redis (fail-open)
        try:
            serialized = json.dumps(asdict(user_entity))
            await self.redis.set(cache_key, serialized, ex=self.CACHE_TTL_SECONDS)
            logger.debug(f"[ExternalUserDirectory] Cached user {user_id} in Redis")
        except Exception as exc:
            logger.warning(
                f"[ExternalUserDirectory] Redis write failed (fail-open): {exc}"
            )

        return user_entity

    async def invalidate_cache(self, user_id: int | None = None) -> None:
        """Invalidate user cache in Redis. If user_id is provided, invalidates specific user and options."""
        try:
            keys_to_delete: list[str] = [self.CACHE_KEY_OPTIONS]
            if user_id is not None:
                keys_to_delete.append(f"{self.CACHE_KEY_USER_PREFIX}{user_id}")
            else:
                async for key in self.redis.scan_iter(
                    match=f"{self.CACHE_KEY_USER_PREFIX}*"
                ):
                    keys_to_delete.append(key)

            if keys_to_delete:
                await self.redis.delete(*keys_to_delete)
                logger.info(
                    f"[ExternalUserDirectory] Invalidated Redis cache keys: {keys_to_delete}"
                )
        except Exception as exc:
            logger.warning(
                f"[ExternalUserDirectory] Failed to invalidate Redis cache: {exc}"
            )

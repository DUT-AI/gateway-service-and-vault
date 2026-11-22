from unittest.mock import AsyncMock

import pytest

from modules.identity.domain.entities import ExternalUserDetailEntity
from modules.identity.use_cases import GetUserDetailUseCase, UserNotFoundError


@pytest.mark.asyncio
async def test_get_user_detail_use_case_success():
    directory_mock = AsyncMock()
    expected_user = ExternalUserDetailEntity(
        id=1,
        name="Huynh Phuoc Nguyen",
        email="huynhphuocnguyen.dev@gmail.com",
        status="ACTIVE",
        role_ids=[1, 9],
        role_names=["admin", "Trainer"],
        permissions=["billing:read"],
        avatar_url="https://avatar.url/1.jpg",
    )
    directory_mock.get_user_by_id.return_value = expected_user

    use_case = GetUserDetailUseCase(directory_service=directory_mock)
    result = await use_case.execute(user_id=1, auth_token="sample_token")

    assert isinstance(result.id, int)
    assert result.id == 1
    assert result.email == "huynhphuocnguyen.dev@gmail.com"
    directory_mock.get_user_by_id.assert_awaited_once_with(
        user_id=1, auth_token="sample_token"
    )


@pytest.mark.asyncio
async def test_get_user_detail_use_case_not_found():
    directory_mock = AsyncMock()
    directory_mock.get_user_by_id.return_value = None

    use_case = GetUserDetailUseCase(directory_service=directory_mock)
    with pytest.raises(UserNotFoundError):
        await use_case.execute(user_id=999999, auth_token="sample_token")

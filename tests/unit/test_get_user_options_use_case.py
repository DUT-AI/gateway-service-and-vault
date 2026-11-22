from unittest.mock import AsyncMock

import pytest

from modules.identity.domain.entities import ExternalUserOptionEntity
from modules.identity.use_cases import GetUserOptionsUseCase


@pytest.mark.asyncio
async def test_get_user_options_use_case():
    directory_mock = AsyncMock()
    expected_options = [
        ExternalUserOptionEntity(
            id=3,
            name="Alice Pham",
            email="alice@example.com",
            avatar_url="https://avatar.url/alice.jpg",
        ),
        ExternalUserOptionEntity(
            id=4,
            name="Bob Ngo",
            email="bob@example.com",
            avatar_url=None,
        ),
    ]
    directory_mock.get_user_options.return_value = expected_options

    use_case = GetUserOptionsUseCase(directory_service=directory_mock)
    result = await use_case.execute(auth_token="sample_token")

    assert len(result) == 2
    assert isinstance(result[0].id, int)
    assert result[0].id == 3
    assert result[1].id == 4
    directory_mock.get_user_options.assert_awaited_once_with(auth_token="sample_token")

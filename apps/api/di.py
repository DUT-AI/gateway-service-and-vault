from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from core.database.session import DatabaseProvider
from core.storage.di import StorageProvider
from modules.identity.di import IdentityProvider


def create_container() -> AsyncContainer:
    """Instantiate and configure Dishka Dependency Injection Container."""
    return make_async_container(
        DatabaseProvider(),
        StorageProvider(),
        IdentityProvider(),
    )


def setup_di(app: FastAPI) -> None:
    """Bind Dishka DI container to FastAPI application instance."""
    container = create_container()
    setup_dishka(container, app)

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent.parent


class AuthSettings(BaseSettings):
    """Authentication and JWT Configuration."""

    model_config = SettingsConfigDict(
        env_file=(ROOT_DIR / ".env",),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    jwt_secret_key: str = "supersecretjwtkeychangemeinproduction32char"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

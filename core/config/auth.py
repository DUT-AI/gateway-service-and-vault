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

    # DUT-AI SSO IdP Configuration
    sso_dutai_base_url: str = "https://manage.dutai.io.vn"
    sso_timeout: float = 10.0

    @property
    def sso_auth_url(self) -> str:
        return f"{self.sso_dutai_base_url.rstrip('/')}/api/v1/auth/login"

    @property
    def sso_me_url(self) -> str:
        return f"{self.sso_dutai_base_url.rstrip('/')}/api/v1/auth/me"


auth_settings = AuthSettings()

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent.parent


class ApisixSettings(BaseSettings):
    """Apache APISIX Gateway Configuration."""

    model_config = SettingsConfigDict(
        env_file=(ROOT_DIR / ".env",),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    apisix_admin_url: str = "http://localhost:9180"
    apisix_admin_key: str = "edd1c9f034335f136f87ad84b625c8f1"
    apisix_gateway_url: str = "http://localhost:9080"
    apisix_gateway_ssl_url: str = "https://localhost:9443"

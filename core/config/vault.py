from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent.parent


class VaultSettings(BaseSettings):
    """Centralized Dynamic Vault Configuration."""

    model_config = SettingsConfigDict(
        env_file=(ROOT_DIR / ".env",),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Master encryption key (256-bit)
    vault_master_key: str = "default-master-key-must-be-changed-in-production-32b"

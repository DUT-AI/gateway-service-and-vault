from core.config.apisix import ApisixSettings
from core.config.app import AppSettings
from core.config.auth import AuthSettings
from core.config.database import DatabaseSettings
from core.config.redis import RedisSettings
from core.config.vault import VaultSettings

settings = AppSettings()
app_settings = settings
db_settings = DatabaseSettings()
redis_settings = RedisSettings()
auth_settings = AuthSettings()
apisix_settings = ApisixSettings()
vault_settings = VaultSettings()

__all__ = [
    "ApisixSettings",
    "AppSettings",
    "AuthSettings",
    "DatabaseSettings",
    "RedisSettings",
    "VaultSettings",
    "apisix_settings",
    "app_settings",
    "auth_settings",
    "db_settings",
    "redis_settings",
    "settings",
    "vault_settings",
]

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Tuple
import toml

import platform
import sys

def get_app_version() -> str:
    with open("pyproject.toml", "r") as f:
        pyproject_data = toml.load(f)
    return pyproject_data["tool"]["bumpversion"]["current_version"]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    API_ID: int
    API_HASH: str
    APP_NAME: str = 'pyTelegramDialogsMirror'
    CHANNEL_MAPPINGS_STR: str  # This will be loaded from .env

    # Performance settings
    SEND_DELAY: float = 0.8
    BATCH_SIZE: int = 150
    MAX_CACHE_SIZE: int = 200

    # Retry and error handling settings
    SKIP_SERVICE_MESSAGES: bool = True
    MAX_RETRIES: int = 5
    BACKOFF_FACTOR: float = 1.0

    # TelegramClient specific settings
    REQUEST_RETRIES: int = 9
    CONNECTION_RETRIES: int = 9
    RETRY_DELAY: int = 36
    AUTO_RECONNECT: bool = True
    DEVICE_MODEL: str = "pyTelegramDialogsMirror"
    SYSTEM_VERSION: str = f"Python {sys.version.split()[0]} on {platform.system()} {platform.release()}"
    APP_VERSION: str = get_app_version()
    LANG_CODE: str = 'ru'
    RECEIVE_UPDATES: bool = True
    LOG_TELETHON_DIFFERENCES: bool = True

    @property
    def CHANNEL_MAPPINGS(self) -> List[Tuple[int, int]]:
        mappings = []
        for pair_str in self.CHANNEL_MAPPINGS_STR.split(';'):
            if pair_str.strip():
                source, target = map(int, pair_str.split(','))
                mappings.append((source, target))
        return mappings

    @property
    def SESSION_NAME(self):
        return f"sessions/{self.APP_NAME}"

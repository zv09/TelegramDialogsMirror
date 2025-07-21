#!/usr/bin/env python3
"""
This module handles the creation and configuration of the Telegram client.
"""

from telethon import TelegramClient
from config.config import Settings

def create_telegram_client(settings: Settings) -> TelegramClient:
    """Creates, configures, and returns a Telegram client instance."""
    client = TelegramClient(
        settings.SESSION_NAME,
        settings.API_ID,
        settings.API_HASH
    )

    # Explicitly set the session parameters to ensure they are used.
    # This is more reliable than relying on the constructor for session info.
    client.session.set_parameters(
        device_model=settings.DEVICE_MODEL,
        system_version=settings.SYSTEM_VERSION,
        app_version=settings.APP_VERSION,
        lang_code=settings.LANG_CODE,
        system_lang_code=settings.LANG_CODE,
    )

    return client

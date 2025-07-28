#!/usr/bin/env python3
"""
This module handles the creation and configuration of the Telegram client.
"""

from telethon import TelegramClient
from config.config import Settings

def create_telegram_client(session_name: str, settings: Settings) -> TelegramClient:
    """Creates, configures, and returns a Telegram client instance."""
    client = TelegramClient(
        session_name,
        settings.API_ID,
        settings.API_HASH,
        device_model=settings.DEVICE_MODEL,
        system_version=settings.SYSTEM_VERSION,
        app_version=settings.APP_VERSION,
        lang_code=settings.LANG_CODE
    )
    return client

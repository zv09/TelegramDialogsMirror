#!/usr/bin/env python3
"""
This module provides utility functions, including robust error handling for Telegram API calls.
"""

import asyncio
import random
from functools import wraps
from telethon.errors import FloodWaitError, RPCError
from loguru import logger

from config.config import Settings


def retry_on_telegram_error():
    """A decorator to handle common Telegram API errors with exponential backoff and jitter.

    Catches FloodWaitError and waits for the specified time. For other common
    RPC errors, it retries with an exponential backoff.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            settings = Settings()
            last_exception = None
            for attempt in range(settings.MAX_RETRIES):
                try:
                    return await func(*args, **kwargs)
                except FloodWaitError as e:
                    logger.warning(f"Flood wait error for {func.__name__}: waiting for {e.seconds} seconds.")
                    await asyncio.sleep(e.seconds)
                    last_exception = e
                except (ConnectionError, TimeoutError, RPCError) as e:
                    wait_time = settings.BACKOFF_FACTOR * (2 ** attempt) + random.uniform(0, 1)
                    logger.warning(f"Attempt {attempt + 1}/{settings.MAX_RETRIES} for {func.__name__} failed with {type(e).__name__}. Retrying in {wait_time:.2f}s.")
                    await asyncio.sleep(wait_time)
                    last_exception = e
            
            logger.error(f"Function {func.__name__} failed after {settings.MAX_RETRIES} retries.")
            raise last_exception
        return wrapper
    return decorator

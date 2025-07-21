#!/usr/bin/env python3
"""
This module contains the main application launcher class.
"""

import asyncio
import signal
from loguru import logger

from app.arguments import parse_args
from config.config import Settings
from app.forwarder import Forwarder
from app.synchronizer import MessageSynchronizer
from app.cache import CacheManager

class Launcher:
    """Orchestrates the application startup and execution flow."""

    def __init__(self):
        self.args = parse_args()
        self.settings = Settings()
        self.cache_manager = CacheManager()
        self.forwarder = Forwarder(self.settings, self.cache_manager)
        self.synchronizer = MessageSynchronizer(self.forwarder.client, self.cache_manager, self.forwarder)
        self.shutdown_event = asyncio.Event()

    def _setup_signal_handlers(self):
        """Sets up graceful shutdown handlers for SIGINT and SIGTERM."""
        def signal_handler():
            logger.info("Shutdown signal received. Initiating graceful shutdown...")
            self.shutdown_event.set()

        signal.signal(signal.SIGINT, lambda s, f: signal_handler())
        signal.signal(signal.SIGTERM, lambda s, f: signal_handler())

    async def run(self):
        """The main execution method for the application."""
        self._setup_signal_handlers()

        if self.args.copy:
            logger.info("Starting in Synchronization mode (--copy).")
        else:
            logger.info("Starting in Live Forwarding mode.")

        logger.info("Application starting...")

        try:
            if self.args.copy:
                await self.forwarder.client.start()
                for source, target in self.settings.CHANNEL_MAPPINGS:
                    if self.shutdown_event.is_set():
                        break
                    await self.synchronizer.synchronize(source, target, self.shutdown_event)
                logger.info("Message synchronization complete.")
            else:
                await self.forwarder.run(self.shutdown_event, self.synchronizer)
        except asyncio.CancelledError:
            logger.info("Application shutdown forcefully.")
        finally:
            if self.forwarder.client.is_connected():
                await self.forwarder.client.disconnect()
                logger.info("Telegram client disconnected.")
            logger.info("Application has shut down.")

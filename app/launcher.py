#!/usr/bin/env python3
"""
This module contains the main application launcher class.
"""

import asyncio
import signal
import sys
from loguru import logger
from pydantic import ValidationError

from app.arguments import parse_args
from config.config import Settings
from app.client import create_telegram_client
from app.forwarder import Forwarder
from app.synchronizer import MessageSynchronizer
from app.cache import CacheManager
from app.session_manager import SessionManager
from app.stats import stats_manager

class Launcher:
    """Orchestrates the application startup, execution flow, and shutdown."""

    def __init__(self):
        self.args = parse_args()
        try:
            self.settings = Settings()
        except ValidationError as e:
            logger.critical("Configuration Error: A required setting is missing or invalid.")
            logger.error("Please ensure your .env file is correctly set up.")
            logger.error(f"Details: {e}")
            sys.exit(1)
            
        self.cache_manager = CacheManager()
        session_manager = SessionManager(self.args.session, self.settings.APP_NAME)
        session_name = session_manager.get_session_name()
        self.client = create_telegram_client(session_name, self.settings)
        self.forwarder = Forwarder(self.client, self.settings, self.cache_manager, stats_manager)
        self.synchronizer = MessageSynchronizer(self.client, self.cache_manager, self.forwarder, stats_manager)
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
            if self.args.dry_run:
                logger.info("Starting in Synchronization Dry Run mode (--copy --dry-run).")
            else:
                logger.info("Starting in Synchronization mode (--copy).")
        else:
            logger.info("Starting in Live Forwarding mode.")

        try:
            if self.args.copy:
                try:
                    await self.client.start()
                    for source, target in self.settings.CHANNEL_MAPPINGS:
                        if self.shutdown_event.is_set():
                            break
                        
                        analysis = await self.synchronizer.analyze_synchronization(source, target)
                        
                        logger.info("\nSynchronization Plan:")
                        logger.info("---------------------------------")
                        logger.info(f"Source: '{analysis['source_title']}' ({source}) - {analysis['source_total']} messages")
                        logger.info(f"Target: '{analysis['target_title']}' ({target}) - {analysis['target_total']} messages")
                        logger.info("---------------------------------")
                        logger.info(f"Messages to copy:   {analysis['to_copy']}")
                        logger.info(f"Messages to delete: {analysis['to_delete']}")
                        
                        if analysis['to_copy'] > 0:
                            estimated_time = (analysis['to_copy'] * self.settings.SEND_DELAY) / 60
                            logger.info(f"Estimated time:     ~{estimated_time:.1f} minutes")

                        if self.args.dry_run:
                            logger.info("\nDry run complete. No changes were made.")
                            continue

                        if input("\nProceed with synchronization? [y/N]: ").lower() not in ['y', 'yes']:
                            logger.warning("Synchronization aborted by user.")
                            continue

                        await self.synchronizer.synchronize(source, target, self.shutdown_event)
                    logger.info("Message synchronization complete.")
                finally:
                    if self.client.is_connected():
                        await self.client.disconnect()
            else:
                await self.forwarder.run(self.shutdown_event, self.synchronizer)
        except (ValueError, TypeError) as e:
            logger.critical(f"Configuration error: {e}")
        except asyncio.CancelledError:
            logger.info("Application shutdown forcefully.")
        finally:
            if self.forwarder.client.is_connected():
                await self.forwarder.client.disconnect()
                logger.info("Telegram client disconnected.")
            stats_manager.log_summary()
            logger.info("Application has shut down.")

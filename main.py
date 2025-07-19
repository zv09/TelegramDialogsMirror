import asyncio
import signal
import argparse
from loguru import logger

from config.config import Settings
from app.forwarder import Forwarder
from app.synchronizer import MessageSynchronizer
from app.cache import CacheManager
from config.logger import setup_logging

async def main():
    """The main entry point of the application."""
    parser = argparse.ArgumentParser(description="Telegram Resender Bot")
    parser.add_argument("-c", "--copy", action="store_true", help="Check and copy missing messages from source to target channels.")
    args = parser.parse_args()

    settings = Settings()
    setup_logging(settings)

    if args.copy:
        logger.info("Starting in Synchronization mode (--copy).")
    else:
        logger.info("Starting in Live Forwarding mode.")

    logger.info("Application starting...")

    shutdown_event = asyncio.Event()

    def signal_handler():
        logger.info("Shutdown signal received. Initiating graceful shutdown...")
        shutdown_event.set()

    signal.signal(signal.SIGINT, lambda s, f: signal_handler())
    signal.signal(signal.SIGTERM, lambda s, f: signal_handler())

    cache_manager = CacheManager()
    forwarder = Forwarder(settings, cache_manager)
    synchronizer = MessageSynchronizer(forwarder.client, cache_manager, forwarder)

    try:
        if args.copy:
            await forwarder.client.start()
            for source, target in settings.CHANNEL_MAPPINGS:
                if shutdown_event.is_set():
                    break
                await synchronizer.synchronize(source, target, shutdown_event)
            logger.info("Message synchronization complete.")
        else:
            await forwarder.run(shutdown_event)
    except asyncio.CancelledError:
        logger.info("Application shutdown forcefully.")
    finally:
        if forwarder.client.is_connected():
            await forwarder.client.disconnect()
            logger.info("Telegram client disconnected.")
        logger.info("Application has shut down.")

if __name__ == "__main__":
    asyncio.run(main())

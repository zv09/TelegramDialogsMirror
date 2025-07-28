#!/usr/bin/env python3
import asyncio
import traceback
from loguru import logger

from app.launcher import Launcher
from config.logger import setup_logging

async def main():
    """The main entry point of the application."""
    launcher = Launcher()
    setup_logging(launcher.settings)
    await launcher.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.critical(f"Application failed to start or crashed: {e}\n{traceback.format_exc()}")
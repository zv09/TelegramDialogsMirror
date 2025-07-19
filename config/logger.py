from loguru import logger
import logging
import sys
from config.config import Settings

class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

def setup_logging(settings: Settings):
    # Remove default Loguru handler to prevent duplicate output
    logger.remove()

    # Add file sink
    logger.add(
        f"Logs/{settings.APP_NAME}.log",
        rotation="10 MB",
        retention="10 days",
        compression="zip",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}"
    )

    # Add stdout sink for terminal output with explicit colors
    logger.add(
        sys.stdout,
        level="INFO",
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )

    # Intercept standard logging messages and redirect to Loguru
    logging.basicConfig(handlers=[InterceptHandler()], level=0)
    telethon_level = logging.INFO if settings.LOG_TELETHON_DIFFERENCES else logging.WARNING
    logging.getLogger("telethon").setLevel(telethon_level) # Set Telethon's logging level

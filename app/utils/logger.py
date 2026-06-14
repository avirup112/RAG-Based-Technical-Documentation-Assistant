import sys
from loguru import logger


def setup_logger():
    """
    Configures structured logging using loguru.
    """
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    )
    logger.add("logs/app.log", rotation="10 MB", retention="10 days", level="INFO")

import sys
from types import TracebackType
from typing import Optional, Type

from loguru import logger as log


def setup_logging(
    log_level: str = "INFO",
    log_to_file: bool = False,
) -> None:
    # Remove default handler
    log.remove()

    # Add console handler with custom format
    log.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<level>{message}</level>",
        colorize=True,
    )

    # Add file handler for persistent logging
    if log_to_file:
        log.add(
            "logs/app.log",
            level="DEBUG",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
            "{name}.{function}.{line} - {message}",
            rotation="1 day",
            retention="7 days",
            compression="zip",
        )


def handle_exception(
    exc_type: Type[BaseException],
    exc_value: BaseException,
    exc_traceback: Optional[TracebackType],
) -> None:
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    log.opt(exception=exc_value).error("Uncaught exception")

from __future__ import annotations

import logging
import sys
from typing import Any

from .filters import RequestContextFilter, SensitiveDataFilter
from .formatters import build_json_formatter, build_text_formatter

_CONFIGURED = False


def get_logger(name: str | None = None) -> logging.Logger:
    return logging.getLogger(name)


def setup_logging(*, level: str = "INFO", json_enabled: bool = False, access_log_enabled: bool = True) -> None:
    global _CONFIGURED

    log_level = _parse_log_level(level)
    formatter = build_json_formatter() if json_enabled else build_text_formatter()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    handler.setFormatter(formatter)
    handler.addFilter(RequestContextFilter())
    handler.addFilter(SensitiveDataFilter())

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(log_level)
    root_logger.addHandler(handler)

    for logger_name in ("app", "uvicorn", "uvicorn.error"):
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        logger.setLevel(log_level)
        logger.propagate = True

    access_logger = logging.getLogger("uvicorn.access")
    access_logger.handlers.clear()
    access_logger.setLevel(log_level)
    access_logger.propagate = access_log_enabled
    if access_log_enabled:
        access_logger.disabled = True

    _CONFIGURED = True


def _parse_log_level(level: str | int | Any) -> int:
    if isinstance(level, int):
        return level
    if isinstance(level, str):
        parsed = logging.getLevelName(level.upper())
        if isinstance(parsed, int):
            return parsed
    return logging.INFO

from __future__ import annotations

import logging
import re
from typing import Any

from .context import get_request_context

DEFAULT_LOG_FIELDS = {
    "request_id": "-",
    "user_id": "-",
    "path": "-",
    "method": "-",
    "client_ip": "-",
    "status_code": "-",
    "duration_ms": "-",
}

SENSITIVE_KEYS = {
    "access_token",
    "api_key",
    "apikey",
    "app_secret",
    "authorization",
    "database_url",
    "password",
    "refresh_token",
    "secret",
    "secret_key",
    "sign",
    "token",
}
SENSITIVE_PATTERN = re.compile(
    r"(?i)(password|token|access[_-]?token|refresh[_-]?token|authorization|api[_-]?key|secret|sign)=([^\s&]+)"
)


class RequestContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        context = get_request_context()
        for field, default in DEFAULT_LOG_FIELDS.items():
            setattr(record, field, context.get(field, getattr(record, field, default)))
        return True


class SensitiveDataFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = mask_sensitive_value(record.msg)
        if isinstance(record.args, dict):
            record.args = {key: mask_sensitive_value(value, key=key) for key, value in record.args.items()}
        elif isinstance(record.args, tuple):
            record.args = tuple(mask_sensitive_value(value) for value in record.args)
        return True


def mask_sensitive_value(value: Any, *, key: str | None = None) -> Any:
    if key and key.lower() in SENSITIVE_KEYS:
        return "***"
    if isinstance(value, str):
        return SENSITIVE_PATTERN.sub(r"\1=***", value)
    if isinstance(value, dict):
        return {item_key: mask_sensitive_value(item_value, key=str(item_key)) for item_key, item_value in value.items()}
    if isinstance(value, list):
        return [mask_sensitive_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(mask_sensitive_value(item) for item in value)
    return value

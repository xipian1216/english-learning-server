from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

STANDARD_FIELDS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "taskName",
    "thread",
    "threadName",
}

TEXT_LOG_FORMAT = (
    "%(asctime)s %(levelname)s [%(name)s] "
    "request_id=%(request_id)s user_id=%(user_id)s method=%(method)s path=%(path)s %(message)s"
)
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        for key, value in record.__dict__.items():
            if key in STANDARD_FIELDS or key.startswith("_"):
                continue
            payload[key] = value

        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        if record.stack_info:
            payload["stack_info"] = self.formatStack(record.stack_info)

        return json.dumps(payload, ensure_ascii=False, default=str)


def build_text_formatter() -> logging.Formatter:
    return logging.Formatter(fmt=TEXT_LOG_FORMAT, datefmt=DATE_FORMAT)


def build_json_formatter() -> logging.Formatter:
    return JsonFormatter()

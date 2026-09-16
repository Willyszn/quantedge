import logging
import sys
import time
from typing import Any

from app.core.config import get_settings


class JSONLogFormatter(logging.Formatter):
    """
    Emits one JSON object per line. Every service is expected to log with
    `extra={...}` fields such as service, symbol, event, duration_ms, status
    — never raw API keys or credentials (see app/core/logging.redact).
    """

    RESERVED = {
        "name",
        "msg",
        "args",
        "levelname",
        "levelno",
        "pathname",
        "filename",
        "module",
        "exc_info",
        "exc_text",
        "stack_info",
        "lineno",
        "funcName",
        "created",
        "msecs",
        "relativeCreated",
        "thread",
        "threadName",
        "processName",
        "process",
        "taskName",
    }

    def format(self, record: logging.LogRecord) -> str:
        import json

        payload: dict[str, Any] = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created)),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key, value in record.__dict__.items():
            if key not in self.RESERVED and not key.startswith("_"):
                payload[key] = redact(key, value)
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


SENSITIVE_KEYS = {"password", "api_key", "apikey", "secret", "token", "credential", "authorization"}


def redact(key: str, value: Any) -> Any:
    if any(sensitive in key.lower() for sensitive in SENSITIVE_KEYS):
        return "***REDACTED***"
    return value


def configure_logging() -> None:
    settings = get_settings()
    root = logging.getLogger()
    root.setLevel(logging.DEBUG if settings.ENVIRONMENT == "development" else logging.INFO)
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONLogFormatter())
    root.addHandler(handler)

    # Quiet noisy third-party loggers.
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

import json
import logging
import logging.handlers
from datetime import datetime, timezone

SENSITIVE_FIELDS = {"password", "token", "creditcard", "credit_card", "secret", "pin"}


def mask_sensitive(data: dict) -> dict:
    result = {}
    for k, v in data.items():
        if k.lower() in SENSITIVE_FIELDS:
            result[k] = "[MASKED]"
        elif isinstance(v, dict):
            result[k] = mask_sensitive(v)
        else:
            result[k] = v
    return result


class JSONFormatter(logging.Formatter):
    EXTRA_KEYS = ("method", "path", "statusCode", "userId", "operation", "entity", "entityId")

    def format(self, record: logging.LogRecord) -> str:
        entry: dict = {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
        }
        for key in self.EXTRA_KEYS:
            if hasattr(record, key):
                entry[key] = getattr(record, key)
        return json.dumps(entry, ensure_ascii=False)


def _build_logger() -> logging.Logger:
    log = logging.getLogger("app")
    if log.handlers:
        return log

    log.setLevel(logging.DEBUG)
    formatter = JSONFormatter()

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    log.addHandler(console)

    file_handler = logging.FileHandler("app.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    log.addHandler(file_handler)

    return log


logger = _build_logger()

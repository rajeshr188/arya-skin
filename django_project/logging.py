import json
import logging
from datetime import UTC, datetime


class JsonFormatter(logging.Formatter):
    """One-line operational logs without query strings or request bodies."""

    def format(self, record):
        payload = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "status_code"):
            payload["status_code"] = record.status_code
        request = getattr(record, "request", None)
        if request is not None:
            payload["method"] = request.method
            payload["path"] = request.path
        if record.exc_info:
            payload["exception_type"] = type(record.exc_info[1]).__name__
        return json.dumps(payload, ensure_ascii=False)

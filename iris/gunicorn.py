import logging.config
from typing import Any

import gunicorn.glogging


class HealthcheckFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        return "/healthz" not in msg and "/readyz" not in msg and "/livez" not in msg


class Logger(gunicorn.glogging.Logger):
    def setup(self, *args: Any, **kwargs: Any) -> None:
        super(Logger, self).setup(*args, **kwargs)

        logger = logging.getLogger("gunicorn.access")
        logger.addFilter(HealthcheckFilter())

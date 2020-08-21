import logging
import gunicorn.glogging


class HealthcheckFilter(logging.Filter):
    def filter(self, record):
        msg = record.getMessage()
        return "/healthz" not in msg and "/readyz" not in msg and "/livez" not in msg


class Logger(gunicorn.glogging.Logger):
    def setup(self, cfg):
        super().setup(cfg)
        logger = logging.getLogger("gunicorn.access")
        logger.addFilter(HealthcheckFilter())

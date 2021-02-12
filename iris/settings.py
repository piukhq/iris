import logging
import sys

from os import getenv


# logging
LOG_FORMAT = getenv("LOG_FORMAT", "%(asctime)s :: %(name)s :: %(levelname)s :: %(message)s")
LOG_LEVEL = getattr(logging, getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)
logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL)

PROMETHEUS_LOG_LEVEL = getattr(logging, getenv("PROMETHEUS_LOG_LEVEL", "INFO").upper(), logging.INFO)
PROMETHEUS_PUSH_GATEWAY = getenv("PROMETHEUS_PUSH_GATEWAY", "http://localhost:9100")
PROMETHEUS_JOB = "iris"

TESTING = any("test" in arg for arg in sys.argv)

from os import getenv

from flask import Response
from prometheus_client import CONTENT_TYPE_LATEST, REGISTRY, CollectorRegistry, Counter, generate_latest, multiprocess

status_code_counter = Counter(
    name="response_by_status", documentation="Count for iris response codes.", labelnames=("status",), namespace="iris"
)


def handle_metrics() -> Response:
    registry = REGISTRY

    if getenv("PROMETHEUS_MULTIPROC_DIR"):
        registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(registry)

    headers = {"Content-Type": CONTENT_TYPE_LATEST}
    return Response(generate_latest(registry), status=200, headers=headers)

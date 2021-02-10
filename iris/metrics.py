from prometheus_client import Counter, CollectorRegistry


registry = CollectorRegistry()

status_code_counter = Counter(
    name="response_by_status",
    documentation="Count for iris response codes.",
    labelnames=("status",),
    namespace="iris"
)

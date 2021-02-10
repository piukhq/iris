from prometheus_client import Counter, CollectorRegistry


registry = CollectorRegistry()

status_code_counter = Counter(
    name="status_code_counter",
    documentation="Count for iris response codes.",
    labelnames=("status",),
    namespace="iris"
)

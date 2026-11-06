import os
import time

import redis


def percentile(values, pct):
    ordered = sorted(values)
    rank = (len(ordered) - 1) * pct / 100.0
    low = int(rank)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (rank - low)


client = redis.Redis(
    host=os.environ["REDIS_HOST"],
    port=int(os.environ["REDIS_PORT"]),
    username=os.environ["REDIS_USERNAME"],
    password=os.environ["REDIS_PASSWORD"],
    socket_timeout=3,
)

for _ in range(100):
    client.ping()

samples = []
for _ in range(1000):
    start = time.perf_counter_ns()
    client.ping()
    samples.append((time.perf_counter_ns() - start) / 1e6)

print("Raw Redis PING round trip")
print("  p50: %.2f ms" % percentile(samples, 50))
print("  p95: %.2f ms" % percentile(samples, 95))
print("  p99: %.2f ms" % percentile(samples, 99))

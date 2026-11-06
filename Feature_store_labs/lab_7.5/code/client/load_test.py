import os
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from feast import FeatureStore

REPO_PATH = os.environ.get("FEAST_REPO", os.path.expanduser("~/poridhi-lab-7-5/feature_repo"))
WORKERS = int(os.environ.get("WORKERS", "8"))
REQUESTS_PER_WORKER = int(os.environ.get("REQUESTS_PER_WORKER", "300"))
FEATURES = [
    "driver_hourly_stats:conv_rate",
    "driver_hourly_stats:acc_rate",
    "driver_hourly_stats:avg_daily_trips",
]

barrier = threading.Barrier(WORKERS)


def percentile(values, pct):
    ordered = sorted(values)
    rank = (len(ordered) - 1) * pct / 100.0
    low = int(rank)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (rank - low)


def worker(seed):
    store = FeatureStore(repo_path=REPO_PATH)
    rng = random.Random(seed)
    for _ in range(20):
        store.get_online_features(features=FEATURES, entity_rows=[{"driver_id": rng.randint(1001, 2000)}]).to_dict()
    barrier.wait()
    latencies = []
    began = time.perf_counter()
    for _ in range(REQUESTS_PER_WORKER):
        row = [{"driver_id": rng.randint(1001, 2000)}]
        start = time.perf_counter_ns()
        store.get_online_features(features=FEATURES, entity_rows=row).to_dict()
        latencies.append((time.perf_counter_ns() - start) / 1e6)
    return latencies, time.perf_counter() - began


with ThreadPoolExecutor(max_workers=WORKERS) as pool:
    results = list(pool.map(worker, range(WORKERS)))

all_latencies = [x for lat, _ in results for x in lat]
wall = max(elapsed for _, elapsed in results)
print("Workers: %d, total requests: %d" % (WORKERS, len(all_latencies)))
print("Throughput: %.0f calls/s" % (len(all_latencies) / wall))
print("p50: %.2f ms" % percentile(all_latencies, 50))
print("p95: %.2f ms" % percentile(all_latencies, 95))
print("p99: %.2f ms" % percentile(all_latencies, 99))

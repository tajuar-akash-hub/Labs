import os
import random
import statistics
import time

from feast import FeatureStore

REPO_PATH = os.environ.get("FEAST_REPO", os.path.expanduser("~/poridhi-lab-7-5/feature_repo"))
N_REQUESTS = int(os.environ.get("N_REQUESTS", "1000"))
WARMUP = int(os.environ.get("WARMUP", "50"))
BATCH_SIZE = int(os.environ.get("BATCH_SIZE", "1"))
TARGET_MS = float(os.environ.get("TARGET_MS", "10"))
TARGET_PCT = float(os.environ.get("TARGET_PCT", "95"))
FIRST_ID = 1001
NUM_DRIVERS = 1000

FEATURES = [
    "driver_hourly_stats:conv_rate",
    "driver_hourly_stats:acc_rate",
    "driver_hourly_stats:avg_daily_trips",
]


def percentile(values, pct):
    ordered = sorted(values)
    rank = (len(ordered) - 1) * pct / 100.0
    low = int(rank)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (rank - low)


def main():
    t0 = time.perf_counter()
    store = FeatureStore(repo_path=REPO_PATH)
    init_ms = (time.perf_counter() - t0) * 1000

    rng = random.Random(7)

    def make_rows():
        ids = rng.sample(range(FIRST_ID, FIRST_ID + NUM_DRIVERS), BATCH_SIZE)
        return [{"driver_id": i} for i in ids]

    t0 = time.perf_counter()
    first = store.get_online_features(features=FEATURES, entity_rows=make_rows()).to_dict()
    cold_ms = (time.perf_counter() - t0) * 1000
    if any(v is None for v in first["conv_rate"]):
        raise SystemExit("Got None features. Run feast materialize-incremental first (Step 11).")

    for _ in range(WARMUP):
        store.get_online_features(features=FEATURES, entity_rows=make_rows()).to_dict()

    latencies = []
    for _ in range(N_REQUESTS):
        rows = make_rows()
        start = time.perf_counter_ns()
        store.get_online_features(features=FEATURES, entity_rows=rows).to_dict()
        latencies.append((time.perf_counter_ns() - start) / 1e6)

    observed = percentile(latencies, TARGET_PCT)
    print("Feast repo           :", REPO_PATH)
    print("Requests / batch size: %d / %d" % (N_REQUESTS, BATCH_SIZE))
    print("FeatureStore init    : %.1f ms" % init_ms)
    print("First (cold) call    : %.1f ms" % cold_ms)
    print("min                  : %.2f ms" % min(latencies))
    print("mean                 : %.2f ms" % statistics.mean(latencies))
    print("p50                  : %.2f ms" % percentile(latencies, 50))
    print("p90                  : %.2f ms" % percentile(latencies, 90))
    print("p95                  : %.2f ms" % percentile(latencies, 95))
    print("p99                  : %.2f ms" % percentile(latencies, 99))
    print("max                  : %.2f ms" % max(latencies))
    print("stdev                : %.2f ms" % statistics.pstdev(latencies))
    print("throughput           : %.0f calls/s" % (len(latencies) / (sum(latencies) / 1000)))

    buckets = [(0, 2), (2, 5), (5, 10), (10, 20), (20, float("inf"))]
    print("Distribution:")
    for low, high in buckets:
        count = sum(1 for x in latencies if low <= x < high)
        label = "%d to %d ms" % (low, high) if high != float("inf") else "%d ms and above" % low
        print("  %-16s %5d  %5.1f%%" % (label, count, 100.0 * count / len(latencies)))

    verdict = "PASS" if observed < TARGET_MS else "FAIL"
    print("Verdict: %s (p%g = %.2f ms, target under %.1f ms)" % (verdict, TARGET_PCT, observed, TARGET_MS))


if __name__ == "__main__":
    main()

import os
import statistics
import time
from datetime import datetime, timezone

import pandas as pd
from feast import FeatureStore
from feast.data_source import PushMode

N = int(os.environ.get("N_EVENTS", "200"))
P95_LIMIT_MS = float(os.environ.get("P95_LIMIT_MS", "100"))

store = FeatureStore(repo_path=".")
features = ["driver_stats_stream:avg_daily_trips"]

push_ms, total_ms = [], []
mismatches = 0

for i in range(N):
    driver_id = 2001 + i
    marker = 10000 + i
    now = datetime.now(timezone.utc)
    df = pd.DataFrame({
        "driver_id": [driver_id],
        "conv_rate": [0.5],
        "acc_rate": [0.5],
        "avg_daily_trips": [marker],
        "event_timestamp": [now],
        "created": [now],
    })

    t0 = time.perf_counter()
    store.push("driver_stats_push", df, to=PushMode.ONLINE)
    t1 = time.perf_counter()
    got = store.get_online_features(
        features=features, entity_rows=[{"driver_id": driver_id}]
    ).to_dict()["avg_daily_trips"][0]
    t2 = time.perf_counter()

    if got != marker:
        mismatches += 1
    push_ms.append((t1 - t0) * 1000)
    total_ms.append((t2 - t0) * 1000)


def pct(data, p):
    return statistics.quantiles(data, n=100)[p - 1]


print("Events pushed:", N, "| read-after-write mismatches:", mismatches)
print("Push only        p50 %.2f ms | p95 %.2f ms | p99 %.2f ms" % (pct(push_ms, 50), pct(push_ms, 95), pct(push_ms, 99)))
print("Push + read back p50 %.2f ms | p95 %.2f ms | p99 %.2f ms" % (pct(total_ms, 50), pct(total_ms, 95), pct(total_ms, 99)))

ok = mismatches == 0 and pct(push_ms, 95) < P95_LIMIT_MS
print("RESULT:", "PASS" if ok else "FAIL", "(push p95 limit %.0f ms)" % P95_LIMIT_MS)

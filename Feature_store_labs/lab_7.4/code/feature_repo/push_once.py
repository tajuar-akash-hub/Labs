import time
from datetime import datetime, timezone

import pandas as pd
from feast import FeatureStore
from feast.data_source import PushMode

store = FeatureStore(repo_path=".")

event = pd.DataFrame({
    "driver_id": [1011],
    "conv_rate": [0.91],
    "acc_rate": [0.88],
    "avg_daily_trips": [321],
    "event_timestamp": [datetime.now(timezone.utc)],
    "created": [datetime.now(timezone.utc)],
})

t0 = time.perf_counter()
store.push("driver_stats_push", event, to=PushMode.ONLINE)
t1 = time.perf_counter()

features = store.get_online_features(
    features=[
        "driver_stats_stream:conv_rate",
        "driver_stats_stream:acc_rate",
        "driver_stats_stream:avg_daily_trips",
    ],
    entity_rows=[{"driver_id": 1011}],
).to_dict()
t2 = time.perf_counter()

print("Push latency:           %.2f ms" % ((t1 - t0) * 1000))
print("Read-after-write total: %.2f ms" % ((t2 - t0) * 1000))
print(features)

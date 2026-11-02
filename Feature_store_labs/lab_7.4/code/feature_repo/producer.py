import os
import random
import time
from datetime import datetime, timedelta, timezone

import pandas as pd
from feast import FeatureStore
from feast.data_source import PushMode

EVENTS = int(os.environ.get("EVENTS", "30"))
INTERVAL_MS = int(os.environ.get("INTERVAL_MS", "200"))

store = FeatureStore(repo_path=".")
state = {d: {"conv": 0.5, "acc": 0.5, "trips": 100} for d in range(1001, 1006)}

BASE = datetime.now(timezone.utc) - timedelta(seconds=EVENTS)

for i in range(EVENTS):
    driver_id = random.choice(list(state))
    s = state[driver_id]
    s["conv"] = min(1.0, max(0.0, s["conv"] + random.uniform(-0.05, 0.05)))
    s["acc"] = min(1.0, max(0.0, s["acc"] + random.uniform(-0.05, 0.05)))
    s["trips"] += random.randint(0, 3)

    now = BASE + timedelta(seconds=i)
    df = pd.DataFrame({
        "driver_id": [driver_id],
        "conv_rate": [s["conv"]],
        "acc_rate": [s["acc"]],
        "avg_daily_trips": [s["trips"]],
        "event_timestamp": [now],
        "created": [now],
    })

    t0 = time.perf_counter()
    store.push("driver_stats_push", df, to=PushMode.ONLINE)
    ms = (time.perf_counter() - t0) * 1000
    print("event %02d | driver %d | trips %d | push %.2f ms" % (i + 1, driver_id, s["trips"], ms))
    time.sleep(INTERVAL_MS / 1000)

print("Done. Pushed", EVENTS, "events.")

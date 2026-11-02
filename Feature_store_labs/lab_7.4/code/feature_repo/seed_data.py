import os
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd

os.makedirs("data", exist_ok=True)
rng = np.random.default_rng(7)
now = datetime.now(timezone.utc)

rows = []
for driver_id in range(1001, 1006):
    for h in range(24):
        rows.append({
            "driver_id": driver_id,
            "event_timestamp": now - timedelta(hours=h + 1),
            "created": now - timedelta(hours=h + 1),
            "conv_rate": np.float32(rng.random()),
            "acc_rate": np.float32(rng.random()),
            "avg_daily_trips": int(rng.integers(10, 500)),
        })

df = pd.DataFrame(rows)
df["conv_rate"] = df["conv_rate"].astype("float32")
df["acc_rate"] = df["acc_rate"].astype("float32")
df["avg_daily_trips"] = df["avg_daily_trips"].astype("int64")
df.to_parquet("data/driver_stats.parquet", index=False)
print("Seeded", len(df), "rows into data/driver_stats.parquet")

import numpy as np
import pandas as pd

NUM_DRIVERS = 1000
HOURS = 72
FIRST_ID = 1001

rng = np.random.default_rng(42)
now = pd.Timestamp.now(tz="UTC")
end = now.replace(minute=0, second=0, microsecond=0, nanosecond=0)
hours = pd.date_range(end=end, periods=HOURS, freq="h")

driver_ids = np.repeat(np.arange(FIRST_ID, FIRST_ID + NUM_DRIVERS), HOURS).astype("int64")
timestamps = pd.to_datetime(np.tile(hours.asi8, NUM_DRIVERS), unit="ns", utc=True)
n = len(driver_ids)

df = pd.DataFrame(
    {
        "driver_id": driver_ids,
        "event_timestamp": timestamps,
        "created": now,
        "conv_rate": rng.random(n).astype("float32"),
        "acc_rate": rng.random(n).astype("float32"),
        "avg_daily_trips": rng.integers(1, 500, n).astype("int64"),
    }
)
df.to_parquet("data/driver_stats.parquet", index=False)
print("Wrote", len(df), "rows for", NUM_DRIVERS, "drivers")

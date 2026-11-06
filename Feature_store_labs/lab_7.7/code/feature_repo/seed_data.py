from datetime import timedelta

import pandas as pd

one_hour_ago = pd.Timestamp.now(tz="UTC") - timedelta(hours=1)

seed = pd.DataFrame(
    {
        "driver_id": [1001, 1002, 1003],
        "event_timestamp": pd.to_datetime([one_hour_ago] * 3, utc=True).astype(
            "datetime64[ns, UTC]"
        ),
        "trips_in_window": [0, 0, 0],
        "avg_speed_kmh": [0.0, 0.0, 0.0],
        "distance_in_window_km": [0.0, 0.0, 0.0],
    }
)

seed.to_parquet("data/driver_stats.parquet", index=False)
print(seed.dtypes)
print("Wrote data/driver_stats.parquet with", len(seed), "rows")

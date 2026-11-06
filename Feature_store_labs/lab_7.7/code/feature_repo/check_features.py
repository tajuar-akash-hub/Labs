import pandas as pd
from feast import FeatureStore

store = FeatureStore(repo_path=".")

features = [
    "driver_stats_stream:trips_in_window",
    "driver_stats_stream:avg_speed_kmh",
    "driver_stats_stream:distance_in_window_km",
]

print("Online features from Redis:")
online = store.get_online_features(
    features=features,
    entity_rows=[{"driver_id": 1001}, {"driver_id": 1002}, {"driver_id": 1003}],
).to_dict()
print(pd.DataFrame(online))

print("Offline history in data/driver_stats.parquet:")
offline = pd.read_parquet("data/driver_stats.parquet")
print("Rows:", len(offline))
print(offline.sort_values("event_timestamp").tail(5))

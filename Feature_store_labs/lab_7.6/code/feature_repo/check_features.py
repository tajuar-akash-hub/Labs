from datetime import datetime, timezone

import pandas as pd
from feast import FeatureStore

store = FeatureStore(repo_path=".")

features = [
    "driver_daily_stats:daily_trips",
    "driver_daily_stats:avg_rating",
    "driver_daily_stats:total_distance_km",
]

print("Online features from Redis:")
online = store.get_online_features(
    features=features,
    entity_rows=[{"driver_id": 1001}, {"driver_id": 1002}],
).to_dict()
print(online)

print("Historical features from the Spark output in MinIO:")
entity_df = pd.DataFrame(
    {
        "driver_id": [1001, 1002, 1003],
        "event_timestamp": [datetime.now(timezone.utc)] * 3,
    }
)
historical = store.get_historical_features(
    entity_df=entity_df, features=features
).to_df()
print(historical)

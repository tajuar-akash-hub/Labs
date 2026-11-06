from feast import FeatureStore

store = FeatureStore(repo_path=".")

by_reference = store.get_online_features(
    features=[
        "driver_hourly_stats:conv_rate",
        "driver_hourly_stats:acc_rate",
        "driver_hourly_stats:avg_daily_trips",
    ],
    entity_rows=[{"driver_id": 1001}],
).to_dict()
print("By feature reference:", by_reference)

by_service = store.get_online_features(
    features=store.get_feature_service("driver_activity_v1"),
    entity_rows=[{"driver_id": 1001}, {"driver_id": 1002}],
).to_dict()
print("By feature service:", by_service)

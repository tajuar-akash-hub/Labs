from feast import FeatureStore

store = FeatureStore(repo_path=".")
result = store.get_online_features(
    features=[
        "driver_stats_stream:conv_rate",
        "driver_stats_stream:acc_rate",
        "driver_stats_stream:avg_daily_trips",
    ],
    entity_rows=[{"driver_id": d} for d in range(1001, 1006)],
).to_df()
print(result)

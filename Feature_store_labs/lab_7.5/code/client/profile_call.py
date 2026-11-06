import cProfile
import os
import pstats

from feast import FeatureStore

REPO_PATH = os.environ.get("FEAST_REPO", os.path.expanduser("~/poridhi-lab-7-5/feature_repo"))
FEATURES = [
    "driver_hourly_stats:conv_rate",
    "driver_hourly_stats:acc_rate",
    "driver_hourly_stats:avg_daily_trips",
]

store = FeatureStore(repo_path=REPO_PATH)
for i in range(50):
    store.get_online_features(features=FEATURES, entity_rows=[{"driver_id": 1001 + i}]).to_dict()

profiler = cProfile.Profile()
profiler.enable()
for i in range(500):
    store.get_online_features(features=FEATURES, entity_rows=[{"driver_id": 1001 + (i % 1000)}]).to_dict()
profiler.disable()

pstats.Stats(profiler).sort_stats("cumulative").print_stats(12)

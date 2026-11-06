from datetime import timedelta

from feast import Entity, FeatureView, Field, FileSource, PushSource
from feast.types import Float64, Int64, ValueType

driver = Entity(name="driver", join_keys=["driver_id"], value_type=ValueType.INT64)

driver_stats_batch_source = FileSource(
    name="driver_stats_batch_source",
    path="data/driver_stats.parquet",
    timestamp_field="event_timestamp",
)

driver_stats_push_source = PushSource(
    name="driver_stats_push",
    batch_source=driver_stats_batch_source,
)

driver_stats_stream = FeatureView(
    name="driver_stats_stream",
    entities=[driver],
    ttl=timedelta(days=1),
    schema=[
        Field(name="trips_in_window", dtype=Int64),
        Field(name="avg_speed_kmh", dtype=Float64),
        Field(name="distance_in_window_km", dtype=Float64),
    ],
    source=driver_stats_push_source,
    online=True,
)

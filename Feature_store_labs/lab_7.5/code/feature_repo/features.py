from datetime import timedelta

from feast import Entity, FeatureService, FeatureView, Field, FileSource
from feast.types import Float32, Int64
from feast.value_type import ValueType

driver = Entity(name="driver", join_keys=["driver_id"], value_type=ValueType.INT64)

driver_stats_source = FileSource(
    name="driver_hourly_stats_source",
    path="data/driver_stats.parquet",
    timestamp_field="event_timestamp",
    created_timestamp_column="created",
)

driver_hourly_stats = FeatureView(
    name="driver_hourly_stats",
    entities=[driver],
    ttl=timedelta(days=2),
    schema=[
        Field(name="conv_rate", dtype=Float32),
        Field(name="acc_rate", dtype=Float32),
        Field(name="avg_daily_trips", dtype=Int64),
    ],
    online=True,
    source=driver_stats_source,
)

driver_activity_v1 = FeatureService(
    name="driver_activity_v1",
    features=[driver_hourly_stats],
)

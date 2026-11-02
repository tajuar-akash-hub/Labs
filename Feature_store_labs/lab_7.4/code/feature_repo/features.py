from datetime import timedelta

from feast import Entity, FeatureView, Field, FileSource, PushSource
from feast.types import Float32, Int64, ValueType

driver = Entity(name="driver", join_keys=["driver_id"], value_type=ValueType.INT64)

driver_stats_batch = FileSource(
    name="driver_stats_batch",
    path="data/driver_stats.parquet",
    timestamp_field="event_timestamp",
    created_timestamp_column="created",
)

driver_stats_push = PushSource(
    name="driver_stats_push",
    batch_source=driver_stats_batch,
)

driver_stats_stream = FeatureView(
    name="driver_stats_stream",
    entities=[driver],
    ttl=timedelta(days=1),
    schema=[
        Field(name="conv_rate", dtype=Float32),
        Field(name="acc_rate", dtype=Float32),
        Field(name="avg_daily_trips", dtype=Int64),
    ],
    online=True,
    source=driver_stats_push,
    tags={"lab": "7.4", "ingestion": "push"},
)

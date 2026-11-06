from datetime import timedelta

from feast import Entity, FeatureView, Field, FileSource, ValueType
from feast.types import Float64, Int64

driver = Entity(name="driver", join_keys=["driver_id"], value_type=ValueType.INT64)

driver_daily_source = FileSource(
    name="driver_daily_source",
    path="s3://feast-spark-lab/offline/driver_daily_stats",
    timestamp_field="event_timestamp",
    created_timestamp_column="created",
    s3_endpoint_override="http://127.0.0.1:9000",
)

driver_daily_stats = FeatureView(
    name="driver_daily_stats",
    entities=[driver],
    ttl=timedelta(days=30),
    schema=[
        Field(name="daily_trips", dtype=Int64),
        Field(name="avg_rating", dtype=Float64),
        Field(name="total_distance_km", dtype=Float64),
    ],
    source=driver_daily_source,
    online=True,
)

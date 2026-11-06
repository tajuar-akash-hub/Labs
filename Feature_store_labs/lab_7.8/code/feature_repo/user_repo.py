from datetime import timedelta

from feast import Entity, FeatureView, Field, FileSource, ValueType
from feast.types import Float64, Int64, String

user = Entity(name="user", join_keys=["user_id"], value_type=ValueType.INT64)

user_stats_source = FileSource(
    name="user_stats_source",
    path="data/user_stats.parquet",
    timestamp_field="event_timestamp",
)

user_stats = FeatureView(
    name="user_stats",
    entities=[user],
    ttl=timedelta(days=7),
    schema=[
        Field(name="orders_7d", dtype=Int64),
        Field(name="avg_order_value", dtype=Float64),
        Field(name="top_category", dtype=String),
    ],
    source=user_stats_source,
    online=True,
)

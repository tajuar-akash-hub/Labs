from datetime import datetime, timedelta, timezone

import pandas as pd
from feast import FeatureStore
from feast.data_source import PushMode

store = FeatureStore(repo_path=".")

DRIVER_ID = 1010
BASE = datetime.now(timezone.utc) - timedelta(seconds=3)


def event(trips, step):
    now = BASE + timedelta(seconds=step)
    return pd.DataFrame({
        "driver_id": [DRIVER_ID],
        "conv_rate": [0.5],
        "acc_rate": [0.5],
        "avg_daily_trips": [trips],
        "event_timestamp": [now],
        "created": [now],
    })


def online_trips():
    out = store.get_online_features(
        features=["driver_stats_stream:avg_daily_trips"],
        entity_rows=[{"driver_id": DRIVER_ID}],
    ).to_dict()
    return out["avg_daily_trips"][0]


def offline_rows(trips):
    df = pd.read_parquet("data/driver_stats.parquet")
    return int((df["avg_daily_trips"] == trips).sum())


def push(trips, step, mode):
    before = offline_rows(trips)
    store.push("driver_stats_push", event(trips, step), to=mode)
    return online_trips(), offline_rows(trips) - before


online, added = push(7001, 1, PushMode.ONLINE)
print("After ONLINE push (7001):               online =", online, "| offline rows added =", added)

online, added = push(7002, 2, PushMode.OFFLINE)
print("After OFFLINE push (7002):              online =", online, "| offline rows added =", added)

online, added = push(7003, 3, PushMode.ONLINE_AND_OFFLINE)
print("After ONLINE_AND_OFFLINE push (7003):   online =", online, "| offline rows added =", added)

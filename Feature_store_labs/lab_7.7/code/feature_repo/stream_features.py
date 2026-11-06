import json
import time
from collections import defaultdict, deque
from datetime import timedelta

import pandas as pd
from confluent_kafka import Consumer
from feast import FeatureStore
from feast.data_source import PushMode

TOPIC = "driver-trips"
PUSH_SOURCE = "driver_stats_push"
WINDOW_SECONDS = 10
IDLE_STOP_SECONDS = 15
MAX_WAIT_SECONDS = 600

store = FeatureStore(repo_path=".")

consumer = Consumer(
    {
        "bootstrap.servers": "localhost:9092",
        "group.id": "feast-stream",
        "auto.offset.reset": "earliest",
    }
)
consumer.subscribe([TOPIC])

windows = defaultdict(deque)
pushed = 0
started = time.time()
last_message = None

print("Waiting for events on topic", TOPIC)
try:
    while True:
        msg = consumer.poll(1.0)
        now = time.time()
        if msg is None:
            if last_message is not None and now - last_message > IDLE_STOP_SECONDS:
                break
            if last_message is None and now - started > MAX_WAIT_SECONDS:
                break
            continue
        if msg.error():
            print("Kafka error:", msg.error())
            continue

        last_message = now
        event = json.loads(msg.value())
        event_time = pd.Timestamp(event["event_time"])
        driver_id = int(event["driver_id"])

        window = windows[driver_id]
        window.append(
            (event_time, float(event["distance_km"]), float(event["speed_kmh"]))
        )
        cutoff = event_time - timedelta(seconds=WINDOW_SECONDS)
        while window and window[0][0] < cutoff:
            window.popleft()

        speeds = [item[2] for item in window]
        features = pd.DataFrame(
            {
                "driver_id": [driver_id],
                "event_timestamp": pd.to_datetime([event_time], utc=True).astype(
                    "datetime64[ns, UTC]"
                ),
                "trips_in_window": [len(window)],
                "avg_speed_kmh": [round(sum(speeds) / len(speeds), 2)],
                "distance_in_window_km": [round(sum(i[1] for i in window), 2)],
            }
        )
        store.push(PUSH_SOURCE, features, to=PushMode.ONLINE_AND_OFFLINE)
        pushed += 1
        print(
            f"driver {driver_id}: trips={len(window)} "
            f"avg_speed={features['avg_speed_kmh'][0]} "
            f"distance={features['distance_in_window_km'][0]}"
        )
finally:
    consumer.close()

print("Done. Pushed", pushed, "feature rows to Feast")

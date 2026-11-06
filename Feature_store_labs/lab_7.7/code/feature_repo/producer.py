import json
import random
import time
from datetime import datetime, timezone

from confluent_kafka import Producer

TOPIC = "driver-trips"
EVENT_COUNT = 60

producer = Producer({"bootstrap.servers": "localhost:9092"})
random.seed(42)

for i in range(EVENT_COUNT):
    driver_id = 1001 + (i % 3)
    event = {
        "driver_id": driver_id,
        "distance_km": round(random.uniform(0.5, 6.0), 2),
        "speed_kmh": round(random.uniform(20.0, 70.0), 2),
        "event_time": datetime.now(timezone.utc).isoformat(),
    }
    producer.produce(TOPIC, key=str(driver_id), value=json.dumps(event))
    producer.poll(0)
    time.sleep(0.5)

producer.flush()
print("Sent", EVENT_COUNT, "events to", TOPIC)

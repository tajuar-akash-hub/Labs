import os

import redis

r = redis.Redis(
    host=os.environ["REDIS_HOST"],
    port=int(os.environ["REDIS_PORT"]),
    username=os.environ["REDIS_USERNAME"],
    password=os.environ["REDIS_PASSWORD"],
)

keys = list(r.scan_iter(match=b"*streaming_ingestion*", count=1000))
print("Feast keys for project streaming_ingestion:", len(keys))

for k in keys[:3]:
    print("  key (first 40 bytes):", k[:40], "| type:", r.type(k).decode(), "| ttl:", r.ttl(k))
    for field in r.hkeys(k):
        print("     hash field:", field)

stats = r.info("commandstats")
print("HSET calls so far:", stats.get("cmdstat_hset", {}).get("calls", 0))

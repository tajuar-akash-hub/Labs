# Lab 7.1: Feature Store Concepts (Easy Version)

## Introduction

A **feature store** is a place where we keep the data (features) our machine learning models use. The trick is that models need features in two very different ways:

- **Training**: a model needs lots of historical data, slowly, all at once. This is the **offline store**.
- **Serving (predicting)**: when a real user shows up, the model needs their features in milliseconds. This is the **online store**.

A feature store gives you both, and — most importantly — it makes sure the training data does not "cheat" by peeking into the future. That cheating is called **feature leakage**, and the way we prevent it is called **point-in-time correctness (PITC)**.

In this short, beginner-friendly lab you will:
1. Spin up a tiny PostgreSQL (offline) + Redis (online) stack with one Docker Compose file.
2. Insert a handful of fake users and features.
3. See a leaky query, then fix it with a point-in-time-aware query.
4. Copy the latest feature snapshot into Redis ("materialize").
5. Read it back fast and check the **freshness** (how old the data is).

You can finish the whole thing in under an hour on a laptop.

![alt text](image.png)

### Architecture Explanation (the short version)

Three things run on your machine in Docker:

- **PostgreSQL** — the offline store. Holds history.
- **Redis** — the online store. Holds only the latest snapshot per user, for fast lookups.
- A **Python client** container — where you run small scripts to write, query, and read features.

The only "magic" step is the **materialize** script: it copies the newest value per user from PostgreSQL into Redis. That is exactly what real feature stores like Feast automate for you.

## Learning Objectives

By the end of this lab you will be able to:

- Explain in one sentence what an offline store and an online store are for.
- Show what feature leakage looks like with a tiny SQL example.
- Fix that leakage with a point-in-time join.
- Run a materialize step and read features back from Redis in milliseconds.

## Prerequisites

- Docker Engine + Docker Compose installed (any recent version).
- About 30 minutes.

## Prologue (1-minute story)

You trained a fraud model. It looked great in the notebook. Six months later in production it suddenly got worse. Why? Because during training you joined "the latest user info" with "the fraud label from 5 days ago" — and the "latest user info" included data from *after* the fraud happened. The model learned from the future. A feature store, with point-in-time joins, prevents exactly that. You will reproduce and fix it below.

## Step-by-Step Implementation

### Step 1: One folder, two files

```bash
mkdir fs-easy && cd fs-easy
```

Create `docker-compose.yml`:

```yaml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: fsuser
      POSTGRES_PASSWORD: fspass
      POSTGRES_DB: feast_offline
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U fsuser -d feast_offline"]
      interval: 5s
      timeout: 3s
      retries: 10

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 10

  client:
    image: python:3.11-slim
    working_dir: /app
    volumes:
      - ./client:/app
    command: sleep infinity
    environment:
      PG_HOST: postgres
      PG_PORT: "5432"
      PG_USER: fsuser
      PG_PASSWORD: fspass
      PG_DB: feast_offline
      REDIS_HOST: redis
      REDIS_PORT: "6379"
```

Create `client/requirements.txt`:

```
psycopg2-binary
redis
```

Create `client/init.sql` (we will auto-load it):

```sql
CREATE TABLE feature_values (
    entity_id      TEXT        NOT NULL,
    feature_name   TEXT        NOT NULL,
    feature_value  DOUBLE PRECISION NOT NULL,
    event_timestamp TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (entity_id, feature_name, event_timestamp)
);

CREATE TABLE labels (
    entity_id      TEXT NOT NULL,
    label          INT  NOT NULL,
    event_timestamp TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (entity_id, event_timestamp)
);
```

> Tiny simplification vs. the full lab: we dropped `entity_registry` and `feature_definitions` so there is less ceremony. The two tables we keep are the only ones that matter for the concepts.

Mount `init.sql` into Postgres by adding one line under the `postgres` service in `docker-compose.yml`:

```yaml
    volumes:
      - ./client/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
```

Start everything:

```bash
docker compose up -d
docker compose exec client pip install -r /app/requirements.txt
```

Wait until both are healthy (`docker compose ps`).

### Step 2: Seed 3 users, 5 days, 2 features

Create `client/seed.py`:

```python
import os, random
from datetime import datetime, timedelta, timezone
import psycopg2

PG = dict(host=os.environ["PG_HOST"], port=os.environ["PG_PORT"],
          user=os.environ["PG_USER"], password=os.environ["PG_PASSWORD"],
          dbname=os.environ["PG_DB"])

now = datetime.now(timezone.utc)
conn = psycopg2.connect(**PG); cur = conn.cursor()

users = ["alice", "bob", "carol"]
features = ["tx_count_7d", "avg_tx_amount"]

rows = []
for u in users:
    for d in range(5):                # 5 days of history
        ts = now - timedelta(days=4-d)
        rows.append((u, "tx_count_7d",     random.randint(1, 20), ts))
        rows.append((u, "avg_tx_amount",   round(random.uniform(10, 100), 2), ts))

cur.executemany(
    "INSERT INTO feature_values VALUES (%s,%s,%s,%s) ON CONFLICT DO NOTHING", rows)

# One label per user, dated 2 days ago (so leakage is possible)
labels = [(u, random.randint(0, 1), now - timedelta(days=2)) for u in users]
cur.executemany("INSERT INTO labels VALUES (%s,%s,%s) ON CONFLICT DO NOTHING", labels)

conn.commit()
print(f"Inserted {len(rows)} feature rows and {len(labels)} labels.")
conn.close()
```

Run:

```bash
docker compose exec client python /app/seed.py
```

### Step 3: The leaky query (the bug)

Create `client/leaky.py`:

```python
import os, psycopg2
PG = dict(host=os.environ["PG_HOST"], port=os.environ["PG_PORT"],
          user=os.environ["PG_USER"], password=os.environ["PG_PASSWORD"],
          dbname=os.environ["PG_DB"])
conn = psycopg2.connect(**PG); cur = conn.cursor()

# WRONG: picks the LATEST feature, even if it's from the future.
cur.execute("""
    SELECT l.entity_id, l.event_timestamp AS label_ts,
           f.event_timestamp AS feat_ts, f.feature_name, f.feature_value
    FROM labels l
    JOIN LATERAL (
        SELECT feature_name, feature_value, event_timestamp
        FROM feature_values
        WHERE entity_id = l.entity_id
        ORDER BY event_timestamp DESC
        LIMIT 2
    ) f ON TRUE
    ORDER BY l.entity_id, f.feature_name, f.event_timestamp DESC;
""")
for r in cur.fetchall(): print(r)
conn.close()
```

Run:

```bash
docker compose exec client python /app/leaky.py
```

You will see `feat_ts` values that are **after** `label_ts` — that is leakage. The model would be training on data from the future.

### Step 4: The fix — point-in-time join

Create `client/pitc.py`:

```python
import os, psycopg2
PG = dict(host=os.environ["PG_HOST"], port=os.environ["PG_PORT"],
          user=os.environ["PG_USER"], password=os.environ["PG_PASSWORD"],
          dbname=os.environ["PG_DB"])
conn = psycopg2.connect(**PG); cur = conn.cursor()

# CORRECT: only features with event_timestamp <= label_ts.
cur.execute("""
    SELECT l.entity_id, l.event_timestamp AS label_ts,
           f.event_timestamp AS feat_ts, f.feature_name, f.feature_value
    FROM labels l
    JOIN LATERAL (
        SELECT feature_name, feature_value, event_timestamp
        FROM feature_values
        WHERE entity_id = l.entity_id
          AND event_timestamp <= l.event_timestamp
        ORDER BY event_timestamp DESC
        LIMIT 2
    ) f ON TRUE
    ORDER BY l.entity_id, f.feature_name;
""")
for r in cur.fetchall(): print(r)
conn.close()
```

Run:

```bash
docker compose exec client python /app/pitc.py
```

Now every `feat_ts` is **on or before** `label_ts`. That is the PITC rule.

### Step 5: Materialize (offline -> online)

Create `client/materialize.py`:

```python
import os, json
from datetime import datetime, timezone
import psycopg2, redis

PG = dict(host=os.environ["PG_HOST"], port=os.environ["PG_PORT"],
          user=os.environ["PG_USER"], password=os.environ["PG_PASSWORD"],
          dbname=os.environ["PG_DB"])
r = redis.Redis(host=os.environ["REDIS_HOST"],
                port=int(os.environ["REDIS_PORT"]), decode_responses=True)

conn = psycopg2.connect(**PG); cur = conn.cursor()
cur.execute("""
    SELECT entity_id, feature_name, feature_value, event_timestamp
    FROM (
        SELECT *, ROW_NUMBER() OVER (PARTITION BY entity_id, feature_name
                                     ORDER BY event_timestamp DESC) AS rn
        FROM feature_values
    ) t WHERE rn = 1;
""")
now_iso = datetime.now(timezone.utc).isoformat()
n = 0
for eid, fname, fval, fts in cur.fetchall():
    r.hset(f"features:{eid}", fname, json.dumps({
        "value": fval, "event_timestamp": fts.isoformat(),
        "materialized_at": now_iso,
    }))
    n += 1
print(f"Materialized {n} features into Redis.")
conn.close()
```

Run:

```bash
docker compose exec client python /app/materialize.py
```

### Step 6: Online read + freshness check

Create `client/online.py`:

```python
import os, json, time, redis
r = redis.Redis(host=os.environ["REDIS_HOST"],
                port=int(os.environ["REDIS_PORT"]), decode_responses=True)

eid = "alice"
t0 = time.perf_counter()
blob = r.hgetall(f"features:{eid}")
ms = (time.perf_counter() - t0) * 1000

print(f"Online read for {eid}: {ms:.2f} ms")
for k, v in blob.items():
    p = json.loads(v)
    print(f"  {k:15s} value={p['value']}  feat_ts={p['event_timestamp']}  mat_ts={p['materialized_at']}")
```

Run:

```bash
docker compose exec client python /app/online.py
```

You should see sub-millisecond to single-digit-millisecond latency. The gap between `feat_ts` and `mat_ts` is your **freshness window**.

## Verification

```bash
# Postgres has data
docker compose exec postgres psql -U fsuser -d feast_offline -c "SELECT COUNT(*) FROM feature_values;"
# Expected: 30  (3 users * 5 days * 2 features)

# PITC fix returns no future features
docker compose exec client python /app/pitc.py
# Expected: every feat_ts <= label_ts

# Redis has the materialized features
docker compose exec redis redis-cli HGETALL features:alice
# Expected: 2 fields
```

## Testing

### Test 1: Leakage is real
```bash
docker compose exec postgres psql -U fsuser -d feast_offline -c "
SELECT COUNT(*) FROM labels l
JOIN feature_values f ON f.entity_id = l.entity_id
WHERE f.event_timestamp > l.event_timestamp;"
```
Expected: non-zero. That is the bug.

### Test 2: PITC fix gives zero leakage
```bash
docker compose exec postgres psql -U fsuser -d feast_offline -c "
SELECT COUNT(*) FROM labels l
JOIN LATERAL (
    SELECT 1 FROM feature_values
    WHERE entity_id = l.entity_id AND event_timestamp > l.event_timestamp
    LIMIT 1
) f ON TRUE;"
```
Expected: zero. Bug fixed.

### Test 3: Materialize is idempotent
```bash
docker compose exec client python /app/materialize.py
docker compose exec client python /app/materialize.py
docker compose exec redis redis-cli HGET features:alice tx_count_7d
```
Expected: same value, no duplicates.

## Troubleshooting

- **Connection refused to Postgres/Redis**: wait a few seconds and `docker compose ps` — they should be `(healthy)`.
- **`0 rows inserted`**: you forgot to wait for Postgres. Check `docker compose logs postgres`.
- **online.py shows nothing**: make sure `materialize.py` ran first.

## Cleanup

```bash
docker compose down -v
cd .. && rm -rf fs-easy
```

No cloud bill — everything was local.

## Epilogue

You just built the smallest possible feature store: two tables in Postgres, two `HGETALL`s in Redis, and one Python script that bridges them. The three ideas — **offline/online split**, **point-in-time correctness**, **freshness** — are exactly the same ideas inside every managed feature store (Feast, Tecton, Vertex, SageMaker). The mechanics you learned here transfer directly.

## What You Learned

- Offline store = history. Online store = latest snapshot, low-latency lookups.
- A naive "join the latest feature" leaks future data.
- Adding `AND event_timestamp <= label_ts` fixes it (PITC).
- Materialize copies the latest snapshot per entity into the online store.
- Freshness = the gap between when a feature was generated and when it was served.

## Next Steps

- **Lab 7.2**: do the same thing with Feast and see how it packages these exact ideas.
- Run `materialize.py` on a timer and watch the freshness number shrink.
- Swap Redis for an in-memory Python dict for an even smaller version of the toy.

## Additional Resources

- Feast docs: <https://docs.feast.dev/>
- "What is a feature store?" (Tecton): <https://www.tecton.ai/blog/what-is-a-modern-feature-store/>

## Conclusion

This lab showed the three ideas behind every feature store — offline/online split, point-in-time correctness, and freshness — using the smallest possible stack: 2 tables, 2 stores, 4 Python scripts. Once you understand this, the production systems are just a polished version of the same pattern.
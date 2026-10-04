# Lab 7.1: Feature Store Concepts

## Introduction

Feature stores have become a foundational component of modern machine learning systems, addressing one of the most persistent pain points in ML operations: the consistent, reliable, and timely delivery of features across training and serving environments. As ML systems scale beyond a single notebook into production pipelines serving hundreds of models, the question of where features live, how they are computed, and how they are served at low latency becomes critical. A feature store is a centralized system that decouples feature engineering from model code, allowing data scientists to define features once and reuse them across many models and use cases.

This lab is a beginner-friendly, hands-on introduction to the three core ideas that every practitioner must internalize: the **offline/online store split**, **point-in-time correctness (PITC)**, and **feature freshness**. Rather than abstract whiteboard sketches, you will run a small local stack with a real PostgreSQL offline store, a real Redis online store, and a Python reference client that writes and reads features. You will reproduce leakage bugs by hand, then fix them with a PITC-aware query, and finally observe end-to-end freshness from batch ingest to online retrieval.

The lab deliberately stays away from heavy cloud infrastructure. Everything runs on your host machine in Docker Compose, so you can focus on the mental model. By the end of the lab, you will be able to explain to a colleague, on a whiteboard, why a naive join between a label table and a feature table produces a leakage model, and what changes when the same feature is materialized into a low-latency online store.

![alt text](<Untitled Diagram-Page-2.drawio.png>)





### Architecture Explanation

The stack is intentionally minimal. Everything runs on your host machine in Docker Compose so you can focus on the mental model rather than cloud plumbing. The host machine hosts three containers: a Python client (the whiteboard driver that you interact with), a PostgreSQL container acting as the offline feature store, and a Redis container acting as the online feature store.

The Python client is the only actor you write code in. It performs three roles: it acts as a batch writer that ingests historical feature rows into PostgreSQL, it acts as a PITC-aware trainer that pulls historical features with an ASOF query, and it acts as a low-latency online reader that issues `GET entity_id` calls to Redis. The ingest job is a separate conceptual step (a small script, also in the client container) that simulates the materialize step: it reads the latest snapshot per entity from PostgreSQL and pushes it to Redis. This mirrors what a real feature store like Feast does with `feast materialize-incremental`.

Connectivity is unidirectional and explicit: the client writes to and reads from both stores; the materialize step bridges the offline store to the online store; nothing in PostgreSQL or Redis talks to anything else. There are no managed AWS resources in this lab, so the default region note is satisfied by using `ap-southeast-1` only as the host's region (your local laptop) and treating the Docker network as the equivalent of a private VPC.

## Learning Objectives

By the end of this lab you will be able to:

- Draw, on a whiteboard, the offline/online store split and explain why both exist.
- Define a feature entity, a feature view, and a feature value with explicit `event_timestamp` columns.
- Reproduce a feature leakage bug using a naive inner join between labels and features.
- Fix the leakage using a point-in-time ASOF JOIN that respects the label's `event_timestamp`.
- Run a materialize step that pushes the latest snapshot per entity from PostgreSQL to Redis.
- Measure end-to-end feature freshness and online retrieval latency.
- Reason about staleness budgets (seconds vs minutes vs hours) for different feature types.

## Prerequisites

- A host machine with Docker Engine 24+ and Docker Compose v2 installed.
- Python 3.10+ available locally for running the client scripts outside the container, or you can exec into the client container.
- `curl` and `psql` (optional, for manual verification).
- Familiarity with basic SQL: `SELECT`, `JOIN`, `GROUP BY`, `WHERE`.
- Familiarity with running Docker Compose stacks locally.
- Region: `ap-southeast-1` (Asia Pacific, Singapore). The lab runs locally on your host machine in Docker, so the AWS region only matters if you later decide to swap local Postgres/Redis for managed RDS/ElastiCache. The Docker network acts as a private VPC equivalent.

## Prologue

Imagine you are a data scientist at a fintech. You trained a fraud detection model in a notebook. It worked great offline. Six months into serving, the model's accuracy has silently degraded. When you debug, you realize that during training you joined the label table with the latest feature snapshot for each user, which means the model saw future information. This is the textbook **feature leakage** problem, and it is one of the three things a feature store is supposed to prevent.

In this lab you will build a tiny feature store from scratch, on your laptop, in one afternoon. You will reproduce the leakage, fix it, and end with a working offline/online split you can show your team on a whiteboard.

## Step-by-Step Implementation

### Step 1: Create the project skeleton

```bash
mkdir feature-store-concepts && cd feature-store-concepts
mkdir -p sql client
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
    volumes:
      - ./sql/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
      - pgdata:/var/lib/postgresql/data
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

volumes:
  pgdata:
```

### Step 2: Define the offline schema

Create `sql/init.sql`:

```sql
CREATE TABLE entity_registry (
    entity_id   TEXT PRIMARY KEY,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE feature_definitions (
    feature_name TEXT PRIMARY KEY,
    dtype        TEXT NOT NULL,
    description  TEXT
);

CREATE TABLE feature_values (
    entity_id      TEXT        NOT NULL,
    feature_name   TEXT        NOT NULL,
    feature_value  DOUBLE PRECISION NOT NULL,
    event_timestamp TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (entity_id, feature_name, event_timestamp)
);

CREATE INDEX ix_feature_values_entity_time
    ON feature_values (entity_id, feature_name, event_timestamp DESC);

CREATE TABLE labels (
    entity_id      TEXT NOT NULL,
    label          INT  NOT NULL,
    event_timestamp TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (entity_id, event_timestamp)
);
```

### Step 3: Install Python client dependencies

Create `client/requirements.txt`:

```
psycopg2-binary==2.9.9
redis==5.0.4
```

Install inside the running client container:

```bash
docker compose up -d
docker compose exec client pip install -r /app/requirements.txt
```

### Step 4: Seed entities, features, and labels

Create `client/seed.py`:

```python
import os, random
from datetime import datetime, timedelta, timezone
import psycopg2

PG = dict(
    host=os.environ["PG_HOST"], port=int(os.environ["PG_PORT"]),
    user=os.environ["PG_USER"], password=os.environ["PG_PASSWORD"],
    dbname=os.environ["PG_DB"],
)

FEATURES = [
    ("user_30d_tx_count", "count",   "Rolling 30-day transaction count"),
    ("user_avg_tx_amount", "amount", "Average transaction amount"),
    ("user_failed_login_24h", "count", "Failed logins in last 24h"),
]

now = datetime.now(timezone.utc)
conn = psycopg2.connect(**PG)
cur = conn.cursor()

# entities
entities = [f"user_{i:04d}" for i in range(50)]
cur.executemany("INSERT INTO entity_registry(entity_id) VALUES (%s) ON CONFLICT DO NOTHING",
                [(e,) for e in entities])

# feature definitions
cur.executemany("INSERT INTO feature_definitions VALUES (%s,%s,%s) ON CONFLICT DO NOTHING",
                FEATURES)

# historical feature values: 30 days of daily snapshots per entity
rows = []
for e in entities:
    base_count   = random.randint(10, 200)
    base_amount  = random.uniform(20, 500)
    base_fail    = random.randint(0, 5)
    for d in range(30):
        ts = now - timedelta(days=29 - d)
        rows.append((e, "user_30d_tx_count",  base_count   + d + random.randint(-3, 3), ts))
        rows.append((e, "user_avg_tx_amount", base_amount  + random.uniform(-10, 10),    ts))
        rows.append((e, "user_failed_login_24h", max(0, base_fail + random.randint(-1, 1)), ts))

cur.executemany(
    "INSERT INTO feature_values(entity_id, feature_name, feature_value, event_timestamp) "
    "VALUES (%s,%s,%s,%s) ON CONFLICT DO NOTHING",
    rows,
)

# labels: one per entity, dated 5 days ago (so leakage is possible if we naively join "latest")
labels = []
for e in entities:
    labels.append((e, random.randint(0, 1), now - timedelta(days=5)))

cur.executemany("INSERT INTO labels VALUES (%s,%s,%s) ON CONFLICT DO NOTHING", labels)

conn.commit()
print(f"Seeded {len(entities)} entities, {len(rows)} feature rows, {len(labels)} labels.")
conn.close()
```

Run it:

```bash
docker compose exec client python /app/seed.py
```

### Step 5: Reproduce the leakage bug (naive join)

Create `client/leaky_join.py`:

```python
import os, psycopg2
PG = dict(host=os.environ["PG_HOST"], port=int(os.environ["PG_PORT"]),
          user=os.environ["PG_USER"], password=os.environ["PG_PASSWORD"],
          dbname=os.environ["PG_DB"])
conn = psycopg2.connect(**PG); cur = conn.cursor()

# WRONG: this picks the *latest* feature snapshot per entity, regardless of label time.
cur.execute("""
    SELECT l.entity_id, l.event_timestamp AS label_ts,
           f.event_timestamp AS feat_ts,
           f.feature_name, f.feature_value
    FROM labels l
    JOIN LATERAL (
        SELECT feature_name, feature_value, event_timestamp
        FROM feature_values
        WHERE entity_id = l.entity_id
        ORDER BY event_timestamp DESC
        LIMIT 3
    ) f ON TRUE
    WHERE l.entity_id = 'user_0001'
    ORDER BY f.feature_name, f.event_timestamp DESC;
""")
for row in cur.fetchall():
    print(row)
conn.close()
```

Run it:

```bash
docker compose exec client python /app/leaky_join.py
```

You will see feature timestamps that are **after** the label timestamp (today vs. 5 days ago). Any model trained on this would be using future information at training time.

### Step 6: Fix it with a point-in-time ASOF JOIN

Create `client/pitc_join.py`:

```python
import os, psycopg2
PG = dict(host=os.environ["PG_HOST"], port=int(os.environ["PG_PORT"]),
          user=os.environ["PG_USER"], password=os.environ["PG_PASSWORD"],
          dbname=os.environ["PG_DB"])
conn = psycopg2.connect(**PG); cur = conn.cursor()

# CORRECT: pick the most recent feature snapshot whose event_timestamp <= label_ts.
cur.execute("""
    WITH label AS (
        SELECT entity_id, event_timestamp AS label_ts, label
        FROM labels
        WHERE entity_id = 'user_0001'
    )
    SELECT l.entity_id, l.label_ts, l.label,
           f.feature_name, f.feature_value, f.event_timestamp AS feat_ts
    FROM label l
    JOIN LATERAL (
        SELECT feature_name, feature_value, event_timestamp
        FROM feature_values fv
        WHERE fv.entity_id = l.entity_id
          AND fv.event_timestamp <= l.label_ts
        ORDER BY fv.event_timestamp DESC
        LIMIT 3
    ) f ON TRUE
    ORDER BY f.feature_name;
""")
for row in cur.fetchall():
    print(row)
conn.close()
```

Run it:

```bash
docker compose exec client python /app/pitc_join.py
```

Now every `feat_ts` is on or before `label_ts`. This is the PITC contract: for every training row at time `t`, only features whose information was available at or before `t` are joined in.

### Step 7: Build the materialize step (offline -> online)

Create `client/materialize.py`:

```python
import os, json
from datetime import datetime, timezone
import psycopg2, redis

PG = dict(host=os.environ["PG_HOST"], port=int(os.environ["PG_PORT"]),
          user=os.environ["PG_USER"], password=os.environ["PG_PASSWORD"],
          dbname=os.environ["PG_DB"])

r_client = redis.Redis(host=os.environ["REDIS_HOST"],
                       port=int(os.environ["REDIS_PORT"]), decode_responses=True)

conn = psycopg2.connect(**PG); cur = conn.cursor()

cur.execute("""
    SELECT entity_id, feature_name, feature_value, event_timestamp
    FROM (
        SELECT entity_id, feature_name, feature_value, event_timestamp,
               ROW_NUMBER() OVER (PARTITION BY entity_id, feature_name
                                  ORDER BY event_timestamp DESC) AS rn
        FROM feature_values
    ) t WHERE rn = 1;
""")

now_iso = datetime.now(timezone.utc).isoformat()
n_features = 0
for entity_id, fname, fvalue, fts in cur.fetchall():
    payload = {
        "value": fvalue,
        "event_timestamp": fts.isoformat(),
        "materialized_at": now_iso,
    }
    r_client.hset(f"features:{entity_id}", fname, json.dumps(payload))
    n_features += 1

print(f"Materialized {n_features} features into Redis.")
conn.close()
```

Run it:

```bash
docker compose exec client python /app/materialize.py
```

### Step 8: Online read with latency measurement

Create `client/online_read.py`:

```python
import os, json, time, redis
r = redis.Redis(host=os.environ["REDIS_HOST"],
                port=int(os.environ["REDIS_PORT"]), decode_responses=True)

entity_id = "user_0001"
t0 = time.perf_counter()
blob = r.hgetall(f"features:{entity_id}")
latency_ms = (time.perf_counter() - t0) * 1000

print(f"Online read latency for {entity_id}: {latency_ms:.2f} ms")
for k, v in blob.items():
    payload = json.loads(v)
    print(f"  {k:25s} value={payload['value']:.3f}  "
          f"feat_ts={payload['event_timestamp']}  "
          f"mat_ts={payload['materialized_at']}")
```

Run it:

```bash
docker compose exec client python /app/online_read.py
```

You should see latencies well under 10 ms on a laptop, and you should see `mat_ts` being later than `feat_ts`. That gap is your **freshness** budget.

### Step 9: Whiteboard summary

Open a text editor (or paper) and draw:

```
          OFFLINE STORE                ONLINE STORE
       (PostgreSQL: history)        (Redis: latest only)

  feature_values  ───materialize──▶   hash features:<entity_id>
   (entity, name,                 (entity, name, latest snapshot
    value, event_ts)                value, materialized_at)

       │                                    │
       │  PITC ASOF JOIN                    │  GET <10ms
       │  (training)                        │  (serving)
       ▼                                    ▼
    Model.fit()                     Model.predict()
```

This is the diagram you should be able to draw from memory after the lab.

## Verification

Run each of these and confirm the expected output:

```bash
# 1. Postgres is reachable and schema is loaded
docker compose exec postgres psql -U fsuser -d feast_offline -c "\dt"
# Expected: 4 tables listed

# 2. Seed data exists
docker compose exec postgres psql -U fsuser -d feast_offline \
  -c "SELECT COUNT(*) FROM feature_values;"
# Expected: 4500 (50 entities * 30 days * 3 features)

# 3. PITC query returns no future features
docker compose exec client python /app/pitc_join.py
# Expected: every row's feat_ts <= label_ts

# 4. Redis has materialized features
docker compose exec redis redis-cli HGETALL features:user_0001
# Expected: 3 fields (one per feature), each a JSON payload

# 6. Latency is sub-10ms
docker compose exec client python /app/online_read.py
# Expected: "Online read latency ... < 10.00 ms"
```

## Testing

### Test 1: Leakage is real

```bash
docker compose exec postgres psql -U fsuser -d feast_offline -c "
SELECT l.entity_id, l.event_timestamp AS label_ts,
       (SELECT MAX(event_timestamp) FROM feature_values WHERE entity_id = l.entity_id) AS latest_feat_ts
FROM labels l
WHERE l.entity_id = 'user_0001';"
```

Expected: `latest_feat_ts` is strictly greater than `label_ts`. This proves the naive join leaks.

### Test 2: PITC fix removes leakage

```bash
docker compose exec postgres psql -U fsuser -d feast_offline -c "
SELECT COUNT(*) AS leaky_rows
FROM labels l
JOIN feature_values f
  ON f.entity_id = l.entity_id
 AND f.event_timestamp > l.event_timestamp;"
```

Expected: a non-zero count for `leaky_rows` if you do not constrain time, zero for the PITC version.

### Test 3: Materialize idempotency

```bash
docker compose exec client python /app/materialize.py
docker compose exec client python /app/materialize.py
docker compose exec redis redis-cli HGET features:user_0001 user_30d_tx_count
```

Expected: running materialize twice does not duplicate keys; the latest snapshot wins.

### Test 4: Freshness under 5 seconds

```bash
START=$(date +%s%3N)
docker compose exec client python /app/materialize.py >/dev/null
docker compose exec client python /app/online_read.py
END=$(date +%s%3N)
echo "End-to-end freshness window: $((END-START)) ms"
```

Expected: the window is dominated by Docker exec startup, but the actual `online_read` line should be under 10 ms.

## Troubleshooting

**1. `psycopg2.OperationalError: could not connect to server`**

The Postgres container is not ready yet. Run `docker compose ps` and wait for `postgres` to show `(healthy)`. Increase the healthcheck retries in `docker-compose.yml` if your machine is slow.

**2. `redis.exceptions.ConnectionError: Error 111 connecting to redis:6379`**

The Redis container exited. Run `docker compose logs redis` to inspect. On macOS/Windows, ensure Docker Desktop is running and the VM has at least 1 GB of memory allocated.

**3. `seed.py` reports `0 rows inserted` for feature_values**

Your entities were created but the executemany silently no-op'd. Check that the timestamp column accepts `timestamptz` and that you are passing timezone-aware datetimes. Re-run after `docker compose down -v` to wipe the volume.

**4. `materialize.py` writes but online_read shows nothing**

You probably ran `online_read.py` against a different entity_id. Confirm with `docker compose exec redis redis-cli KEYS 'features:*'`. The materialize script iterates over all of them.

**6. Latency is 80 ms instead of <10 ms**

This is the cold path of `docker exec`. The actual Redis `HGETALL` itself is sub-millisecond; the 80 ms is mostly Python interpreter startup inside the container. For real numbers, run `online_read.py` in a loop and report the median.

**7. `permission denied` on `pgdata` volume**

On Linux hosts, run `sudo chown -R 999:999 ./pgdata` or remove the named volume with `docker compose down -v` before restarting.

## Cleanup

Run these commands in order to stop the stack and free disk space:

```bash
# Stop containers and remove the named volume (wipes Postgres data)
docker compose down -v

# Remove the project directory
cd .. && rm -rf feature-store-concepts
```

There is no cloud billing in this lab: all resources are local Docker containers on your host machine. Once the stack is down, you owe nothing.

## Epilogue

You built a two-store feature system from scratch on your laptop. You reproduced the textbook leakage bug, fixed it with a PITC ASOF JOIN, materialized features from PostgreSQL into Redis, and measured online latency. You also produced the whiteboard diagram you should be able to redraw for any interview or design review.

The bigger picture is that every production feature store (Feast, Tecton, Hopsworks, Vertex Feature Store, SageMaker Feature Store) is a richer, managed version of what you just built: an offline store, an online store, a materialize step, and a PITC contract. The mechanics you learned here transfer directly into those systems.

## Principles

- **Separation of concerns**: the offline store is optimized for full-history scans; the online store is optimized for point lookups. One system cannot do both well.
- **Time as a first-class dimension**: every feature row carries `event_timestamp`, and every join respects it. This is the only durable defense against leakage.
- **Idempotent materialize**: the bridge between offline and online must be re-runnable without producing duplicate or stale keys.
- **Freshness is a budget, not a number**: you choose seconds, minutes, or hours per feature based on cost and downstream impact.
- **Whiteboard-first design**: if you cannot draw the system on a whiteboard, you do not understand it yet.
- **Local before cloud**: every production feature store starts as a local prototype. This lab is that prototype.

## What You Learned

- The three pillars of feature store design: offline/online split, PITC, freshness.
- How to encode an `event_timestamp` on each feature row and use it in a `JOIN LATERAL ... ORDER BY event_timestamp DESC LIMIT 1 WHERE event_timestamp <= label_ts` pattern.
- How to reproduce and then fix feature leakage with a real SQL example.
- How a materialize step pushes the latest snapshot per entity from PostgreSQL into Redis.
- How to measure online retrieval latency and freshness on a laptop.
- The shape of the canonical feature-store whiteboard diagram.

## Next Steps

- **Lab 7.2**: replace the hand-written stack with Feast. Install Feast, write a `feature_store.yaml`, and apply a feature definition. You will see the same concepts packaged in a real feature store.
- **Add TTL**: extend `materialize.py` to write a TTL on each Redis hash, then watch entries expire and observe how the system handles staleness.
- **Add a streaming source**: pipe Kafka events into the offline store via a background worker, then materialize more frequently to shrink the freshness window.
- **Wire it to a model**: load the PITC-joined features into scikit-learn and train a tiny classifier. Compare AUC between leaky and PITC versions to see the leakage impact numerically.
- **Swap local Postgres for S3 + Athena and local Redis for ElastiCache** to convert the local stack into a cloud-native stack on AWS `ap-southeast-1`.

## Additional Resources

- Feast documentation: <https://docs.feast.dev/>
- Google Cloud reference on point-in-time correctness: <https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning#feature_store>
- "The Modern Feature Store" (Tecton blog): <https://www.tecton.ai/blog/what-is-a-modern-feature-store/>
- Redis HASH commands: <https://redis.io/commands/hset/>
- PostgreSQL `JOIN LATERAL`: <https://www.postgresql.org/docs/current/queries-lateral.html>
- Poridhi Labs, Module 7: Feature Stores (overview)

## Conclusion

This lab introduced the three ideas that every practitioner must internalize before adopting a production feature store: the offline/online split, point-in-time correctness, and feature freshness. You built a minimal two-store stack on your laptop using PostgreSQL as the offline store and Redis as the online store, reproduced a leakage bug, fixed it with a PITC ASOF JOIN, and verified the online path with a materialize step. The takeaway: the offline/online split, a strict time-aware join, and a freshness budget are the foundation that every managed feature store inherits. Carry that whiteboard into Lab 7.2, where you will reproduce the same architecture using a real framework.
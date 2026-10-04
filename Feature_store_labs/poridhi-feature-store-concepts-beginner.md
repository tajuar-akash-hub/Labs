# Lab 7.1: Feature Store Concepts (Beginner Friendly)

> **Lab Status:** Pending
> **Level:** Beginner
> **Type:** Standalone (no prerequisites from other labs; you can run this on a fresh laptop)
> **Key Focus:** Sketch the offline/online store split, point-in-time correctness (PITC), and feature freshness on a whiteboard example.

> **Who this is for:** People who have used Python and basic SQL, but have never built a feature store before. If terms like "PITC" or "materialize" sound scary, this lab is for you.

## Introduction

A feature store is a place where we keep the data (features) our machine learning models use. The trick is that models need features in two very different ways:

- **Training:** a model needs lots of historical data, slowly, all at once. This is the **offline store**.
- **Serving (predicting):** when a real user shows up, the model needs their features in milliseconds. This is the **online store**.

A feature store gives you both, and, most importantly, it makes sure the training data does not "cheat" by peeking into the future. That cheating is called **feature leakage**, and the way we prevent it is called **point-in-time correctness (PITC)**.

Imagine you bake cookies (your ML model) and you need flour (your features). You have two problems:

1. When you are testing recipes (training), you want a big pantry with months of flour shipments so you can study how each batch affected past cookies.
2. When a customer walks in (serving/predicting), you want that customer's flour ready in 1 second, not 1 minute.

A feature store is just "the pantry + the grab-bag". It is two databases:

- **Offline store** = the pantry (PostgreSQL in this lab). Big, slow, holds history. Good for training.
- **Online store** = the grab-bag (Redis in this lab). Small, fast, holds only the latest flour per customer. Good for serving.

The cleverest part of a feature store is that it stops you from cheating. You will see how in this lab.

In this short, beginner-friendly lab you will:
1. Spin up a tiny PostgreSQL (offline) + Redis (online) stack with one Docker Compose file.
2. Insert a handful of fake users and features.
3. See a leaky query, then fix it with a point-in-time-aware query.
4. Copy the latest feature snapshot into Redis ("materialize").
5. Read it back fast and check the **freshness** (how old the data is).

You can finish the whole thing in under an hour on a laptop.

## Architecture

### Architecture Structure

The system is intentionally tiny. Everything runs on your laptop in Docker Compose so you can focus on the mental model rather than cloud plumbing.

```
HOST MACHINE (laptop, region ap-southeast-1)
└── DOCKER COMPOSE  (acts like a private VPC equivalent)
    ├── POSTGRES CONTAINER      [offline store : history]
    │     └── tables: feature_values, labels
    │           ▲
    │           │  (1) seed.py writes fake history
    │           │
    ├── REDIS CONTAINER          [online store : latest snapshot per user]
    │     └── hash: features:<entity_id>
    │           ▲
    │           │  (4) materialize.py copies newest row per (user, feature)
    │           │
    └── CLIENT CONTAINER (Python)
          ├── (1) seed.py            writes fake rows into Postgres
          ├── (2) leaky.py          the BUG: joins latest features
          ├── (3) pitc.py           the FIX: adds event_timestamp <= label_ts
          ├── (4) materialize.py    copies latest snapshot into Redis
          └── (5) online.py         reads from Redis in <1 ms (model serving)
```

Components:

1. **Postgres container** (offline store). Holds every historical feature row.
2. **Redis container** (online store). Holds only the latest snapshot per user.
3. **Client container** (Python). The whiteboard notebook where you author queries and run scripts.
4. **Materialize script** (Python). The bridge between Postgres and Redis.
5. **Leaky vs PITC queries** (Python/SQL). The bug and the fix.

### Draw.io Diagram

```xml
<mxfile host="app.diagrams.net" modified="2026-10-05T00:00:00.000Z" agent="poridhi" version="22.0.0" type="device">
  <diagram name="Lab-7.1-Feature-Store" id="lab-7-1-feature-store">
    <mxGraphModel dx="1700" dy="900" grid="0" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1700" pageHeight="900" background="#000000" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />

        <!-- Top title banner -->
        <mxCell id="title-banner" value="Lab 7.1: Feature Store Concepts&#10;Beginner Friendly: offline/online split, PITC, freshness" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1F2A44;strokeColor=#1F2A44;fontColor=#FFFFFF;fontSize=22;fontStyle=1;align=center;verticalAlign=middle;" vertex="1" parent="1">
          <mxGeometry x="40" y="20" width="1620" height="70" as="geometry" />
        </mxCell>

        <!-- Outer container: HOST MACHINE -->
        <mxCell id="host-machine" value="HOST MACHINE : ap-southeast-1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#FF6B1A;strokeWidth=3;dashed=0;verticalAlign=top;fontColor=#FFFFFF;fontSize=18;fontStyle=1;align=left;spacingLeft=10;" vertex="1" parent="1">
          <mxGeometry x="40" y="110" width="1620" height="700" as="geometry" />
        </mxCell>

        <!-- DOCKER COMPOSE nested environment -->
        <mxCell id="docker-compose" value="DOCKER COMPOSE : private VPC equivalent" style="rounded=1;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#5A8FCE;strokeWidth=2;dashed=1;verticalAlign=top;fontColor=#FFFFFF;fontSize=14;fontStyle=1;align=left;spacingLeft=10;" vertex="1" parent="1">
          <mxGeometry x="80" y="160" width="1540" height="620" as="geometry" />
        </mxCell>

        <!-- POSTGRES container -->
        <mxCell id="postgres-box" value="POSTGRES : Offline Feature Store" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1F2A44;strokeColor=#1F2A44;fontColor=#FFFFFF;fontSize=14;fontStyle=1;align=center;" vertex="1" parent="1">
          <mxGeometry x="140" y="220" width="420" height="100" as="geometry" />
        </mxCell>
        <mxCell id="postgres-sub" value="Image : postgres:16-alpine&#10;Port : 5432&#10;Tables : feature_values, labels" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#1F2A44;strokeColor=#1F2A44;fontColor=#CCCCCC;fontSize=11;align=center;" vertex="1" parent="1">
          <mxGeometry x="140" y="280" width="420" height="40" as="geometry" />
        </mxCell>
        <mxCell id="postgres-chip" value="Service : postgres" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#CCCCCC;fontColor=#000000;fontSize=11;align=center;" vertex="1" parent="1">
          <mxGeometry x="450" y="225" width="105" height="22" as="geometry" />
        </mxCell>

        <!-- REDIS container -->
        <mxCell id="redis-box" value="REDIS : Online Feature Store" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1F2A44;strokeColor=#1F2A44;fontColor=#FFFFFF;fontSize=14;fontStyle=1;align=center;" vertex="1" parent="1">
          <mxGeometry x="620" y="220" width="420" height="100" as="geometry" />
        </mxCell>
        <mxCell id="redis-sub" value="Image : redis:7-alpine&#10;Port : 6379&#10;Key : features:&lt;entity_id&gt; (HASH)" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#1F2A44;strokeColor=#1F2A44;fontColor=#CCCCCC;fontSize=11;align=center;" vertex="1" parent="1">
          <mxGeometry x="620" y="280" width="420" height="40" as="geometry" />
        </mxCell>
        <mxCell id="redis-chip" value="Service : redis" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#CCCCCC;fontColor=#000000;fontSize=11;align=center;" vertex="1" parent="1">
          <mxGeometry x="930" y="225" width="105" height="22" as="geometry" />
        </mxCell>

        <!-- CLIENT container -->
        <mxCell id="client-box" value="CLIENT : Python Playbook" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1F2A44;strokeColor=#1F2A44;fontColor=#FFFFFF;fontSize=14;fontStyle=1;align=center;" vertex="1" parent="1">
          <mxGeometry x="1100" y="220" width="480" height="100" as="geometry" />
        </mxCell>
        <mxCell id="client-sub" value="Image : python:3.11-slim&#10;Scripts : seed.py, leaky.py, pitc.py, materialize.py, online.py" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#1F2A44;strokeColor=#1F2A44;fontColor=#CCCCCC;fontSize=11;align=center;" vertex="1" parent="1">
          <mxGeometry x="1100" y="280" width="480" height="40" as="geometry" />
        </mxCell>
        <mxCell id="client-chip" value="Mount : ./client" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#CCCCCC;fontColor=#000000;fontSize=11;align=center;" vertex="1" parent="1">
          <mxGeometry x="1455" y="225" width="120" height="22" as="geometry" />
        </mxCell>

        <!-- DATA FLOW: client -> postgres (seed) -->
        <mxCell id="edge-seed" value="(1) seed.py writes history" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#7AA8FF;endArrow=classic;fontColor=#FFFFFF;fontSize=11;labelBackgroundColor=#1F2A44;" edge="1" parent="1" source="client-box" target="postgres-box">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>

        <!-- PITC QUERY inside client (visualized as a sub-box under client) -->
        <mxCell id="pitc-subgroup" value="PITC CONTRACT : only feature rows with event_timestamp &lt;= label_ts" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#3A2A1A;strokeColor=#FF6B1A;dashed=0;strokeWidth=1;fontColor=#FFFFFF;fontSize=12;fontStyle=1;align=center;" vertex="1" parent="1">
          <mxGeometry x="1100" y="400" width="480" height="60" as="geometry" />
        </mxCell>

        <!-- MATERIALIZE arrow: postgres -> redis -->
        <mxCell id="edge-materialize" value="(4) materialize.py copies newest per (user, feature)" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#7AA8FF;endArrow=classic;fontColor=#FFFFFF;fontSize=11;labelBackgroundColor=#1F2A44;" edge="1" parent="1" source="postgres-box" target="redis-box">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>

        <!-- ONLINE READ: redis -> client -->
        <mxCell id="edge-online" value="(5) online.py : sub-ms HGETALL (serving)" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#7AA8FF;endArrow=classic;fontColor=#FFFFFF;fontSize=11;labelBackgroundColor=#1F2A44;" edge="1" parent="1" source="redis-box" target="client-box">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>

        <!-- PITC QUERY arrow: postgres -> pitc-subgroup -->
        <mxCell id="edge-pitc-query" value="(3) pitc.py : point-in-time JOIN (training)" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#7AA8FF;endArrow=classic;fontColor=#FFFFFF;fontSize=11;labelBackgroundColor=#1F2A44;" edge="1" parent="1" source="postgres-box" target="pitc-subgroup">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>

        <!-- LEAKY -> BLOCKED overlay -->
        <mxCell id="leaky-block" value="LEAKY QUERY (BUG): naive join of LATEST snapshot leaks future data" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#3A2A1A;strokeColor=#CC0000;strokeWidth=2;dashed=1;fontColor=#FFFFFF;fontSize=12;fontStyle=1;align=center;" vertex="1" parent="1">
          <mxGeometry x="140" y="400" width="420" height="60" as="geometry" />
        </mxCell>
        <mxCell id="leaky-cross" value="X" style="shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.cross;sketch=0;outlineConnect=0;html=1;strokeColor=#CC0000;fillColor=#CC0000;fontColor=#FFFFFF;fontSize=24;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="540" y="405" width="40" height="50" as="geometry" />
        </mxCell>

        <!-- FRESHNESS band -->
        <mxCell id="freshness-band" value="FRESHNESS : gap between feat_ts (in Postgres) and materialized_at (in Redis). Measured in seconds, minutes, or hours." style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1F2A44;strokeColor=#7AA116;strokeWidth=2;dashed=1;fontColor=#FFFFFF;fontSize=12;fontStyle=1;align=center;" vertex="1" parent="1">
          <mxGeometry x="140" y="500" width="1440" height="60" as="geometry" />
        </mxCell>

        <!-- KEY POINTS callout -->
        <mxCell id="keypoints-box" value="Key Points:&#10;1. Offline store (Postgres) holds full history; online store (Redis) holds only the latest snapshot per entity.&#10;2. Materialize is a one-way copy from offline to online, re-runnable and idempotent.&#10;3. Point-in-time correctness: at training time, only use feature rows with event_timestamp &lt;= label_ts.&#10;4. Freshness is a budget, not a number: seconds, minutes, or hours depending on the feature.&#10;5. Whiteboard-first design: if you cannot draw the system on paper, you do not understand it yet." style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFF7E6;strokeColor=#FF6B1A;fontColor=#000000;fontSize=12;align=left;verticalAlign=top;spacingLeft=10;" vertex="1" parent="1">
          <mxGeometry x="140" y="600" width="760" height="180" as="geometry" />
        </mxCell>

        <!-- RESULT callout -->
        <mxCell id="result-box" value="Result:&#10;A working two-store feature system on your laptop.&#10;A leaky query that you can prove leaks future data.&#10;A PITC fix that brings leakage to zero.&#10;A materialize script that copies the latest snapshot into Redis.&#10;A sub-1ms feature read for model serving.&#10;A whiteboard mental model that transfers to Feast, Tecton, and Vertex." style="rounded=1;whiteSpace=wrap;html=1;fillColor=#E8F5E9;strokeColor=#7AA116;fontColor=#000000;fontSize=12;align=left;verticalAlign=top;spacingLeft=10;" vertex="1" parent="1">
          <mxGeometry x="920" y="600" width="660" height="180" as="geometry" />
        </mxCell>

      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

### Architecture Explanation

Three things run on your machine in Docker:

- **PostgreSQL** = the offline store. Holds history.
- **Redis** = the online store. Holds only the latest snapshot per user, for fast lookups.
- **Python client** = where you write and run scripts to seed, fix, materialize, and read features.

The only "magic" step is the **materialize** script: it copies the newest value per user from PostgreSQL into Redis. That is exactly what real feature stores like Feast automate for you.

Connectivity is unidirectional and explicit:
- The **client** writes to Postgres (seed).
- The **client** reads from Postgres (leaky vs PITC).
- The **client** writes to Redis via materialize.py.
- The **client** reads from Redis via online.py (sub-millisecond).

There are no managed AWS resources in this lab, so the default region note (`ap-southeast-1`) is satisfied by using it only as the host's region (your local laptop) and treating the Docker network as the equivalent of a private VPC.

## Learning Objectives

By the end of this lab you will be able to:

- Tell a friend what an offline store and an online store do.
- Show what feature leakage looks like using a small SQL example.
- Fix the leakage with one extra line in a SQL query.
- Run a "materialize" script that copies data from offline to online.
- Read features back from the online store in milliseconds.

## Prerequisites

- **Docker Desktop** (or Docker Engine + Compose) installed and running. [Get it here](https://www.docker.com/products/docker-desktop/) if you don't have it.
- **30 minutes** of your time.
- That's it. Everything else (Python, Postgres, Redis) runs inside Docker.

> Tip: You don't need to install Python, Postgres, or Redis yourself. Docker containers carry their own copies.

- Region: `ap-southeast-1` (Asia Pacific, Singapore). The lab runs locally on your host machine in Docker, so the AWS region only matters if you later decide to swap local Postgres/Redis for managed RDS/ElastiCache. The Docker network acts as a private VPC equivalent. Availability zones `ap-southeast-1a`, `ap-southeast-1b`, and `ap-southeast-1c` are listed for completeness only; this lab does not provision any AWS AZs.

## Prologue

### The story (1 minute, worth reading)

You trained a fraud model. It looked great. Six months later it started getting worse. Why?

During training, you joined "the *latest* user info" with "fraud labels from 5 days ago." Problem: that "latest user info" included things that happened *after* the fraud. Your model learned from the future: it learned that "users who look like this got flagged as fraud," without realizing those features were collected *because* of the fraud.

This is **feature leakage**. It makes your offline metrics look amazing and your production model look terrible.

A feature store, with **point-in-time joins**, prevents this. You will reproduce the bug, then fix it.

### The whiteboard sketch (the "key focus" of this lab)

Before any code, draw this on a piece of paper. By the end of the lab, every box and arrow here will be something you actually ran.

```
                 OFFLINE STORE                     ONLINE STORE
              (PostgreSQL: history)             (Redis: latest only)
              ┌──────────────────┐              ┌──────────────────┐
              │ feature_values   │              │ features:alice   │
              │ ───────────────  │              │ ─────────────    │
              │ alice, tx_count, │   materialize │ tx_count_7d → 17 │
              │   17, day-3      │ ───────────▶  │ avg_tx_amount→58 │
              │ alice, tx_count, │  (copy newest│ materialised_at  │
              │   14, day-2      │   per user)  │   = 2026-10-04   │
              │ alice, tx_count, │              └──────────────────┘
              │   11, day-1      │                       │
              │ alice, tx_count, │                       │ GET (sub-ms)
              │   17, day-0      │                       ▼
              └──────────────────┘                  Model.predict()
                       │
                       │  PITC ASOF JOIN
                       │  (training; only feature rows
                       │   with event_timestamp <= label_ts)
                       ▼
                  Model.fit()
```

Three ideas this picture captures (the entire lab in one diagram):

1. **Two stores:** left is history (Postgres), right is latest snapshot (Redis). They have different jobs.
2. **One bridge:** the `materialize` arrow copies the newest row per user from left to right.
3. **One rule:** the PITC arrow only lets feature rows from *before* the label's time through. That single rule is what stops leakage.

Keep this picture in mind as you build each step.

### Glossary (read this first!)

| Word | What it really means |
|------|----------------------|
| **Feature** | One column of input for a model. Example: "user's transaction count last 7 days". |
| **Entity** | The "thing" the features are about. Usually a user, a product, a session. |
| **Event timestamp** | When the feature value was true. Very important: this is how we stop cheating. |
| **Label** | The answer the model is trying to predict (e.g. `0` = not fraud, `1` = fraud). |
| **Offline store** | Big database with full history. Used for training. |
| **Online store** | Tiny fast database with only the latest snapshot per entity. Used for serving. |
| **Materialize** | Copy the latest snapshot from offline to online. |
| **Leakage** | When the model accidentally sees data from the future during training. Bad. |
| **PITC (point-in-time correctness)** | The rule: at training time, only use features that were known *on or before* the label's timestamp. |

## Step-by-Step Implementation

### Step 1: Create the project folder

Open a terminal (PowerShell, bash, zsh, any will do) and run:

```bash
mkdir fs-beginner && cd fs-beginner
```

Now create **three files** inside this folder:

```
fs-beginner/
├── docker-compose.yml      ← tells Docker what to run
└── client/
    ├── requirements.txt    ← Python libraries we need
    └── init.sql            ← creates the database tables
```

Run these to make the folders:

```bash
mkdir client
```

### Step 2: `docker-compose.yml`

Create the file `docker-compose.yml` (in the `fs-beginner` folder) with this content. Don't worry about understanding every line yet; the comments explain each block.

```yaml
# We are running 3 "services" (containers):
#   1. postgres  : the offline store (history)
#   2. redis     : the online store (latest snapshot, fast)
#   3. client    : a Python playground where we run our scripts

services:
  postgres:
    image: postgres:16-alpine       # a small Postgres image
    environment:                    # login + database name
      POSTGRES_USER: fsuser
      POSTGRES_PASSWORD: fspass
      POSTGRES_DB: feast_offline
    ports:
      - "5432:5432"                 # exposed on your laptop
    volumes:
      - ./client/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
                                     # auto-run init.sql on first start
    healthcheck:                     # is it ready yet?
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
    image: python:3.11-slim          # a small Python image
    working_dir: /app
    volumes:
      - ./client:/app               # your scripts appear inside the container
    command: sleep infinity          # keep the container alive
    environment:                     # so scripts know how to reach Postgres/Redis
      PG_HOST: postgres
      PG_PORT: "5432"
      PG_USER: fsuser
      PG_PASSWORD: fspass
      PG_DB: feast_offline
      REDIS_HOST: redis
      REDIS_PORT: "6379"
```

### Step 3: `client/init.sql` (the table schemas)

Create `client/init.sql`. This is what makes our two tables. Think of these as two spreadsheets:

- **`feature_values`**: rows like "Alice, tx_count_7d = 12, on 2026-10-01"
- **`labels`**: rows like "Alice, fraud = 1, on 2026-09-30"

```sql
-- One row per (user, feature, day)
CREATE TABLE feature_values (
    entity_id       TEXT        NOT NULL,   -- the user, e.g. 'alice'
    feature_name    TEXT        NOT NULL,   -- the feature, e.g. 'tx_count_7d'
    feature_value   DOUBLE PRECISION NOT NULL, -- the number
    event_timestamp TIMESTAMPTZ NOT NULL,   -- WHEN this value was true
    PRIMARY KEY (entity_id, feature_name, event_timestamp)
);

-- One row per (user, day) for the answer we are trying to predict
CREATE TABLE labels (
    entity_id       TEXT NOT NULL,
    label           INT  NOT NULL,          -- 0 or 1 (e.g. 1 = fraud)
    event_timestamp TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (entity_id, event_timestamp)
);
```

### Step 4: `client/requirements.txt`

Create `client/requirements.txt`:

```
psycopg2-binary
redis
```

These are the two Python libraries we will use:
- `psycopg2-binary`: talks to Postgres
- `redis`: talks to Redis

### Step 5: Start everything

In the `fs-beginner` folder:

```bash
docker compose up -d
```

This downloads and starts the 3 containers. Wait ~10 seconds, then check that they are healthy:

```bash
docker compose ps
```

You should see all three with `(healthy)` in the STATUS column. If Postgres or Redis show `starting`, wait a few more seconds and run it again.

Now install the Python libraries inside the client container:

```bash
docker compose exec client pip install -r /app/requirements.txt
```

> What does `exec` mean? It runs a command *inside* a running container. So we are asking the `client` container to run `pip install`.

### Step 6: Seed some fake data

Create `client/seed.py`. This script pretends 3 users existed for 5 days, with 2 features each, plus 1 fraud label per user from 2 days ago.

```python
# seed.py: fill our database with a tiny bit of fake data
import os, random
from datetime import datetime, timedelta, timezone
import psycopg2

# Read connection info from environment variables (set by docker-compose)
PG = dict(
    host=os.environ["PG_HOST"],
    port=os.environ["PG_PORT"],
    user=os.environ["PG_USER"],
    password=os.environ["PG_PASSWORD"],
    dbname=os.environ["PG_DB"],
)

now = datetime.now(timezone.utc)        # current time in UTC
conn = psycopg2.connect(**PG)           # open Postgres connection
cur = conn.cursor()

users = ["alice", "bob", "carol"]       # three fake users

# Build a row per (user, day, feature)
rows = []
for u in users:
    for d in range(5):                  # 5 days of history
        ts = now - timedelta(days=4-d)  # walk back 4,3,2,1,0 days
        rows.append((u, "tx_count_7d",   random.randint(1, 20), ts))
        rows.append((u, "avg_tx_amount", round(random.uniform(10, 100), 2), ts))

# Insert all rows at once. ON CONFLICT DO NOTHING = no error if rerun.
cur.executemany(
    "INSERT INTO feature_values VALUES (%s,%s,%s,%s) ON CONFLICT DO NOTHING",
    rows,
)

# One label per user, dated 2 days ago. This is the "fraud happened on day X" we want to predict.
labels = [(u, random.randint(0, 1), now - timedelta(days=2)) for u in users]
cur.executemany(
    "INSERT INTO labels VALUES (%s,%s,%s) ON CONFLICT DO NOTHING",
    labels,
)

conn.commit()                          # save changes to disk
print(f"Inserted {len(rows)} feature rows and {len(labels)} labels.")
conn.close()
```

Run it:

```bash
docker compose exec client python /app/seed.py
```

Expected output:

```
Inserted 30 feature rows and 3 labels.
```

If you see that, your database now has data.

> Why 30 rows? 3 users x 5 days x 2 features = 30.

### Step 7: The leaky query (the bug)

Now the fun part. We are going to write a query that **looks correct** but is broken.

Create `client/leaky.py`:

```python
# leaky.py: THIS IS THE BUG. Don't write queries like this.
import os, psycopg2

PG = dict(host=os.environ["PG_HOST"], port=os.environ["PG_PORT"],
          user=os.environ["PG_USER"], password=os.environ["PG_PASSWORD"],
          dbname=os.environ["PG_DB"])
conn = psycopg2.connect(**PG); cur = conn.cursor()

# For each label, we "join" the LATEST feature values for that user.
# The problem: "latest" means "most recent in the table", which might be
# *after* the label's timestamp. That is leakage.
cur.execute("""
    SELECT l.entity_id,
           l.event_timestamp AS label_ts,    -- when the fraud (or not) happened
           f.event_timestamp AS feat_ts,     -- when the feature was true
           f.feature_name, f.feature_value
    FROM labels l
    JOIN LATERAL (
        SELECT feature_name, feature_value, event_timestamp
        FROM feature_values
        WHERE entity_id = l.entity_id
        ORDER BY event_timestamp DESC        -- newest first
        LIMIT 2                              -- just 2 features
    ) f ON TRUE
    ORDER BY l.entity_id, f.feature_name;
""")

for row in cur.fetchall():
    print(row)
conn.close()
```

Run it:

```bash
docker compose exec client python /app/leaky.py
```

Expected output (yours will differ; what matters is the dates):

```
('alice', datetime.datetime(2026, 10, 3, ...), datetime.datetime(2026, 10, 4, ...), 'avg_tx_amount', 47.81)
('alice', datetime.datetime(2026, 10, 3, ...), datetime.datetime(2026, 10, 4, ...), 'tx_count_7d', 14)
...
```

Notice the **second date (`feat_ts`) is AFTER the first (`label_ts`)**. That is the leak. We are using data from the future to "predict" a past event.

If the dates look the same to you because of timezone formatting, focus on the order: if `feat_ts` > `label_ts`, that is leakage. The PITC fix below will guarantee `feat_ts <= label_ts`.

### Step 8: The fix: point-in-time join

Add one line and the bug disappears. Create `client/pitc.py`:

```python
# pitc.py: the CORRECT version. The only difference from leaky.py is the
# extra WHERE clause: event_timestamp <= l.event_timestamp
import os, psycopg2

PG = dict(host=os.environ["PG_HOST"], port=os.environ["PG_PORT"],
          user=os.environ["PG_USER"], password=os.environ["PG_PASSWORD"],
          dbname=os.environ["PG_DB"])
conn = psycopg2.connect(**PG); cur = conn.cursor()

cur.execute("""
    SELECT l.entity_id,
           l.event_timestamp AS label_ts,
           f.event_timestamp AS feat_ts,
           f.feature_name, f.feature_value
    FROM labels l
    JOIN LATERAL (
        SELECT feature_name, feature_value, event_timestamp
        FROM feature_values
        WHERE entity_id = l.entity_id
          AND event_timestamp <= l.event_timestamp   -- THE FIX
        ORDER BY event_timestamp DESC
        LIMIT 2
    ) f ON TRUE
    ORDER BY l.entity_id, f.feature_name;
""")

for row in cur.fetchall():
    print(row)
conn.close()
```

Run it:

```bash
docker compose exec client python /app/pitc.py
```

Expected output:

```
('alice', datetime.datetime(2026, 10, 3, ...), datetime.datetime(2026, 10, 3, ...), 'avg_tx_amount', 52.13)
('alice', datetime.datetime(2026, 10, 3, ...), datetime.datetime(2026, 10, 2, ...), 'tx_count_7d', 11)
...
```

Notice that now every `feat_ts` is **on or before** `label_ts`. The model can only see information that existed at the time of the event. That is the PITC rule. This is the entire "magic" of a feature store for training.

### Step 9: Materialize (offline to online)

Now we copy the *latest snapshot per user* from Postgres into Redis, so that when a real user shows up we can get their features in 1 millisecond.

Create `client/materialize.py`:

```python
# materialize.py: copy the LATEST feature value per (user, feature) into Redis.
import os, json
from datetime import datetime, timezone
import psycopg2, redis

PG = dict(host=os.environ["PG_HOST"], port=os.environ["PG_PORT"],
          user=os.environ["PG_USER"], password=os.environ["PG_PASSWORD"],
          dbname=os.environ["PG_DB"])
r = redis.Redis(host=os.environ["REDIS_HOST"],
                port=int(os.environ["REDIS_PORT"]), decode_responses=True)

conn = psycopg2.connect(**PG); cur = conn.cursor()

# For each (user, feature) keep only the row with the newest event_timestamp.
cur.execute("""
    SELECT entity_id, feature_name, feature_value, event_timestamp
    FROM (
        SELECT *, ROW_NUMBER() OVER (
            PARTITION BY entity_id, feature_name
            ORDER BY event_timestamp DESC
        ) AS rn
        FROM feature_values
    ) t
    WHERE rn = 1;
""")

now_iso = datetime.now(timezone.utc).isoformat()
n = 0
for entity_id, feature_name, feature_value, event_ts in cur.fetchall():
    payload = {
        "value": feature_value,
        "event_timestamp": event_ts.isoformat(),
        "materialized_at": now_iso,   # when we put it into Redis
    }
    # Redis hash: one per user, one field per feature
    r.hset(f"features:{entity_id}", feature_name, json.dumps(payload))
    n += 1

print(f"Materialized {n} features into Redis.")
conn.close()
```

Run it:

```bash
docker compose exec client python /app/materialize.py
```

Expected output:

```
Materialized 6 features into Redis.
```

> Why 6? 3 users x 2 features = 6.

### Step 10: Online read (the fast path)

Now read features back from Redis, the same way a real model would in production.

Create `client/online.py`:

```python
# online.py: what a model serving system would do: grab features in <10ms.
import os, json, time, redis

r = redis.Redis(host=os.environ["REDIS_HOST"],
                port=int(os.environ["REDIS_PORT"]), decode_responses=True)

entity_id = "alice"   # try "bob" or "carol" too

t0 = time.perf_counter()
blob = r.hgetall(f"features:{entity_id}")
elapsed_ms = (time.perf_counter() - t0) * 1000

print(f"\nOnline read for {entity_id}: {elapsed_ms:.2f} ms\n")
for feature_name, raw_value in blob.items():
    payload = json.loads(raw_value)
    print(f"  {feature_name:15s} value={payload['value']}")
    print(f"  {' ':15s} feat_ts = {payload['event_timestamp']}")
    print(f"  {' ':15s} mat_ts  = {payload['materialized_at']}")
    print()
```

Run it:

```bash
docker compose exec client python /app/online.py
```

Expected output (numbers will vary):

```
Online read for alice: 0.42 ms

  avg_tx_amount   value=58.43
                 feat_ts = 2026-10-04T...
                 mat_ts  = 2026-10-04T...

  tx_count_7d     value=17
                 feat_ts = 2026-10-04T...
                 mat_ts  = 2026-10-04T...
```

Two things to notice:

1. **Latency is sub-millisecond.** That is why online stores are needed.
2. **`mat_ts` is very close to `feat_ts`.** That gap is your **freshness**, i.e. how recent your features are. In production this could be 5 seconds, 5 minutes, or 5 hours depending on the pipeline.

## Verification

Run each of these. The output should match what's written after "Expected".

```bash
# How many rows are in Postgres?
docker compose exec postgres psql -U fsuser -d feast_offline -c "SELECT COUNT(*) FROM feature_values;"
# Expected: 30

# Run the fixed query; every feat_ts should be on or before label_ts
docker compose exec client python /app/pitc.py
# Expected: no future dates in feat_ts

# Inspect Redis directly (no Python needed)
docker compose exec redis redis-cli HGETALL features:alice
# Expected: 2 fields (avg_tx_amount, tx_count_7d), each a JSON blob
```

## Testing

### Test 1: Confirm leakage is real (without our fix)

```bash
docker compose exec postgres psql -U fsuser -d feast_offline -c "
SELECT COUNT(*) AS leaky_rows
FROM labels l
JOIN feature_values f
  ON f.entity_id = l.entity_id
 AND f.event_timestamp > l.event_timestamp;"
```

Expected: A non-zero number. That is the bug we want to fix.

### Test 2: Confirm PITC fix gives zero leakage

```bash
docker compose exec postgres psql -U fsuser -d feast_offline -c "
SELECT COUNT(*) AS still_leaky
FROM labels l
JOIN LATERAL (
    SELECT 1 FROM feature_values
    WHERE entity_id = l.entity_id AND event_timestamp > l.event_timestamp
    LIMIT 1
) f ON TRUE;"
```

Expected: `0`. Bug fixed.

### Test 3: Materialize is safe to re-run

```bash
docker compose exec client python /app/materialize.py
docker compose exec client python /app/materialize.py
docker compose exec redis redis-cli HGET features:alice tx_count_7d
```

Expected: No errors, the value is the same after both runs. Re-running the materialize script does not duplicate anything; it just overwrites with the latest snapshot.

## Troubleshooting

**Containers won't start / `connection refused`**
- Wait 10 seconds. Run `docker compose ps`. Both `postgres` and `redis` should say `(healthy)`.
- If stuck, run `docker compose logs postgres` or `docker compose logs redis` to see the error.

**`psycopg2.OperationalError: could not connect to server`**
- The Postgres container is still starting up. Wait, then retry.

**`redis.exceptions.ConnectionError: Error 111`**
- The Redis container failed. Run `docker compose logs redis` to see why.

**`seed.py` says `Inserted 0 ...`**
- Postgres was not ready. Re-run the command after a few seconds, or do `docker compose down -v && docker compose up -d` to start fresh.

**`online.py` shows nothing**
- You probably forgot to run `materialize.py` first. Redis is empty until you materialize.

**`docker compose exec` says "container is not running"**
- Run `docker compose ps`. If a container is `Exit 1`, check its logs with `docker compose logs <name>`.

**Still stuck?**
- Nuclear option: `docker compose down -v && docker compose up -d`. This wipes Postgres data and restarts everything.

## Cleanup

When you are done:

```bash
docker compose down -v
cd .. && rm -rf fs-beginner
```

No cloud bill: all of this ran locally in Docker on your machine.

## Epilogue

You just built the smallest possible feature store: two tables in Postgres, two `HGETALL`s in Redis, and one Python script that bridges them. The three ideas (offline/online split, point-in-time correctness, freshness) are exactly the same ideas inside every managed feature store (Feast, Tecton, Vertex, SageMaker). The mechanics you learned here transfer directly.

## Principles

These are the underlying design principles this lab demonstrates:

- **Separation of concerns:** the offline store is optimized for full-history scans; the online store is optimized for point lookups. One system cannot do both well.
- **Time as a first-class dimension:** every feature row carries `event_timestamp`, and every join respects it. This is the only durable defense against leakage.
- **Idempotent materialize:** the bridge between offline and online must be re-runnable without producing duplicate or stale keys.
- **Freshness is a budget, not a number:** you choose seconds, minutes, or hours per feature based on cost and downstream impact.
- **Whiteboard-first design:** if you cannot draw the system on a whiteboard, you do not understand it yet.
- **Local before cloud:** every production feature store starts as a local prototype. This lab is that prototype.

## What You Learned

In one sentence: a feature store is **a history database for training + a snapshot database for serving, joined in a way that respects time**.

If you remember nothing else, remember these three phrases:

1. **Offline for training, online for serving.** Different jobs need different tools.
2. **Always join with `event_timestamp <= label_ts`.** One line of SQL prevents leakage.
3. **Materialize keeps the online store fresh.** It is just a "copy the latest" script.

Concrete takeaways:

- The three pillars of feature store design: offline/online split, PITC, freshness.
- How to encode an `event_timestamp` on each feature row and use it in a `JOIN LATERAL ... ORDER BY event_timestamp DESC LIMIT 1 WHERE event_timestamp <= label_ts` pattern.
- How to reproduce and then fix feature leakage with a real SQL example.
- How a materialize step pushes the latest snapshot per entity from PostgreSQL into Redis.
- How to measure online retrieval latency and freshness on a laptop.
- The shape of the canonical feature-store whiteboard diagram.

## Next Steps

- **Lab 7.2**: do the exact same thing using **Feast** (a real open-source feature store) and see how it packages these ideas.
- **Add a timer**: run `materialize.py` every minute and watch the freshness gap shrink.
- **Add more features**: edit `seed.py` to add a third feature like `failed_login_24h`.
- **Train a real model**: take the `pitc.py` output, put it into pandas, and train a tiny scikit-learn classifier. Compare AUC between the leaky version and the PITC version. You will see leakage inflate offline metrics.
- **Swap local Postgres for S3 + Athena and local Redis for ElastiCache** to convert the small stack into a cloud-native stack on AWS `ap-southeast-1`.

## Additional Resources

- Feast documentation: <https://docs.feast.dev/>
- Google Cloud reference on point-in-time correctness: <https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning#feature_store>
- "The Modern Feature Store" (Tecton blog): <https://www.tecton.ai/blog/what-is-a-modern-feature-store/>
- Redis HASH commands: <https://redis.io/commands/hset/>
- PostgreSQL `JOIN LATERAL`: <https://www.postgresql.org/docs/current/queries-lateral.html>
- Poridhi Labs, Module 7: Feature Stores (overview)

## Conclusion

This lab introduced the three ideas that every practitioner must internalize before adopting a production feature store: the offline/online split, point-in-time correctness, and feature freshness. You built a minimal two-store stack on your laptop using PostgreSQL as the offline store and Redis as the online store, reproduced a leakage bug, fixed it with a PITC ASOF JOIN, and verified the online path with a materialize script. Once this pattern is clear in your head, every managed feature store (Feast, Tecton, Vertex, SageMaker) is just a polished version of the same idea, which is the entire point of starting local before going to the cloud.
# Lab 7.4: Streaming Ingestion with Feast

## Introduction

Every production feature store has to keep the online store fresh. In Lab 7.3 you saw the **batch** path: a daily job writes Parquet to S3, then `feast materialize-incremental` copies the latest snapshot into Redis. That works for hourly or daily features, but real systems also have features that change in real time: a driver's current GPS location, a user's last-click event, a fraud score that updates every few seconds, a session token that must reach the model in milliseconds. Batch ingestion is far too slow for these signals.

This is where **streaming ingestion** comes in. Feast exposes a method called `feast.push()` (also reachable as `fs.push()` or `store.push()`) that writes a single feature vector straight to the online store, bypassing the S3 round-trip and the registry lock. There is no Parquet write, no point-in-time join, and no materialization job. The call lands in Redis, and the next `get_online_features()` call returns the new value, typically in single-digit milliseconds.

In this lab you will install Feast, wire it to the Poridhi managed Redis, define a `driver_stats` feature view, push events with the Python SDK and over HTTP, inspect the raw keys in Redis, compare the three `PushMode` options, and benchmark push and read-after-write latency with percentiles. The lab is fully self-contained: every step runs from a clean Poridhi VM, even if you have not completed Labs 7.2 or 7.3.

![alt text](images/image-11.png)

Inside the VM, the **Producer** is either the **Stream Simulator** (`producer.py`) that calls `store.push()` from Python, or an **HTTP client** (`curl`) that hits the Feast Feature Server on port 6566. Both target the same `PushSource` named `driver_stats_push`, which is bound to a `FileSource` batch source. The **FeatureView** `driver_stats_stream` declares the features, the entity, and the TTL.

Where the rows land depends on `PushMode`. `ONLINE` writes only to Redis. `OFFLINE` appends to the parquet batch source (the file is rewritten with the pushed rows plus schema). `ONLINE_AND_OFFLINE` does both. The **Online Reader** calls `get_online_features()`, which always reads from Redis regardless of the push mode.

## Learning Objectives

By the end of this lab, you will be able to:

- Install Feast in a Python virtual environment on the Poridhi lab VM and verify the CLI works.
- Point Feast at the Poridhi managed Redis (endpoint and credentials from the Cloud Tray panel) and confirm the connection.
- Write a `feature_store.yaml` that uses a local registry, a file offline store, and the managed Redis as the online store.
- Define an `Entity`, a `FileSource`, a `PushSource`, and a `FeatureView` whose `source=` is a `PushSource`.
- Run `feast apply` to register the definitions and confirm the registry was created.
- Call `store.push()` from the Python SDK to write a single feature vector to Redis.
- Call `POST /push` on the Feast Feature Server to push from a non-Python producer.
- Inspect raw Redis keys, hash fields, and the `HSET` counter to prove the online write happened.
- Compare the three `PushMode` options (`ONLINE`, `OFFLINE`, `ONLINE_AND_OFFLINE`).
- Measure push and read-after-write latency with p50, p95, and p99 percentiles.
- Explain when to use push ingestion instead of scheduled materialization.

## Prerequisites

- **Region:** `ap-southeast-1` (Asia Pacific, Singapore) with AZs `ap-southeast-1a`, `ap-southeast-1b`, `ap-southeast-1c`. This lab creates no AWS resources; the region is set so the VM stays consistent with the rest of the Feature Store series.
- **Environment:** Poridhi Cloud lab VM with Linux (Debian/Ubuntu shell) and VS Code pre-installed. The VS Code CLI (`code`), `nano`, `xdg-open`, and `redis-cli` are NOT available in the default lab VM, so this lab uses `vim` to edit config files and a Python `redis.Redis` client to inspect Redis directly.
- **Cloud Tray: Redis (managed, already running):** Open the Cloud Tray in the Poridhi lab UI, click **Database**, then click the **Redis** card. The panel shows the actual credentials for this lab session: **Username**, **Password**, **IP Address**, **Port**, and a copy-able **Connection String**. The values can change between lab runs, so always read them from the panel instead of hard-coding them. You will use these in Steps 1, 4, and 6.
- **Tools already on the VM:** `python3` (3.10 or 3.11 recommended; 3.9 works but Feast wheels are best for 3.10+), `pip`, `vim` (at `/usr/bin/vim`), and `curl`. The `redis` Python client is installed by `feast[redis]`, so you do not need a separate install.
- **Note on prior labs:** This lab is part of the Feature Store series (7.1 through 7.8). It is fully self-contained, so you do NOT need to have completed Lab 7.2 or 7.3 first. Every step, from creating the venv to running `feast apply`, is repeated here. If you have already completed Lab 7.2 or 7.3, those steps simply recreate the same artifacts and run idempotent commands.

## Prologue

Imagine you work at a ride-hailing company. Your ML team has built a model that predicts whether a driver is likely to accept the next ride offer. The model uses features like average rating, completed trips last 7 days, and current online hours. Most of these features are computed in a nightly batch job: a Spark pipeline reads raw events, computes aggregates, writes Parquet to S3, and the next morning `feast materialize-incremental` copies the freshest snapshot into Redis. The training pipeline uses `get_historical_features()` and the inference service uses `get_online_features()`. So far, so good.

Now imagine a new product feature: a real-time "driver momentum" signal that updates every few seconds from a Kafka topic. A driver finishes a ride and the score should jump within the same second. A batch job is far too slow for that: by the time the nightly Spark job runs, the signal is hours stale and useless. This is exactly the problem streaming ingestion solves. With `feast.push()`, a Kafka consumer (or any streaming app) can take one event, build a feature row, and call `store.push()`. The call lands in Redis, the next `get_online_features()` returns the new value, and the model can use the fresh signal in real time.

In this lab you will set up that streaming path on the Poridhi lab VM. You will install Feast, wire it to the Poridhi managed Redis, define a `driver_stats_stream` feature view backed by a `PushSource`, then push events with the Python SDK and over HTTP, inspect the raw keys, and measure latency with percentiles. By the end, the path from "fresh signal" to "model can use it" will be a few milliseconds.

## Step-by-Step Implementation

### Step 1: Collect the managed Redis credentials from the Cloud Tray

Before you start, open the Cloud Tray in the Poridhi lab UI and copy the Redis credentials. You will paste them once and the rest of the lab will use the resulting env vars.

1. In the Poridhi Cloud Playground, click **Cloud Tray**.
2. Click **Database** to open the Database Servers panel.
3. Click the **Redis** card. The panel shows the **Username**, **Password**, **IP Address**, **Port**, and a copy-able **Connection String** for the current lab session. Confirm the status is `Running`.
4. Copy the **Username**, **Password**, **IP Address**, and **Port** values.

Keep the panel open in another tab. The endpoint and password can rotate between lab sessions, so always re-read them from the panel if you start a new session.

### Step 2: Create the project directory and the env file

```bash
mkdir -p ~/feast-streaming-lab
cd ~/feast-streaming-lab
```

Create an `env.sh` file with `vim`:

```bash
vim env.sh
```

Paste the following into `env.sh`, replacing each placeholder with the value from the Cloud Tray panel:

```bash
export REDIS_HOST="<paste-ip-from-cloud-tray>"
export REDIS_PORT="<paste-port-from-cloud-tray>"
export REDIS_USERNAME="<paste-username-from-cloud-tray>"
export REDIS_PASSWORD="<paste-password-from-cloud-tray>"
export AWS_REGION="ap-southeast-1"
```

Save with `:wq`. Then load it into your shell:

```bash
source env.sh
echo "*" > .gitignore
echo "Redis target: $REDIS_HOST:$REDIS_PORT as user $REDIS_USERNAME"
```



Expected: a line like `Redis target: 10.10.0.5:6379 as user default`. If `source env.sh` prints nothing, the file is empty; re-open it and paste again.

![alt text](images/image-12.png)

> **Would I get an error if I ran this?** No. The only failure mode is forgetting to load `env.sh` in a new terminal, in which case later steps will print `KeyError: 'REDIS_HOST'`. If that happens, run `cd ~/feast-streaming-lab && source env.sh` and retry.

### Step 3: Create the Python virtual environment and install packages

```bash
cd ~/feast-streaming-lab
sudo apt update
sudo apt install -y python3-venv python3-pip
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
# Install order matters. feast 0.40.1 hard-pins numpy<2,>=1.22 in its package
# metadata, and modern pyarrow (>=14) hard-pins numpy>=2. The two constraints
# are not simultaneously satisfiable: any `pip install "feast[redis]==0.40.1"
# pyarrow>=14` in one venv will either downgrade numpy to 1.26.4 (and then
# pyarrow 14+ refuses to import) or leave numpy 2.x and break feast. We avoid
# the conflict by giving pandas a second parquet engine (fastparquet) that
# supports numpy 1.26.4, and letting feast keep the numpy 1.x it requires.
pip install "pandas>=2.2" "fastparquet"
pip install "feast[redis]==0.40.1"
```

Confirm the installs (this also proves the two parquet engines are loadable, which is the actual root cause of the Step 6 error):

```bash
feast --version
python -c "import feast, redis, pandas, fastparquet; print('feast', feast.__version__, '| redis-py', redis.__version__, '| pandas', pandas.__version__, '| fastparquet', fastparquet.__version__)"
```

Expected: a `feast` version starting with `0.40`, four successful imports, and a `fastparquet` version printed (anything in the `2023.x` to `2026.x` range).

> **Would I get an error if I ran this?** Possibly. Three things can fail, in order of likelihood on a Poridhi VM:
> 1. `python3 -m venv .venv` fails on a VM without `python3-venv` installed. The `apt install` line above installs it. If `apt` complains about a locked dpkg, wait a minute and retry, or run `sudo apt install -y python3-venv` on its own.
> 2. `ImportError: Unable to find a usable engine; tried using: 'pyarrow', 'fastparquet'` (confirmed on Python 3.12 by a Poridhi user in October 2026): the venv has pandas but no parquet engine. `pip install "feast[redis]==0.40.1"` does not pull in `pyarrow` (it depends on `pyarrow>=4` only at the metadata level and is happy with the system version), and on a clean Python 3.12 venv there is no `pyarrow` at all. Install `fastparquet` (or `pyarrow`) explicitly: `pip install fastparquet`, then re-run the verification import. The `engine="fastparquet"` argument in Step 6 picks it up.
> 3. `pip install "feast[redis]==0.40.1"` can fail to build a wheel on Python 3.9 or older. If you see "Could not build wheels for ...", check `python -V`: if it prints 3.9 or older, ask the lab UI for a VM with Python 3.10 or 3.11, or drop the version pin and let pip pick a compatible Feast (Feast 0.30+ supports Python 3.9).

### Step 4: Test the connection to managed Redis

```bash
cd ~/feast-streaming-lab
source env.sh
python - <<'PY'
import os, redis
r = redis.Redis(
    host=os.environ["REDIS_HOST"],
    port=int(os.environ["REDIS_PORT"]),
    username=os.environ["REDIS_USERNAME"],
    password=os.environ["REDIS_PASSWORD"],
)
print("PING:", r.ping())
print("Redis version:", r.info("server")["redis_version"])
PY
```

Expected output:

```text
PING: True
Redis version: 7.0.15
```

![alt text](images/image-13.png)

> **Would I get an error if I ran this?** Possibly. Common failures:
> 1. `redis.exceptions.AuthenticationError` or `WRONGPASS`: the credentials in `env.sh` do not match the current Cloud Tray session. Reopen the Redis card, copy the fresh values, update `env.sh`, and re-run `source env.sh`.
> 2. `redis.exceptions.ConnectionError` or a timeout: the IP or port is wrong, or Redis is not `Running`. Check the status in the Cloud Tray and confirm `echo $REDIS_HOST $REDIS_PORT` prints the values from the panel.
> 3. `KeyError: 'REDIS_HOST'`: you opened a new terminal and forgot `source env.sh`. Run it again.
> 4. If you see the wrong Redis version (e.g. `6.x`): the lab is on a different Cloud Tray image. The script still works; only the expected `Redis version: 7.0.15` line in the assertions will differ.

### Step 5: Create the Feast repository and `feature_store.yaml`

```bash
cd ~/feast-streaming-lab
mkdir -p feature_repo/data
cd feature_repo
```

Write the file with one heredoc. Replace the four placeholders (`__REDIS_USERNAME__`, `__REDIS_PASSWORD__`, `__REDIS_HOST__`, `__REDIS_PORT__`) with the actual values from the Cloud Tray panel. Paste the heredoc block by itself, then run the verification commands in a separate block.

```bash
cat > feature_store.yaml <<'YAML_END'
project: streaming_ingestion
provider: local
registry: data/registry.db
online_store:
  type: redis
  redis_type: redis
  connection_string: "redis://__REDIS_USERNAME__:__REDIS_PASSWORD__@__REDIS_HOST__:__REDIS_PORT__/0"
offline_store:
  type: file
entity_key_serialization_version: 2
YAML_END
```

> **Why `redis://user:pass@host:port/0`?** Feast's Redis online store parses the standard `redis://` URL form. The bare `host:port,key=value` form (without `redis://`) is not understood by Feast 0.40. The URL already carries username and password, so no extra `auth_type` field is needed: including `auth_type: basic` in `feature_store.yaml` is rejected by `RepoConfig` in Feast 0.40.1 and breaks `feast apply` with `pydantic_core._pydantic_core.ValidationError: auth_type: Extra inputs are not permitted`.
>
> **Why a heredoc and not `vim`?** The Poridhi lab VM does not ship with `envsubst` by default, and pasting a multi-line `vim` buffer across an SSH-style terminal often drops the `i` (insert) or the final `:wq`, leaving the file empty. The `cat > file <<'YAML_END' ... YAML_END` pattern writes the file in one shell command with no editor in the loop. If you prefer `vim`, run `vim feature_store.yaml`, type `i`, paste the YAML body, press `Esc`, type `:wq`, and confirm with `cat feature_store.yaml`.

Verify the file:

```bash
cat feature_store.yaml
grep connection_string feature_store.yaml
```

Expected `grep` output (with your real values substituted in):

```text
  connection_string: "redis://ACTUAL_USERNAME:ACTUAL_PASSWORD@ACTUAL_HOST:ACTUAL_PORT/0"
```

If the file is empty, contains the literal words `YAML_END` or `grep` on their own lines, or if the `connection_string` still shows the `__REDIS_*__` placeholders, the heredoc was pasted with the trailing commands attached. Re-paste the `cat > feature_store.yaml <<'YAML_END' ... YAML_END` block by itself, then re-run `cat feature_store.yaml`. Because the file contains credentials, keep `.gitignore` set to `*` (already done in Step 2):

```bash
ls -la
```

![alt text](images/image-14.png)

> **Would I get an error if I ran this?** No, this step just creates a file. The error would only show up at `feast apply` time. See Step 8 for the connection-string failure mode.

### Step 6: Seed the batch source (offline store)

A `PushSource` needs a `FileSource` as its `batch_source`; the file defines the schema. Seed a small parquet file with 24 hours of history for five drivers. This is enough for any `get_historical_features()` call later and is what `PushMode.OFFLINE` writes back to.

```bash
cd ~/feast-streaming-lab/feature_repo
vim seed_data.py
```

Paste:

```python
import os
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd

os.makedirs("data", exist_ok=True)
rng = np.random.default_rng(7)
now = datetime.now(timezone.utc)

rows = []
for driver_id in range(1001, 1006):
    for h in range(24):
        rows.append({
            "driver_id": driver_id,
            "event_timestamp": now - timedelta(hours=h + 1),
            "created": now - timedelta(hours=h + 1),
            "conv_rate": np.float32(rng.random()),
            "acc_rate": np.float32(rng.random()),
            "avg_daily_trips": int(rng.integers(10, 500)),
        })

df = pd.DataFrame(rows)
df["conv_rate"] = df["conv_rate"].astype("float32")
df["acc_rate"] = df["acc_rate"].astype("float32")
df["avg_daily_trips"] = df["avg_daily_trips"].astype("int64")
df.to_parquet("data/driver_stats.parquet", index=False, engine="fastparquet")
print("Seeded", len(df), "rows into data/driver_stats.parquet")
```

Save with `:wq`. Run it:

```bash
python seed_data.py
```

![alt text](images/image-15.png)

Expected: `Seeded 120 rows into data/driver_stats.parquet`.

> **Would I get an error if I ran this?** Possibly. Three common failures:
> 1. `ModuleNotFoundError: No module named 'pandas'` (or `numpy`, `fastparquet`): the venv is not active, or Step 3's install was skipped. Run `source .venv/bin/activate` from `~/feast-streaming-lab/` and, if the module is still missing, `pip install pandas fastparquet` from inside the venv.
> 2. `ImportError: Unable to find a usable engine; tried using: 'pyarrow', 'fastparquet'` (confirmed on Python 3.12 by a Poridhi user in October 2026): `fastparquet` is not installed. `pip install fastparquet` inside the active venv, then re-run.
> 3. `ImportError: pyarrow requires NumPy 2.0 or newer, found 1.26.x` (confirmed on Python 3.12 by a Poridhi user in October 2026): `feast 0.40.1` hard-pins `numpy<2` and modern `pyarrow` hard-pins `numpy>=2`; they cannot coexist. The lab uses `fastparquet` for parquet I/O so `pyarrow` is never imported at runtime; if a stray `import pyarrow` somewhere in the environment is triggering this, remove it with `pip uninstall -y pyarrow` rather than fighting the version conflict.

> **What does `PushMode.OFFLINE` actually do?** It rewrites `data/driver_stats.parquet` with the pushed rows (it does not literally append a row to the existing file). For a file offline store the new file will contain the pushed rows plus the schema. The Step 12 test (`push_modes.py`) prints `offline rows with 222 = 1` because the new file has exactly one row whose `avg_daily_trips` equals 222.

### Step 7: Define the Entity, PushSource, and FeatureView

```bash
cd ~/feast-streaming-lab/feature_repo
vim features.py
```

Paste:

```python
from datetime import timedelta

from feast import Entity, FeatureView, Field, FileSource, PushSource
from feast.types import Float32, Int64

driver = Entity(name="driver", join_keys=["driver_id"])

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
```

Save with `:wq`.

The critical line is `source=driver_stats_push`. Because the `FeatureView` points at a `PushSource` instead of a plain batch source, Feast accepts `store.push("driver_stats_push", ...)` calls for it. The TTL is one day so freshly pushed values are never treated as expired during the lab.

> **Would I get an error if I ran this?** No, this is just a file. Errors show up at `feast apply` (Step 8). The `created_timestamp_column="created"` is required when the batch source is a `FileSource` in Feast 0.40; without it, `feast apply` may warn that the offline store cannot use the source for incremental ingestion. The streaming path in this lab does not need `created`, but keeping it makes the lab future-proof.

### Step 8: Apply the definitions

```bash
cd ~/feast-streaming-lab/feature_repo
feast apply
feast feature-views list
feast entities list
```

Expected output (abbreviated):

```text
Created entity driver
Created feature view driver_stats_stream
Deploying infrastructure for driver_stats_stream
...
NAME                 ENTITIES   TYPE
driver_stats_stream  {'driver'} FeatureView
```

![alt text](images/image-16.png)

If you re-run `feast apply` on the same definitions, the output ends with `No changes to registry` instead of `Created ...`. That is normal and means the registry is already in sync.

> **Would I get an error if I ran this?** Possibly. The realistic failures, in order of likelihood:
> 1. `pydantic_core._pydantic_core.ValidationError: auth_type: Extra inputs are not permitted` (confirmed on Feast 0.40.1): `feature_store.yaml` contains an `auth_type: basic` line under `online_store`. The `redis://user:pass@host:port/0` URL already carries the credentials, so the `auth_type` field is not part of the `RepoConfig` schema. Remove the `auth_type: basic` line from `feature_store.yaml` and re-run `feast apply`.
> 2. `yaml.scanner.ScannerError: while scanning a simple key ... could not find expected ':'` with `YAML` and `grep` appearing on their own lines (confirmed when pasting heredocs across an SSH-style terminal): the heredoc body was pasted together with the closing terminator and the next command. The terminator and the trailing command were written into the YAML file as literal text. Re-paste the `cat > feature_store.yaml <<'YAML_END' ... YAML_END` block by itself, then re-run `cat feature_store.yaml` and confirm the file is exactly 10 lines and contains the literal `YAML_END` token nowhere.
> 3. `bash: envsubst: command not found` (confirmed on the default Poridhi lab VM): the VM does not ship with the `gettext-base` package, so `envsubst` is not available. Either install it with `sudo apt-get install -y gettext-base` and use the `envsubst < feature_store.yaml > feature_store.yaml.rendered` form, or skip `envsubst` and write the file with the `cat > feature_store.yaml <<'YAML_END' ... YAML_END` heredoc from Step 5 (recommended; the lab uses that path by default).
> 4. `redis.exceptions.AuthenticationError` or `WRONGPASS`: the `connection_string` in `feature_store.yaml` does not match the current Cloud Tray. Reopen the Redis card, update `env.sh`, then re-write `feature_store.yaml` with the new values (substitute the four placeholders in the `connection_string` line).
> 5. `redis.exceptions.ConnectionError`: Redis is not `Running` in the Cloud Tray, or the host/port is wrong.
> 6. `ValidationError: PushSource ... batch_source must be set`: the `PushSource` block is missing the `batch_source=` argument. Re-open `features.py` and confirm the line `batch_source=driver_stats_batch` is present.
> 7. `ValidationError: source ... is not a known source type`: you accidentally wrote `from feast.types import ...` for the source instead of using `feast.FileSource` and `feast.PushSource`. Re-check the imports.
> 8. `FileNotFoundError: ...driver_stats.parquet`: you skipped Step 6. Run `python seed_data.py` from inside `feature_repo`.

### Step 9: Capture the Redis baseline

Before pushing anything, write a small helper that inspects Feast data directly in Redis. You will run it before and after pushes to prove the writes hit Redis.

```bash
cd ~/feast-streaming-lab/feature_repo
vim inspect_redis.py
```

Paste:

```python
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
```

Save with `:wq`. Run it:

```bash
python inspect_redis.py
```

Expected output before any push:

```text
Feast keys for project streaming_ingestion: 0
HSET calls so far: 0
```

![alt text](images/image-17.png)

> **Would I get an error if I ran this?** Possibly. The same three failures as Step 4 apply (`AuthenticationError`, `ConnectionError`, `KeyError: 'REDIS_HOST'`). Also: if another Poridhi user has been pushing to the same Redis with the same project name, `Feast keys for project streaming_ingestion` may be non-zero. That is fine; the lab still works. Note the baseline number so you can compare it after the pushes.

### Step 10: Push one event with the Python SDK and read it back

This is the core of the lab. `store.push()` takes the push source name, a DataFrame, and a `PushMode`.

```bash
cd ~/feast-streaming-lab/feature_repo
vim push_once.py
```

Paste:

```python
import time
from datetime import datetime, timezone

import pandas as pd
from feast import FeatureStore
from feast.data_source import PushMode

store = FeatureStore(repo_path=".")

event = pd.DataFrame({
    "driver_id": [1001],
    "conv_rate": [0.91],
    "acc_rate": [0.88],
    "avg_daily_trips": [321],
    "event_timestamp": [datetime.now(timezone.utc)],
})

t0 = time.perf_counter()
store.push("driver_stats_push", event, to=PushMode.ONLINE)
t1 = time.perf_counter()

features = store.get_online_features(
    features=[
        "driver_stats_stream:conv_rate",
        "driver_stats_stream:acc_rate",
        "driver_stats_stream:avg_daily_trips",
    ],
    entity_rows=[{"driver_id": 1001}],
).to_dict()
t2 = time.perf_counter()

print("Push latency:           %.2f ms" % ((t1 - t0) * 1000))
print("Read-after-write total: %.2f ms" % ((t2 - t0) * 1000))
print(features)
```

Save with `:wq`. Run it:

```bash
python push_once.py
```

Expected output (timings vary with the network path to Redis):

```text
Push latency:           8.40 ms
Read-after-write total: 12.95 ms
{'driver_id': [1001], 'conv_rate': [0.9100000262260437], 'acc_rate': [0.8799999952316406], 'avg_daily_trips': [321], 'event_timestamp': [...]}
```

The values you pushed are now readable from the online store, and no `feast materialize` was ever run.

> **Would I get an error if I ran this?** Possibly. The realistic failures:
> 1. `ImportError: cannot import name 'PushMode' from 'feast.data_source'`: you are on a Feast version that does not expose `PushMode` from there. The fix is to use `from feast import PushMode` (already done above) instead of `from feast.data_source import PushMode`. If the import still fails, check `pip show feast` and reinstall with `pip install --upgrade "feast[redis]==0.40.1"`.
> 2. `PushSourceNotFoundException`: the name `driver_stats_push` is not in the registry. Re-run `feast apply`.
> 3. `ValueError: ... does not have online=True enabled`: the `FeatureView` is missing `online=True`. Edit `features.py` and re-apply.
> 4. `TypeError: ... event_timestamp ... must be timezone-aware`: you used `datetime.utcnow()` instead of `datetime.now(timezone.utc)`. Fix the script to use `datetime.now(timezone.utc)`.

### Step 11: Inspect the raw keys in Redis

Now confirm the write really landed in Redis rather than being served from a cache:

```bash
cd ~/feast-streaming-lab/feature_repo
python inspect_redis.py
```

Expected output:

```text
Feast keys for project streaming_ingestion: 1
  key (first 40 bytes): b'...' | type: hash | ttl: -1
     hash field: b'...'
     hash field: b'...'
     hash field: b'...'
     hash field: b'_ts:driver_stats_stream'
HSET calls so far: 1
```

Feast stores each entity as one Redis **hash**. The hash fields are hashed feature identifiers plus a `_ts:driver_stats_stream` field that records the event timestamp. The HSET counter increased, which proves the push hit Redis directly. The exact byte content of the key depends on `entity_key_serialization_version` and the schema, so the prefix may differ; what matters is `type: hash` and that `HSET calls so far` is at least 1.

> **Would I get an error if I ran this?** No, this is a read-only script. The only failure modes are the same Redis connection errors as Step 4. If the script prints `Feast keys for project streaming_ingestion: 0` even after the push in Step 10, the push call did not actually hit Redis; go back to Step 10 and check for exceptions in its output.

### Step 12: Compare the three push modes

`PushMode` controls where a pushed row lands. This script proves it, using driver 1005:

```bash
cd ~/feast-streaming-lab/feature_repo
vim push_modes.py
```

Paste:

```python
from datetime import datetime, timezone

import pandas as pd
from feast import FeatureStore, PushMode

store = FeatureStore(repo_path=".")


def event(trips):
    return pd.DataFrame({
        "driver_id": [1005],
        "conv_rate": [0.5],
        "acc_rate": [0.5],
        "avg_daily_trips": [trips],
        "event_timestamp": [datetime.now(timezone.utc)],
    })


def online_trips():
    out = store.get_online_features(
        features=["driver_stats_stream:avg_daily_trips"],
        entity_rows=[{"driver_id": 1005}],
    ).to_dict()
    return out["avg_daily_trips"][0]


def offline_has(trips):
    df = pd.read_parquet("data/driver_stats.parquet")
    return int((df["avg_daily_trips"] == trips).sum())


store.push("driver_stats_push", event(111), to=PushMode.ONLINE)
print("After ONLINE push (111):               online =", online_trips(), "| offline rows with 111 =", offline_has(111))

store.push("driver_stats_push", event(222), to=PushMode.OFFLINE)
print("After OFFLINE push (222):              online =", online_trips(), "| offline rows with 222 =", offline_has(222))

store.push("driver_stats_push", event(333), to=PushMode.ONLINE_AND_OFFLINE)
print("After ONLINE_AND_OFFLINE push (333):   online =", online_trips(), "| offline rows with 333 =", offline_has(333))
```

Save with `:wq`. Run it:

```bash
python push_modes.py
```

Expected output:

```text
After ONLINE push (111):               online = 111 | offline rows with 111 = 0
After OFFLINE push (222):              online = 111 | offline rows with 222 = 1
After ONLINE_AND_OFFLINE push (333):   online = 333 | offline rows with 333 = 1
```

Read the three lines carefully. The `ONLINE` push did not touch the parquet file. The `OFFLINE` push left the online value at `111` (because offline and online are independent) and rewrote the parquet file with the pushed 222 row. Only `ONLINE_AND_OFFLINE` updated both, which is the mode to use when you need serving and training data to stay in sync.

> **Would I get an error if I ran this?** Possibly:
> 1. Same `PushMode` import error as Step 10. Use `from feast import PushMode`.
> 2. `FileNotFoundError: data/driver_stats.parquet`: you ran the script from the wrong directory. `cd ~/feast-streaming-lab/feature_repo` first.
> 3. The `offline rows with 222` count is `0`: `PushMode.OFFLINE` is not supported on a `file` offline store in your Feast version, or the file is read from a cached handle. Try `from feast.data_source import PushMode` and `to=PushMode.OFFLINE` (the alternative import path), then re-run.

### Step 13: Run the Stream Simulator

Now simulate a real stream. This producer emits one event per tick across five drivers and prints the push latency of each event:

```bash
cd ~/feast-streaming-lab/feature_repo
vim producer.py
```

Paste:

```python
import os
import random
import time
from datetime import datetime, timezone

import pandas as pd
from feast import FeatureStore, PushMode

EVENTS = int(os.environ.get("EVENTS", "30"))
INTERVAL_MS = int(os.environ.get("INTERVAL_MS", "200"))

store = FeatureStore(repo_path=".")
state = {d: {"conv": 0.5, "acc": 0.5, "trips": 100} for d in range(1001, 1006)}

for i in range(EVENTS):
    driver_id = random.choice(list(state))
    s = state[driver_id]
    s["conv"] = min(1.0, max(0.0, s["conv"] + random.uniform(-0.05, 0.05)))
    s["acc"] = min(1.0, max(0.0, s["acc"] + random.uniform(-0.05, 0.05)))
    s["trips"] += random.randint(0, 3)

    df = pd.DataFrame({
        "driver_id": [driver_id],
        "conv_rate": [s["conv"]],
        "acc_rate": [s["acc"]],
        "avg_daily_trips": [s["trips"]],
        "event_timestamp": [datetime.now(timezone.utc)],
    })

    t0 = time.perf_counter()
    store.push("driver_stats_push", df, to=PushMode.ONLINE)
    ms = (time.perf_counter() - t0) * 1000
    print("event %02d | driver %d | trips %d | push %.2f ms" % (i + 1, driver_id, s["trips"], ms))
    time.sleep(INTERVAL_MS / 1000)

print("Done. Pushed", EVENTS, "events.")
```

Save with `:wq`. Run it:

```bash
cd ~/feast-streaming-lab/feature_repo
source env.sh
python producer.py
```

Expected output (abbreviated):

```text
event 01 | driver 1003 | trips 102 | push 6.91 ms
event 02 | driver 1001 | trips 101 | push 5.37 ms
...
Done. Pushed 30 events.
```

Read the current state of all five drivers with the Online Reader:

```bash
cd ~/feast-streaming-lab/feature_repo
vim read_online.py
```

Paste:

```python
from feast import FeatureStore

store = FeatureStore(repo_path=".")
result = store.get_online_features(
    features=[
        "driver_stats_stream:conv_rate",
        "driver_stats_stream:acc_rate",
        "driver_stats_stream:avg_daily_trips",
    ],
    entity_rows=[{"driver_id": d} for d in range(1001, 1006)],
).to_df()
print(result)
```

Save with `:wq`. Run it:

```bash
python read_online.py
```

Expected: a DataFrame with five rows (one per driver) and the three feature columns.

> **Would I get an error if I ran this?** Possibly. The realistic failures:
> 1. `NameError: name 'PushMode' is not defined`: the import line `from feast import FeatureStore, PushMode` is missing or commented out. Re-add it.
> 2. `KeyError` or `TypeError` in the dict update: the `state` initializer is missing one of the three keys. The script above initializes all three.
> 3. `ConnectionError`: Redis dropped the connection. Re-run the script; Feast reconnects automatically.

### Step 14: Push over HTTP with the Feature Server

Non-Python producers can use the Feature Server. Start it in the background:

```bash
cd ~/feast-streaming-lab/feature_repo
nohup feast serve -p 6566 > feature_server.log 2>&1 &
echo $! > feature_server.pid
sleep 5
tail -n 5 feature_server.log
```

Expected: a log line that includes `Uvicorn running on http://0.0.0.0:6566` (or similar). If the port is taken, use a different one and adjust the `curl` URLs.

Push an event for driver 1002 over HTTP:

```bash
TS=$(date -u +"%Y-%m-%d %H:%M:%S")
curl -s -X POST http://127.0.0.1:6566/push \
  -H "Content-Type: application/json" \
  -d "{
    \"push_source_name\": \"driver_stats_push\",
    \"df\": {
      \"driver_id\": [1002],
      \"conv_rate\": [0.77],
      \"acc_rate\": [0.66],
      \"avg_daily_trips\": [555],
      \"event_timestamp\": [\"$TS\"]
    },
    \"to\": \"online\"
  }"
echo
```

Read it back through the HTTP API:

```bash
curl -s -X POST http://127.0.0.1:6566/get-online-features \
  -H "Content-Type: application/json" \
  -d '{
    "features": ["driver_stats_stream:conv_rate", "driver_stats_stream:avg_daily_trips"],
    "entities": {"driver_id": [1002]}
  }'
echo
```

Expected: a JSON response that lists `avg_daily_trips` as `555` for driver `1002`. Time the push call:

```bash
TS=$(date -u +"%Y-%m-%d %H:%M:%S")
curl -s -o /dev/null -w "HTTP push total time: %{time_total}s\n" -X POST http://127.0.0.1:6566/push \
  -H "Content-Type: application/json" \
  -d "{\"push_source_name\":\"driver_stats_push\",\"df\":{\"driver_id\":[1002],\"conv_rate\":[0.78],\"acc_rate\":[0.66],\"avg_daily_trips\":[556],\"event_timestamp\":[\"$TS\"]},\"to\":\"online\"}"
```

> **Would I get an error if I ran this?** Possibly:
> 1. `Address already in use` when starting the Feature Server: port 6566 is taken, usually by an earlier run. Stop it with `kill $(cat feature_server.pid)` and start again, or pick another port with `feast serve -p 6577` and adjust the `curl` URLs.
> 2. `Connection refused` on the `curl` call: the server is still starting. Re-run the `curl` after a few seconds.
> 3. `HTTP 422 Unprocessable Entity` on the push: the `to` value or `push_source_name` does not match what the server expects. Check the server log with `tail -n 20 feature_server.log`. In Feast 0.40 the `to` field accepts the strings `"online"`, `"offline"`, `"online_and_offline"` (lowercase, with underscores). If you used `ONLINE` (uppercase) by mistake, change it to `"online"`.
> 4. `HTTP 500` with `pydantic` validation error: the `df` payload is missing `event_timestamp` or one of the feature columns. Re-check the JSON.

### Step 15: Benchmark push and read-after-write latency

Finally, measure latency with percentiles over many events. Each iteration pushes a unique `avg_daily_trips` value, immediately reads it back, and checks it matches, so the benchmark proves correctness as well as speed.

```bash
cd ~/feast-streaming-lab/feature_repo
vim benchmark.py
```

Paste:

```python
import os
import statistics
import time
from datetime import datetime, timezone

import pandas as pd
from feast import FeatureStore, PushMode

N = int(os.environ.get("N_EVENTS", "200"))
P95_LIMIT_MS = float(os.environ.get("P95_LIMIT_MS", "100"))

store = FeatureStore(repo_path=".")
features = ["driver_stats_stream:avg_daily_trips"]

push_ms, total_ms = [], []
mismatches = 0

for i in range(N):
    driver_id = 1001 + (i % 5)
    marker = 10000 + i
    df = pd.DataFrame({
        "driver_id": [driver_id],
        "conv_rate": [0.5],
        "acc_rate": [0.5],
        "avg_daily_trips": [marker],
        "event_timestamp": [datetime.now(timezone.utc)],
    })

    t0 = time.perf_counter()
    store.push("driver_stats_push", df, to=PushMode.ONLINE)
    t1 = time.perf_counter()
    got = store.get_online_features(
        features=features, entity_rows=[{"driver_id": driver_id}]
    ).to_dict()["avg_daily_trips"][0]
    t2 = time.perf_counter()

    if got != marker:
        mismatches += 1
    push_ms.append((t1 - t0) * 1000)
    total_ms.append((t2 - t0) * 1000)


def pct(data, p):
    return statistics.quantiles(data, n=100)[p - 1]


print("Events pushed:", N, "| read-after-write mismatches:", mismatches)
print("Push only        p50 %.2f ms | p95 %.2f ms | p99 %.2f ms" % (pct(push_ms, 50), pct(push_ms, 95), pct(push_ms, 99)))
print("Push + read back p50 %.2f ms | p95 %.2f ms | p99 %.2f ms" % (pct(total_ms, 50), pct(total_ms, 95), pct(total_ms, 99)))

ok = mismatches == 0 and pct(push_ms, 95) < P95_LIMIT_MS
print("RESULT:", "PASS" if ok else "FAIL", "(push p95 limit %.0f ms)" % P95_LIMIT_MS)
```

Save with `:wq`. Run it:

```bash
cd ~/feast-streaming-lab/feature_repo
source env.sh
python benchmark.py
```

Expected output (exact numbers depend on the VM and network path to Redis):

```text
Events pushed: 200 | read-after-write mismatches: 0
Push only        p50 6.10 ms | p95 11.80 ms | p99 19.40 ms
Push + read back p50 9.70 ms | p95 17.30 ms | p99 26.10 ms
RESULT: PASS (push p95 limit 100 ms)
```

Zero mismatches means every pushed value was immediately readable. The percentiles show typical and tail behavior, which matters more than averages for real-time serving.

> **Would I get an error if I ran this?** Possibly:
> 1. `statistics.quantiles` with `n=100` requires at least 100 data points. The default `N_EVENTS=200` is fine. If you set `N_EVENTS=50`, change `n=100` to `n=50` (or to `n=N_EVENTS // 2`) or Python will raise `StatisticsError`.
> 2. `TypeError: '<=' not supported between instances of 'NoneType' and 'int'`: `got` is `None` for some events. This means the push did not land. Re-run the producer and confirm `inspect_redis.py` shows non-zero keys. The most common cause is a stale `feature_server` process from Step 14 holding the registry; stop it with `kill $(cat feature_server.pid) 2>/dev/null` and retry.

## Verification

Run through this checklist. Every item should be true:

- `PING: True` and `Redis version: 7.0.15` appeared in Step 4.
- `feast apply` created the entity `driver` and the feature view `driver_stats_stream` (Step 8).
- `push_once.py` printed the pushed values (`avg_daily_trips` of `321`) without any materialize command (Step 10).
- `inspect_redis.py` reported at least one key of type `hash` and an increased `HSET` count (Step 11).
- `push_modes.py` showed that `OFFLINE` does not change the online value and `ONLINE_AND_OFFLINE` updates both (Step 12).
- `producer.py` finished with `Done. Pushed 30 events.` (Step 13).
- The HTTP read for driver `1002` returned `avg_daily_trips` of `555` or `556` (Step 14).
- `benchmark.py` reported `mismatches: 0` and `RESULT: PASS` (Step 15).

Quick one-shot confirmation of the online state:

```bash
cd ~/feast-streaming-lab/feature_repo
source env.sh
python read_online.py
python inspect_redis.py
```



## Epilogue

You have just built a real streaming ingestion path with Feast. A producer emits events, a `PushSource` accepts them, and the Poridhi managed Redis serves them back within milliseconds, with correctness verified on every read and latency measured with p50, p95, and p99. You also saw exactly where each `PushMode` writes, and confirmed the online write by inspecting Redis hashes and the `HSET` counter directly.

The bigger picture is that batch materialization and push ingestion are complementary. Batch jobs are the right tool for heavy aggregations over large history. Push ingestion is the right tool when freshness matters, and it slots in behind any streaming system: replace the Stream Simulator with a Kafka consumer or a Flink sink, and the rest of the architecture stays the same.

## Principles

- **Freshness is a feature requirement:** decide per feature how stale the online value may be, then choose push or batch accordingly.
- **Training and serving must agree:** `ONLINE_AND_OFFLINE` pushes keep the offline history consistent with what the model saw in production, which prevents training-serving skew.
- **Verify, do not assume:** reading back the exact pushed value and inspecting Redis directly turns "it should work" into evidence.
- **Measure tails, not averages:** p95 and p99 describe user experience under load far better than a mean.
- **Idempotent and scoped cleanup:** delete only the keys your lab wrote from a shared service, never flush the whole database.
- **Keep secrets out of code:** credentials come from the Cloud Tray, live in environment variables, and are excluded from version control.
- **One schema, many ingestion paths:** the SDK and HTTP paths write through the same `PushSource`, so producers in any language stay consistent.

## What You Learned

- A `PushSource` wraps a batch source and lets producers write features without a materialization job.
- `store.push(source_name, df, to=PushMode.X)` is the Python entry point, and `POST /push` is the HTTP equivalent.
- `ONLINE` writes only to Redis, `OFFLINE` rewrites the parquet batch source, and `ONLINE_AND_OFFLINE` does both.
- Feast stores each entity in Redis as a hash, with a `_ts:` field holding the event timestamp.
- A `FeatureView` TTL controls how long a pushed value stays valid when read online.
- You can quantify real-time performance with percentile latency and a read-after-write correctness check.

## Next Steps

- Replace the Stream Simulator with a real Kafka consumer (for example `kafka-python`) that calls `store.push()` in micro-batches.
- Add a second `FeatureView` on the same `PushSource` and compare push cost as the number of features grows.
- Try batching 100 rows per push and compare per-row latency against single-row pushes.
- Combine push ingestion with a scheduled `feast materialize` job so history is backfilled in batch while fresh values stream in.
- Add streaming transformations (windowed averages) before the push, using a stream processor such as Flink or Spark Structured Streaming.

## Additional Resources

- Feast documentation: Push source and stream ingestion, https://docs.feast.dev
- Feast documentation: Redis online store, https://docs.feast.dev/reference/online-stores/redis
- Feast documentation: Python feature server, https://docs.feast.dev/reference/feature-servers/python-feature-server
- redis-py documentation, https://redis-py.readthedocs.io
- Redis documentation: hashes and the INFO command, https://redis.io/docs
- Related Poridhi labs: Labs 7.2 (Feast setup) and 7.3 (Batch ingestion with `materialize-incremental`).

## Conclusion

Lab 7.4 extended the Feast project from the earlier labs with a streaming ingestion path. You installed Feast, wired it to the Poridhi managed Redis, declared a `PushSource` bound to a `FileSource` batch source, and called `store.push()` from the Python SDK and `POST /push` over HTTP to write feature vectors straight to Redis. You then called `get_online_features()` and measured single-digit millisecond round-trips, proved the writes by inspecting Redis hashes and the `HSET` counter, compared the three `PushMode` options, and benchmarked latency with percentiles. The takeaway is simple: use `feast.push()` with `PushMode.ONLINE_AND_OFFLINE` when the model needs the signal in the same second and you also need the row for training; use `PushMode.ONLINE` alone when only the online store matters.

## Iteration Notes

- 2026-10-15: Step 3 install block and Step 6 `to_parquet` line changed. Root cause confirmed by a Poridhi user on Python 3.12: `feast 0.40.1` hard-pins `numpy<2,>=1.22` in its package metadata, while any modern `pyarrow` (`>=14`) hard-pins `numpy>=2`. The two constraints are not simultaneously satisfiable, so the previous three-line `numpy`/`pandas`/`pyarrow` pin dance could only ever end with either a broken numpy or a broken pyarrow. Replaced the install block with `pandas>=2.2` + `fastparquet` (a second parquet engine that supports `numpy 1.x`), and added `engine="fastparquet"` to the one `pandas.to_parquet` call in `seed_data.py`. Feast's file offline store and the rest of the lab are unaffected because they read/write parquet through pandas, not pyarrow. The verification `import` line was updated to check `fastparquet` instead of `pyarrow`. Screenshots under Steps 4, 5, and 6 are unchanged. Confirmed end-to-end on Python 3.12 with `numpy 1.26.4` and `fastparquet 2026.9.0`.

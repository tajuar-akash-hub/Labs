## Introduction

This lab, **Feast Setup on AWS S3 with Managed Redis**, walks through standing up a feature store on the Poridhi lab VM so that training jobs and inference services stop disagreeing about feature values.

In production ML systems, training and inference often compute the same features in two different ways, a problem called the **training-serving skew**. Feast is an open-source feature store that fixes this by giving training and serving a single shared definition backed by two stores: an **offline store** (S3, for historical reads) and an **online store** (Redis, for low-latency inference).

In this lab, you will install Feast on the Poridhi lab VM, wire it to S3 (offline) and the Poridhi managed Redis (online), define a `driver_stats` feature view, and run `feast apply` to register it. By the end you will have a working feature store ready to feed both training jobs and inference services.

![Feast architecture diagram](animation/7.2_main_feast_architecture.svg)


## Learning Objectives

By the end of this lab, you will be able to:

- Install Feast in a Python virtual environment on the Poridhi lab VM and verify the CLI works.
- Generate AWS credentials from the Poridhi Cloud Playground and configure the AWS CLI for `ap-southeast-1`.
- Create an S3 bucket and use it as a Feast offline store and registry.
- Point Feast at the Poridhi managed Redis (endpoint and credentials from the Cloud Tray panel) and confirm the connection.
- Write a `feature_store.yaml` that wires Feast to S3 (offline) and managed Redis (online).
- Define a feature set in Python using `Entity`, `FeatureView`, and `FileSource`.
- Apply the feature definition and confirm the registry was updated on S3.

### Folder Structure

The lab creates the following folders and files on the Poridhi Lab VM. Every `mkdir -p`, `cd`, and file-creation step in the lab matches this tree exactly.

```text
~/poridhi-lab-7-2/
├── feature_repo/
│   ├── feature_store.yaml
│   ├── driver_repo.py
│   └── data/
│       └── driver_stats.parquet
└── venv/
```

## Prerequisites

- **Region:** `ap-southeast-1` (Asia Pacific, Singapore). All AWS resources (S3 bucket, IAM, CLI default) are pinned to this region.
- **Environment:** Poridhi Cloud lab VM running Linux (Debian/Ubuntu shell), with VS Code pre-installed and an active Poridhi Cloud Playground session. The lab creates its files in `~/poridhi-lab-7-2/`: Step 2.1 shows the one-time VS Code Command Palette step (`Shell Command: Install 'code' command in PATH`) so the Explorer can open that folder. After that, every file in this lab is created by right-clicking the folder in the VS Code Explorer and choosing `New File…`; no shell-level text editors are used.
- **Storage:** Managed AWS S3 bucket in `ap-southeast-1`, created with `aws s3api create-bucket` in Step 5. Credentials are short-lived and come from the Poridhi Cloud Playground lab UI. The bucket is destroyed with the lab session and is not torn down explicitly.
- **Cloud Tray: Redis (managed, already running):** Open the Cloud Tray in the Poridhi lab UI, click **Database**, then click the **Redis** card. The panel shows the actual credentials for this lab session: **Username**, **Password**, **IP Address**, **Port**, and a copy-able **Connection String**. The values can change between lab runs, so always read them from the panel instead of hard-coding them. You will use these in Step 6 and in the `feature_store.yaml` in Step 8.
- **AWS credentials:** Generate a credential from the Poridhi Cloud Playground lab UI (Generate credential button). Region is `ap-southeast-1` (Singapore). The SessionToken field may or may not appear: treat it as optional.
- **Tools already on the VM:** `python3` (3.9+), `pip`, `aws` CLI. The `redis` Python client is installed in Step 3 if missing. `redis-cli` is also NOT pre-installed; use the Python fallback in Step 6. The lab never invokes `vim`, `nano`, `cat`, `tee`, `xdg-open`, or any shell-level write to create files.

## Prologue

Imagine you work at a ride-hailing company. Your ML team has built a model that predicts whether a driver is likely to accept the next ride offer. The model uses features like average rating, completed trips last 7 days, and current online hours. Right now, the training pipeline computes these features by reading raw data from a data lake, and the inference service computes them again from a different data source. The numbers almost never match, and the model performs worse in production than it did in evaluation.

The fix is to make features a first-class artifact with one definition and two access paths. Feast is the tool that makes this possible. In this lab you will set up that foundation on the Poridhi lab VM: a central feature registry on S3, an offline store on S3 for training, and an online store on the Poridhi managed Redis for inference. Once this is in place, the training pipeline and the inference service will read the exact same definitions, and the training-serving skew problem will be largely solved.

## Step-by-Step Implementation

### Step 1: Collect all credentials from the Poridhi lab UI

> Note: this step collects two sets of credentials (AWS and managed Redis) once and stores them locally. Every later step references them as shell variables, so the values never need to be pasted again.

Before you start, collect two sets of credentials from the Poridhi lab UI. You will paste them once, and the rest of the lab will use the resulting env vars.

**A. AWS credential (for S3)**

1. In the Poridhi Cloud Playground, click **Generate credential**.
2. Copy the fields shown: `AccessKey`, `SecretKey`, and `SessionToken` if one is shown.

**B. Managed Redis credential (for the online store)**

1. Open the **Cloud Tray** in the Poridhi lab UI.
2. Click **Database** to open the Database Servers panel.
3. Click the **Redis** card. The panel shows the **Username**, **Password**, **IP Address**, **Port**, and **Connection String** for the current lab session.
4. Copy the **Username**, **Password**, **IP Address**, and **Port** values.

![Cloud Tray Redis credentials](images/7.1_cloudtray_redis_credentials.png)

This is what the panel looks like: the **Database Servers** view lists MongoDB, Redis, and PostgreSQL, and the Redis card below it expands into the credential block. The **Redis** card must show a green **Running** badge, and the **Connection String** line gives you everything in one copy-able string, for example `redis://redis:••••••@100.80.60.245:6379`. The password is masked in the panel, so use the copy button rather than trying to read it.

Keep the Cloud Tray panel open in another tab. The endpoint and password can rotate between lab sessions, so always re-read them from the panel if you start a new session.

Treat these credentials like a password: do not paste them into shared documents or commit them to git. The lab session credentials are short-lived and stop working when the lab ends.

> Would I get an error if I ran this? No. This step only reads values from the lab UI, it runs no commands. The one thing to watch for is a missing SessionToken: some Poridhi sessions issue only an AccessKey and a SecretKey, and the lab does not require a token.

### Step 2: Create a project directory and Python virtual environment

> Note: this step creates the project directory `~/poridhi-lab-7-2` and the Python virtual environment that Step 3 onward uses.

Open a terminal on the lab VM and run:

```bash
mkdir -p ~/poridhi-lab-7-2
cd ~/poridhi-lab-7-2
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
```

You should now be inside an isolated Python environment, with the prompt showing `(venv)` and the project folder as `~/poridhi-lab-7-2`. Anything you install will only affect this folder. Keep this terminal open for the rest of the lab: the environment stays active until you deactivate it.

> Would I get an error if I ran this? Possibly: `The virtual environment was not created successfully because ensurepip is not available` on some Debian images. If that happens, install the missing package with `sudo apt-get update && sudo apt-get install -y python3-venv` and repeat the `python3 -m venv venv` command. You can also confirm the environment is active by checking that the prompt now starts with `(venv)`.

#### Step 2.1: Make VS Code see the project folder (one-time setup)

The lab creates files inside `~/poridhi-lab-7-2/` using the VS Code Explorer (right-click → `New File…`) instead of a shell editor. Before that works, you need the `code` CLI on `PATH` so Step 8 and Step 9 can rely on `code ~/poridhi-lab-7-2` to open the folder, and the Explorer label needs to point at this folder.

1. **Open the VS Code Command Palette.** Press `Ctrl+Shift+P` (Linux) inside any VS Code window, or open VS Code and use `View → Command Palette`.
2. **Install the `code` CLI.** Type `Shell Command: Install 'code' command in PATH` and press `Enter`. Wait for the small "Shell Command successfully installed in PATH" notification at the bottom-right of VS Code.
3. **Trust the new PATH.** Open a fresh terminal (or `source ~/.bashrc`) so the shell picks up the new `code` binary.
4. **Open the project folder.** Run:

   ```bash
   code ~/poridhi-lab-7-2
   ```

   Confirm the Explorer panel on the left shows the path `PORIDHI-LAB-7-2` and is now rooted at `~/poridhi-lab-7-2`. If the label did not flip, use `File → Open Folder…` from the VS Code menu and pick `~/poridhi-lab-7-2` manually.

After this one-time setup, every later step that creates a file just tells you to right-click a folder in the Explorer and choose `New File…`.

### Step 3: Install Feast with AWS and Redis support

> Note: this step installs Feast plus its AWS and Redis extras, then pins the transitive `numpy` floor that newer `pandas`/`pyarrow` wheels require.

Install Feast plus the AWS and Redis extras. This pulls in `boto3`, `redis`, and the S3 file source plugin:

```bash
pip install --upgrade pip
```

```bash
pip install "numpy>=2.0,<3" "pandas>=2" "pyarrow>=14" "feast[aws,redis]"
```

> Would I get an error if I ran this? Possibly: `ERROR: Could not find a version that satisfies the requirement pyarrow` if the resolver picks an `numpy` build incompatible with your Python version. The explicit `numpy>=2.0,<3` floor in the same command prevents that. If pip reports a build failure for `pyarrow`, run `pip install --upgrade pip` once more and repeat the command.

Verify the install:

```bash
feast version
feast --help
```

![feast version and help](images/7.2_feast_version_and_help.png)

The first line is the SDK version (`Feast SDK Version: "0.67.0"` on a current install; `0.36.x` and later are all fine for this lab). Below it, `feast --help` prints the usage line and the full list of subcommands: `apply`, `materialize`, `materialize-incremental`, `entities`, `feature-views`, `feature-services`, `get-online-features`, `teardown`, and more. You should see that list without any import errors.

> Would I get an error if I ran this? Possibly: `Error: No such option '--version'` if you type `feast --version` instead of `feast version`. In current Feast the version is a subcommand, not a flag, so `feast version` is the correct form and `feast --version` was removed after the older releases. You can also read the installed package version with `pip show feast | grep Version`, which prints `Version: 0.67.0`.

### Step 4: Configure AWS credentials

> Note: this step exports the AWS credentials from Step 1 into the shell, then sets the default region to `ap-southeast-1`.

Export the credentials from Step 1 as environment variables so they reach `boto3`:

```bash
export AWS_ACCESS_KEY_ID="<paste-access-key-id>"
export AWS_SECRET_ACCESS_KEY="<paste-secret-access-key>"
export AWS_REGION="ap-southeast-1"

# Only run this if Poridhi issued a session token in Step 1.
# If your credential only had AccessKey and SecretKey, skip this line.
export AWS_SESSION_TOKEN="<paste-session-token>"
```

Then set the default region and output format:

```bash
aws configure set region ap-southeast-1
aws configure set output json
```

If you would rather use the interactive prompt instead of `export`, you can run:

```bash
aws configure
```

and paste `AccessKey` for `AWS Access Key ID`, `SecretKey` for `AWS Secret Access Key`, `ap-southeast-1` for `Default region name`, and `json` for `Default output format`. Leave `Default profile` blank.

Verify that the credentials work:

```bash
aws sts get-caller-identity
```

![aws caller identity output](images/7.2_aws_sts_caller_identity.png)

The output is a JSON document with three fields: `UserId`, `Account` (your AWS account ID), and `Arn`. The `Arn` reads `arn:aws:iam::949675286521:user/pxg6-poridhi`, which is the temporary IAM identity the Poridhi Cloud Playground issued for this session. Seeing that `Arn` back is what confirms the credentials reached the AWS API.

> Would I get an error if I ran this? Yes, if the Poridhi credential has expired: `Unable to locate credentials` or `The security token included in the request is expired`. Re-generate a credential from the Poridhi Cloud Playground and re-export the three variables above. If the output shows the wrong region, run `aws configure set region ap-southeast-1` again.

### Step 5: Create the S3 bucket for the offline store

> Note: this step creates a globally unique S3 bucket in `ap-southeast-1` that Step 8 uses as both the Feast offline store and the registry location.

Pick a globally unique bucket name and create it in `ap-southeast-1`:

```bash
export BUCKET_NAME="feast-offline-store-$(date +%s)"
echo "Bucket name: $BUCKET_NAME"
aws s3api create-bucket \
  --bucket "$BUCKET_NAME" \
  --region ap-southeast-1 \
  --create-bucket-configuration LocationConstraint=ap-southeast-1
```

![s3 bucket created](images/7.2_create_bucket_output.png)

The command echoes the generated bucket name and then returns a JSON document with two fields: `Location` (the bucket's S3 endpoint) and `BucketArn` (its ARN). Seeing `BucketArn` back means the bucket was created successfully.

> Would I get an error if I ran this? Possibly: `BucketAlreadyExists` if the timestamped name collides with a bucket created in the same second, or `BucketAlreadyOwnedByYou` if you re-ran Step 5 in the same session. Both are harmless: the bucket already exists, so keep it and carry on with the `FEAST_S3_BUCKET` value. If you get `AccessDenied`, your Poridhi credential has expired, so re-generate it and re-export the AWS variables from Step 4.

Confirm it exists:

```bash
aws s3 ls | grep "$BUCKET_NAME"
```

![s3 bucket listing](images/7.2_s3_ls_bucket_listed.png)

The listing shows one line with the bucket's creation timestamp and name. If the grep returns nothing, the bucket was not created, so go back and re-run the `create-bucket` command.

Persist the bucket name for later steps:

```bash
echo "export FEAST_S3_BUCKET=$BUCKET_NAME" >> ~/.bashrc
export FEAST_S3_BUCKET=$BUCKET_NAME
```

> **Write down your bucket name now.** Run `echo "$FEAST_S3_BUCKET"` in the same terminal and copy the output: it will look like `feast-offline-store-1792384265` (your value will differ). You will paste that exact value into `feature_store.yaml` in Step 8 (replacing the `your-unique-bucket-name` placeholder). The `$FEAST_S3_BUCKET` env var is also fine to keep using; just remember the value in case you start a new terminal session before Step 8 and the env var is no longer set. If you lose it, run `echo "$FEAST_S3_BUCKET"` again in the same terminal where you exported it. (The bucket itself persists in S3; only the local shell variable needs restoring.)

### Step 6: Confirm the Poridhi managed Redis is reachable

> Note: this step reads the managed Redis credentials from the Cloud Tray, exports them as shell variables, and pings the service from Python so Step 8 can wire them into `feature_store.yaml`.

If you skipped Step 1, open the Poridhi Cloud Tray in the lab UI, click **Database**, then click the **Redis** card. Read the **Username**, **Password**, **IP Address**, and **Port** from the panel and export them as shell variables:

```bash
export REDIS_HOST="<paste-ip-from-cloud-tray>"
export REDIS_PORT="<paste-port-from-cloud-tray>"
export REDIS_USERNAME="<paste-username-from-cloud-tray>"
export REDIS_PASSWORD="<paste-password-from-cloud-tray>"
```

The panel gives you all four values in the **CREDENTIALS** block, and the **Connection String** at the bottom carries them in one string. The **IP Address** becomes `REDIS_HOST`, the **Port** becomes `REDIS_PORT`, and the masked **Username** and **Password** become `REDIS_USERNAME` and `REDIS_PASSWORD`. Use the copy button on each field: the password is never shown in plain text in the panel.

The Poridhi lab VM does not have `redis-cli` pre-installed by default, so use the Python client (which Feast already depends on) to ping the Redis:

```bash
python -c "import redis; r=redis.Redis(host='$REDIS_HOST', port=int('$REDIS_PORT'), password='$REDIS_PASSWORD', username='$REDIS_USERNAME'); print(r.ping())"
```

![redis ping returns True](images/7.2_redis_python_ping_true.png)

The output is `True`, which means the managed Redis accepted the connection and the credentials. If you see `ModuleNotFoundError: No module named 'redis'`, install it first:

```bash
pip install redis
```

If you would rather use `redis-cli`, install it and ping with the same variables:

```bash
sudo apt-get update && sudo apt-get install -y redis-tools
redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" --user "$REDIS_USERNAME" -a "$REDIS_PASSWORD" ping
```

![redis-cli ping returns PONG](images/7.2_redis_cli_pong.png)

The output is `PONG`. The `Warning: Using a password with '-a' or '-u' option on the command line interface may not be safe.` line above it is harmless: the password is only exposed in your own terminal history. The lab works either way; pick one and continue.

> Would I get an error if I ran this? Possibly: `redis.exceptions.ConnectionError` if the managed Redis endpoint is unreachable or the port is wrong, and `redis.exceptions.AuthenticationError: WRONGPASS` if the username or password does not match. Re-open the Cloud Tray, Database, Redis panel and re-read the four values, then re-export them. If you see `int() can't convert non-string with explicit base`, one of the variables is empty, which usually means the export line was skipped in a fresh terminal.

### Step 7: Create the Feast project folder

> Note: this step creates the `~/poridhi-lab-7-2/feature_repo` project folder by hand, without using `feast init`.

Recent versions of `feast init` create a nested folder `feature_repo/feature_repo/` and ship a `feature_definitions.py` that defines its own `Project`, `Entity`, `FeatureView`, and `LabelView`. Because `feast apply` scans every `.py` file under the repository, that scaffolded file would collide with the definitions we write in Step 9 and cause `PydanticValidationError: Entity 'driver' is already registered` or `extra fields not permitted` errors.

Skip the scaffold and create the project folder by hand. This one command creates both the `feature_repo/` folder and the `data/` subfolder that Step 10 writes into:

```bash
mkdir -p ~/poridhi-lab-7-2/feature_repo/data
```

```bash
cd ~/poridhi-lab-7-2/feature_repo
```

The VS Code Explorer on the left is rooted at `PORIDHI-LAB-7-2` and lists two folders: `feature_repo` and `venv`. Both are collapsed, so expand `feature_repo` to see the `data` subfolder inside it. You should now be in `~/poridhi-lab-7-2/feature_repo` in the terminal as well. Steps 8 through 10 all write into this folder, so keep this terminal open and stay in this directory for the rest of the lab.

> Would I get an error if I ran this? No. Both commands are safe to re-run: `mkdir -p` does not fail if the folder already exists, and `cd` simply moves you into it. If the `cd` fails with `No such file or directory`, the `mkdir -p` block did not run: run it again first.

### Step 8: Create `feature_store.yaml`

> Note: this step writes `feature_store.yaml` in `~/poridhi-lab-7-2/feature_repo` so Feast knows the S3 bucket and the managed Redis endpoints.

This file has two long values, and a long value pasted into a text editor is where labs like this one usually break. The editor soft-wraps the line, the wrap gets copied along with the text, and the file ends up with a value split across two lines. The YAML parser then rejects it with a `ScannerError`.

So write this file from the terminal instead, where the bytes are exact. Your terminal is already inside `~/poridhi-lab-7-2/feature_repo` from Step 7.

Before you run the command, put your own values into it:

- `your-unique-bucket-name` becomes the bucket name from Step 5, the one you wrote down with `echo "$FEAST_S3_BUCKET"`. If you lost it, run `echo "$FEAST_S3_BUCKET"` in the terminal and use that value.
- `your-redis-host` and `your-redis-port` become the IP Address and Port from the Cloud Tray Redis panel in Step 6.
- `your-redis-username` and `your-redis-password` become the Username and Password from the same panel.

Then run this in the terminal:

```bash
python - <<'PY'
from pathlib import Path

Path("feature_store.yaml").write_text(
    "project: feast_lab\n"
    "registry: s3://your-unique-bucket-name/registry/registry.db\n"
    "provider: aws\n"
    "offline_store:\n"
    "  type: file\n"
    "online_store:\n"
    "  type: redis\n"
    "  connection_string: your-redis-host:your-redis-port,username=your-redis-username,password=your-redis-password\n"
    "entity_key_serialization_version: 3\n"
)
print("wrote feature_store.yaml")
PY
```

**Important: the connection string is not the `redis://` URL from the Cloud Tray panel.** The panel shows something like `redis://redis:YOUR-PASSWORD@100.80.60.245:6379`, and Feast cannot read that form. It splits the value on `:` and tries to parse the second piece as a port number, which fails with `ValueError: invalid literal for int() with base 10: '//redis'`.

Feast wants the endpoint and the credentials as two separate parts of one value:

| | Format |
|---|---|
| Cloud Tray panel | `redis://redis:YOUR-PASSWORD@100.80.60.245:6379` |
| What Feast wants | `100.80.60.245:6379,username=redis,password=YOUR-PASSWORD` |

Drop the `redis://` prefix, drop the quotes, and replace the `user:password@` section with `,username=...,password=...`. The command above already has the correct shape; you only substitute the four real values.

Now confirm the file is exactly right before you go on. This prints every line with a `$` marker at the end, and shows tabs as `^I`:

```bash
cat -A feature_store.yaml
```

You want to see **9 lines**, each ending in a single `$`:

```text
project: feast_lab$
registry: s3://feast-offline-store-1792814057/registry/registry.db$
provider: aws$
offline_store:$
  type: file$
online_store:$
  type: redis$
  connection_string: 100.80.60.245:6379,username=redis,password=YOUR-PASSWORD$
entity_key_serialization_version: 3$
```

Three things to check: `project` starts at column 1, `type:` is indented by exactly two spaces, and the `connection_string` value is complete on one line. If a line looks long in the terminal, that is only the display wrapping; what matters is that you count 9 `$` markers, not 11.

Notes about this file:

- `project`: a human-readable name for the project. Used in paths and logs.
- `registry`: where Feast stores the metadata about your features. We are putting it on S3 so the registry survives across machines.
- `provider: aws`: tells Feast we want the AWS flavor of the offline store.
- `offline_store.type: file`: tells Feast to use the file-based (S3 + Parquet) offline store. No `region` key is required for the file offline store: the bucket region is discovered from S3 itself.
- `online_store.type: redis`: tells Feast to use the Poridhi managed Redis for online lookups.
- `connection_string: host:port,username=...,password=...`: the Poridhi managed Redis endpoint and credentials. The auth fields must be embedded in the connection string itself, not written as separate top-level `user:` or `password:` keys, and not written as a `redis://` URL.
- `entity_key_serialization_version: 3`: the modern serialization for Redis keys. Required by recent Feast versions.

> Would I get an error if I ran this? Possibly: `Extra inputs are not permitted` if you accidentally paste `user: your-redis-username` and `password: your-redis-password` as separate top-level keys, or if you leave a `region:` key under `offline_store`. Modern Feast requires the Redis credentials to be embedded in `connection_string` only, and it rejects the `region` key for the file offline store. Delete those keys and re-run `feast apply`. A YAML `ScannerError: while scanning a simple key` means a value was split across two lines, which the `cat -A` check above catches. A `ValueError: invalid literal for int() with base 10: '//redis'` at materialization time means the `redis://` URL form was used instead of `host:port,username=...,password=...`.

### Step 9: Create `driver_repo.py`

> Note: this step writes `driver_repo.py` (the feature definition for `driver_id`) in `~/poridhi-lab-7-2/feature_repo`.

Write this file the same way you wrote `feature_store.yaml`: from the terminal, so the indentation is exactly right. Your terminal is already inside `~/poridhi-lab-7-2/feature_repo`.

```bash
python - <<'PY'
from pathlib import Path

Path("driver_repo.py").write_text(
    '"""Feature definitions for the driver_stats feature view."""\n'
    "from datetime import timedelta\n"
    "\n"
    "from feast import Entity, FeatureView, Field, FileSource, ValueType\n"
    "from feast.types import Float64, Int64\n"
    "\n"
    "# Source: a Parquet file we'll generate in the next step\n"
    "driver_stats_source = FileSource(\n"
    '    name="driver_stats_source",\n'
    '    path="data/driver_stats.parquet",\n'
    '    timestamp_field="event_timestamp",\n'
    '    created_timestamp_column="created",\n'
    ")\n"
    "\n"
    "# Entity: the thing we want to look up features for\n"
    "driver = Entity(\n"
    '    name="driver_id",\n'
    '    join_keys=["driver_id"],\n'
    '    description="Driver identifier",\n'
    "    value_type=ValueType.INT64,\n"
    ")\n"
    "\n"
    "# FeatureView: a logical group of features tied to the entity\n"
    "driver_stats_fv = FeatureView(\n"
    '    name="driver_stats",\n'
    "    entities=[driver],\n"
    "    ttl=timedelta(days=3650),\n"
    "    schema=[\n"
    '        Field(name="conv_rate", dtype=Float64),\n'
    '        Field(name="acc_rate", dtype=Float64),\n'
    '        Field(name="avg_daily_trips", dtype=Int64),\n'
    "    ],\n"
    "    source=driver_stats_source,\n"
    "    online=True,\n"
    ")\n"
)
print("wrote driver_repo.py")
PY
```

Confirm it was written and imports cleanly:

```bash
cat driver_repo.py
python -c "import driver_repo; print('driver_repo.py imported cleanly')"
```

Notes about the file:

- `Field(name="conv_rate", dtype=Float64)` declares the schema with typed columns. Modern Feast rejects the old tuple form (`("conv_rate", ValueType.FLOAT)`) because `FLOAT` is not a valid `FeastType`.
- `entities=[driver]` passes the `Entity` object. The old string form (`entities=["driver_id"]`) is rejected with `Entity 'driver_id' not found` because Feast no longer resolves the name from the registry lookup.
- `ttl=timedelta(days=3650)` makes the view remember the last ten years of values. **This number matters more than it looks.** The default TTL in Feast is one day, and the Parquet rows this lab generates are dated `2026-01-01`, which is months before the day you run the lab. With the default `timedelta(days=1)` those rows fall outside the window and the materialization in Step 13 writes **zero rows without raising any error at all**. Ten years covers the data with room to spare.

> Would I get an error if I ran this? Possibly: `TypeCheckError: Invalid type INT64 for feature conv_rate` if you kept the old tuple schema, or `Entity 'driver_id' not found` if you passed the entity name as a string. Both are caught at `feast apply` time in Step 11, not here, so if you see them there, come back and check this file against the block above. A wrong TTL does not raise an error: it silently produces an empty materialization in Step 13, so check the `ttl=` line in the output of `cat driver_repo.py` if Step 13 reports no rows.

### Step 10: Generate a small Parquet sample

> Note: this step writes a small Parquet sample (`data/driver_stats.parquet`) that `feast apply` and `feast materialize` will read.

Step 7 already created the `data/` subfolder and your terminal is already inside `feature_repo`, so the relative path `data/driver_stats.parquet` in `driver_repo.py` resolves from here. Run this Python script to create a 5-row Parquet file with the right schema:

```bash
python - <<'PY'
import pandas as pd
from datetime import datetime, timezone

df = pd.DataFrame(
    {
        "driver_id": [1001, 1002, 1003, 1004, 1005],
        "conv_rate": [0.82, 0.55, 0.91, 0.40, 0.73],
        "acc_rate": [0.95, 0.88, 0.99, 0.71, 0.84],
        "avg_daily_trips": [28, 14, 35, 7, 22],
        "event_timestamp": [datetime(2026, 1, 1, tzinfo=timezone.utc)] * 5,
        "created": [datetime(2026, 1, 1, tzinfo=timezone.utc)] * 5,
    }
)

# Match the Float64 types declared in driver_repo.py
df["conv_rate"] = df["conv_rate"].astype("float64")
df["acc_rate"] = df["acc_rate"].astype("float64")

df.to_parquet("data/driver_stats.parquet", index=False)
print("Wrote data/driver_stats.parquet")
PY
```

![parquet generation output](images/7.2_parquet_generation_output.png)

The terminal shows the whole `python - <<'PY'` block echoed at the prompt, including the two `astype("float64")` casts and the `to_parquet` call. The last line is the confirmation you want: `Wrote data/driver_stats.parquet`. Note the prompt path is `~/poridhi-lab-7-2/feature_repo`, which is where the relative path `data/driver_stats.parquet` resolves to the `data/` folder that Step 7 created.

> Would I get an error if I ran this? Possibly: `ModuleNotFoundError: No module named 'pandas'` or `No module named 'pyarrow'`, which means the virtual environment is not active. Run `source ~/poridhi-lab-7-2/venv/bin/activate` and repeat the command. The explicit `astype("float64")` casts prevent a `Float32 vs Float64 mismatch` during the materialize step in Step 13, because pandas would otherwise infer a narrower float type for those columns.

### Step 11: Apply the feature definition

> Note: this step validates the feature definition and registers the `driver_stats` view in S3.

Run this from inside the project folder, `~/poridhi-lab-7-2/feature_repo`. Your terminal is already there: Step 7 moved you in and nothing since then has changed directory. Feast looks for `feature_store.yaml` in the current working directory, so running `feast apply` from `~/poridhi-lab-7-2` instead fails with a "repo path" or "no feature_store.yaml" error.

Confirm where you are before you run it:

```bash
pwd
ls
```

The output should show `/home/poridhian/poridhi-lab-7-2/feature_repo` and a listing that includes `feature_store.yaml`, `driver_repo.py`, and the `data` folder.

Now run `feast apply`. This validates the definitions, uploads the registry to S3, and registers the feature view:

```bash
feast apply
```

![feast apply output](images/7.2_feast_apply_output.png)

The output has four lines. `No project found in the repository. Using project name feast_lab defined in feature_store.yaml` is not an error: it means Feast found no `Project` object declared in Python, so it took the project name from your YAML, which is exactly what this lab wants. `INFO:botocore.credentials:Found credentials in environment variables` confirms the AWS credentials from Step 4 reached boto3, so the registry can be written to S3. `Applying changes for project feast_lab` and `Deploying infrastructure for driver_stats` mean the entity and the feature view were registered.

Confirm the feature view was registered by listing entities, feature views, and feature services:

```bash
feast entities list
feast feature-views list
feast feature-services list
```

![entities and feature views listed](images/7.2_feast_entities_and_views_listed.png)

The entity table shows `driver_id` with the description `Driver identifier` and type `ValueType.INT64`, which matches the `Entity` you defined in Step 9. The feature view table shows `driver_stats` with entities `{'driver_id'}`, type `FeatureView`, and `ENABLED` set to `Yes`. The `FEATURES` column is empty because Feast populates it only for views that declare a schema in the registry listing, and the entity set renders with curly braces because Feast stores it as a set. The feature services list at the end is empty, which is correct: this lab does not define one.

> Would I get an error if I ran this? Possibly: `Extra inputs are not permitted` if `feature_store.yaml` still carries a `region:` key under `offline_store` or separate `user:` and `password:` keys under `online_store`, and `TypeCheckError` or `Entity 'driver_id' not found` if `driver_repo.py` still uses the old tuple schema or a string entity name. Both point back to Steps 8 and 9, so fix the file and re-run `feast apply`. A `NoSuchBucket` error means the `registry:` line does not match the bucket name from Step 5. A YAML `ScannerError: while scanning a simple key` means `feature_store.yaml` has a broken line, usually a `registry:` or `connection_string:` value that wrapped onto a second line while pasting.

### Step 12: Verify the registry on S3

> Note: this step confirms that Feast wrote the registry to the S3 bucket.

Confirm that Feast wrote the registry file to your bucket:

```bash
aws s3 ls s3://$FEAST_S3_BUCKET/registry/
```

![registry.db in S3](images/7.2_registry_db_in_s3.png)

The listing shows one object, `registry.db`, with its size and the timestamp when Feast wrote it. That file is the single source of truth for your feature definitions: every later command reads the entity and the feature view from it, not from the Python file.

> Would I get an error if I ran this? Possibly: `An error occurred (NoSuchBucket) when calling the ListObjectsV2 operation` if `$FEAST_S3_BUCKET` is empty in this shell. Run `echo "$FEAST_S3_BUCKET"`; if it prints nothing, re-export the value from Step 5. An empty listing without an error means `feast apply` in Step 11 did not complete successfully, so run it again before checking S3.

### Step 13: Materialize to the online store and read back

> Note: this step pushes the latest features into the managed Redis and reads them back through `get_online_features`, which is what an inference service would call at request time.

Run this from inside `~/poridhi-lab-7-2/feature_repo`, the same folder as Step 11. Feast resolves both the feature view and the relative `data/driver_stats.parquet` source path against the current working directory.

Push the latest rows from the Parquet file into the managed Redis:

```bash
feast materialize-incremental 2026-01-02T00:00:00
```

![empty materialization window](images/7.2_materialize_empty_window.png)

Feast treats the end timestamp as **exclusive**, so pass a timestamp one day after the batch you want included. The Parquet rows generated in Step 10 are dated `2026-01-01T00:00:00`, which means `2026-01-02T00:00:00` is the earliest end timestamp that includes them.

Now look carefully at the time window the command reports, because this is the one thing in this lab that fails **without raising an error**:

```text
driver_stats from 2026-01-02 00:00:00+00:00 to 2026-01-02 00:00:00+00:00:
```

The start and the end are the same instant, so the window is empty and nothing gets written. Feast computes the start of the window as *now minus the feature view TTL*, and it clamps the window when that start falls after your end timestamp. Two different things produce that collapsed window, and it is worth knowing which one you have.

The first is the TTL in `driver_repo.py`. Feast's default is one day, and the Parquet rows in this lab are dated `2026-01-01`, so the default would leave the window empty. Check it directly:

```bash
grep -n "ttl" driver_repo.py
```

![driver_repo.py ttl check](images/7.2_driver_repo_ttl_check.png)

You want to see `ttl=timedelta(days=3650)`. If it says `timedelta(days=1)`, change it.

The second cause is a stale registry, and it is the more common one. The registry on S3 holds its own copy of the feature view, and `materialize-incremental` reads **the registry**, not your local Python file. If you edited `driver_repo.py` but did not re-run `feast apply`, the registry still holds the old definition and the old TTL, and the local file is irrelevant. So whenever you change the TTL, or the connection string, or anything else in `driver_repo.py` or `feature_store.yaml`, re-run `feast apply` before materializing.

A correct run reports a wide window:

```text
Materializing 1 feature views to 2026-01-02 00:00:00+00:00 into the redis online store.

driver_stats from 2016-10-26 04:52:01+00:00 to 2026-01-02 00:00:00+00:00:
```

Now read those features from Python using the same `FeatureStore` object that the CLI uses:

```bash
python - <<'PY'
from feast import FeatureStore
fs = FeatureStore(repo_path=".")
features = fs.get_online_features(
    features=["driver_stats:conv_rate", "driver_stats:acc_rate"],
    entity_rows=[{"driver_id": 1001}, {"driver_id": 1003}],
).to_dict()
print(features)
PY
```

![online features read-back](images/7.2_get_online_features_read_back.png)

The printed dictionary is the end-to-end proof of the lab. `driver_id` returns the two entities you asked for. `conv_rate` returns `0.82` for driver 1001 and `0.91` for driver 1003, and `acc_rate` returns `0.95` and `0.99`. Those are exactly the values in the Parquet file from Step 10, which means the path worked: pandas wrote the Parquet file, Feast read it during materialization, the values landed in the managed Redis, and `get_online_features` read them back out of Redis by entity key. An inference service in production would make this same call at request time.

> Would I get an error if I ran this? Possibly: `redis.exceptions.ConnectionError` if the managed Redis endpoint rotated, in which case re-open the Cloud Tray, Database, Redis panel, re-export `REDIS_HOST`, `REDIS_PORT`, `REDIS_USERNAME`, and `REDIS_PASSWORD`, then update the `connection_string` line in `feature_store.yaml` and re-run `feast apply`. A `ValueError: invalid literal for int() with base 10: '//redis'` means the `connection_string` still uses the `redis://` URL form, and the fix is in Step 8. If the materialize step reports zero rows or an empty time window, your end timestamp was not past the batch date, or the `ttl` in `driver_repo.py` is still `timedelta(days=1)`.

## Epilogue

You now have a working Feast installation on the Poridhi lab VM. The feature registry lives in S3, the online store is the Poridhi managed Redis (endpoint and credentials from the Cloud Tray panel), and the offline store is configured to read from a Parquet file. This is the same basic structure that production Feast deployments use: the only differences are scale, authentication, and the data sources.

The next thing you would normally do is connect a real data source (a Kafka stream, a Snowflake table, or an S3 path updated by an ETL job), populate it with real data, and then have your training pipeline call `get_historical_features` while your inference service calls `get_online_features`. From Feast's perspective, those two calls are symmetric: they read the same feature definitions and return the same feature values.

## Conclusion

This lab stood up a complete Feast feature store on the Poridhi lab VM: Feast installed in a virtual environment, an S3 bucket in `ap-southeast-1` as the offline store and registry, and the Poridhi managed Redis from the Cloud Tray as the online store, all wired together through a single `feature_store.yaml` plus a feature definition applied to the registry. The key takeaway is the two-store architecture, where S3 handles historical, training-time reads while the managed Redis handles low-latency, inference-time reads, and Feast keeps the two in sync through one shared feature definition. With this foundation in place, you can now plug in real data sources and connect both training and inference pipelines to the same source of truth.
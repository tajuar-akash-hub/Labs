#!/usr/bin/env bash
# setup.sh
# Lab 7.1 (Feature Store Concepts, Beginner Friendly) starter scaffold.
#
# Run this once from the Feature_store_labs/ folder:
#     bash setup.sh
#
# It creates exactly the 3 files shown in the lab's first folder diagram:
#     fs-beginner/docker-compose.yml
#     fs-beginner/client/init.sql
#     fs-beginner/client/requirements.txt
#
# The 5 Python scripts (seed.py, leaky.py, pitc.py, materialize.py, online.py)
# are NOT created here on purpose: the lab walks you through writing each one
# with a comment explaining what it does. Skip this script if you prefer to
# create everything by hand.
#
# This script refuses to overwrite an existing docker-compose.yml.

set -euo pipefail

# Resolve the directory this script is in, so it works no matter where you run it from.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PROJECT_DIR="$SCRIPT_DIR/fs-beginner"
COMPOSE_FILE="$PROJECT_DIR/docker-compose.yml"

# Safety: refuse to clobber work in progress.
if [ -f "$COMPOSE_FILE" ]; then
    echo "ERROR: $COMPOSE_FILE already exists."
    echo "Refusing to overwrite. Delete the fs-beginner folder first if you want a clean slate."
    exit 1
fi

echo "Creating folder structure under $PROJECT_DIR ..."
mkdir -p "$PROJECT_DIR/client"

# ---- docker-compose.yml --------------------------------------------------
cat > "$COMPOSE_FILE" <<'EOF'
# We are running 3 "services" (containers):
#   1. postgres  - the offline store (history)
#   2. redis     - the online store (latest snapshot, fast)
#   3. client    - a Python playground where we run our scripts

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
EOF

# ---- client/init.sql -----------------------------------------------------
cat > "$PROJECT_DIR/client/init.sql" <<'EOF'
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
EOF

# ---- client/requirements.txt --------------------------------------------
cat > "$PROJECT_DIR/client/requirements.txt" <<'EOF'
psycopg2-binary
redis
EOF

# ---- Report ---------------------------------------------------------------
echo ""
echo "Scaffold created. Files written:"
echo "  $COMPOSE_FILE"
echo "  $PROJECT_DIR/client/init.sql"
echo "  $PROJECT_DIR/client/requirements.txt"
echo ""
echo "Next steps (from the lab):"
echo "  cd $PROJECT_DIR"
echo "  docker compose up -d"
echo "  docker compose exec client pip install -r /app/requirements.txt"
echo ""
echo "Then write client/seed.py, client/leaky.py, client/pitc.py,"
echo "client/materialize.py, and client/online.py by following the lab."
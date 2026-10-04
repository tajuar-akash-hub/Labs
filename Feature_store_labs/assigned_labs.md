![alt text](image.png)

# ◆ MODULE 7: Feature Stores

  Lab #: 7.1
  Title: Feature Store Concepts
  Level: Beginner
  Type: Standalone
  Key Focus: Sketch the offline/online store split, point-in-time
    correctness (PITC), and feature freshness on a whiteboard
  example.
  Lab Status: Pending
  ────────────────────────────────────────
  Lab #: 7.2
  Title: Feast Setup
  Level: Intermediate
  Type: Standalone
  Key Focus: Install Feast, configure a feature_store.yaml with S3
    (offline) + Redis (online), and apply a feature definition.
  Lab Status: Pending
  ────────────────────────────────────────
  Lab #: 7.3
  Title: Batch Feature Ingestion
  Level: Intermediate
  Type: Standalone
  Key Focus: Run feast materialize-incremental, then build a
    historical feature DataFrame via get_historical_features() for
    training.
  Lab Status: Pending
  ────────────────────────────────────────
  Lab #: 7.4
  Title: Streaming Ingestion
  Level: Advanced
  Type: Standalone
  Key Focus: Push features directly to the online store via
    feast.push() and verify they appear in Redis within milliseconds.
  Lab Status: Pending
  ────────────────────────────────────────
  Lab #: 7.5
  Title: Real-Time Serving
  Level: Advanced
  Type: Standalone
  Key Focus: Call get_online_features() from a Python client and
    measure end-to-end retrieval latency (target <10ms).
  Lab Status: Pending
  ────────────────────────────────────────
  Lab #: 7.6
  Title: Spark → Feast Batch
  Level: Intermediate
  Type: Spark → Feast
  Key Focus: Run a Spark job that computes daily features and feeds
    them into the Feast offline store for the next materialize run.
  Lab Status: Pending
  ────────────────────────────────────────
  Lab #: 7.7
  Title: Kafka → Feast Stream
  Level: Advanced
  Type: Kafka/Faust → Feast
  Key Focus: Consume Kafka events, compute real-time features, and
    push them to Feast via the streaming push API.
  Lab Status: Pending
  ────────────────────────────────────────
  Lab #: 7.8
  Title: FastAPI ↔ Feast → Redis
  Level: Advanced
  Type: FastAPI ↔ Feast → Redis
  Key Focus: Build a FastAPI /predict endpoint that calls Feast's
    online store and returns a recommendation in <50ms.
  Lab Status: Pending
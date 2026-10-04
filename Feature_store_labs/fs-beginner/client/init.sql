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

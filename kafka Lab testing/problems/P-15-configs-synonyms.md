# [s2-ep04-lab-02] P-15: `kafka-configs --describe` prints a header line and `synonyms={…}` that the expected block omits

> **Observed on the VM, 2026-11-10** (Chapter 5.3).

| Field | Value |
|---|---|
| **Lab ID** | `s2-ep04-lab-02` |
| **Section** | 5.3 Implementation: Durable Producer and Topic (the `kafka-configs --describe` block) |
| **Kind** | Content (expected-output block does not match real output) |
| **Severity** | **4 Polish** (the check still passes; the doc's expected block is simply incomplete) |
| **Commit tested** | doc as published 2026-11-10 (doc commit not recorded) |

## Steps to reproduce

1. Run Chapter 5.3 as written:

```bash
kafka kafka-configs $B --alter --entity-type topics --entity-name payments.authorized \
  --add-config min.insync.replicas=2,unclean.leader.election.enable=false
kafka kafka-configs $B --describe --entity-type topics --entity-name payments.authorized
```

## Expected

README 5.3:

```text
Completed updating config for topic payments.authorized.
min.insync.replicas=2 sensitive=false
unclean.leader.election.enable=false sensitive=false
```

## Actual

```text
Completed updating config for topic payments.authorized.
Dynamic configs for topic payments.authorized are:
  min.insync.replicas=2 sensitive=false synonyms={DYNAMIC_TOPIC_CONFIG:min.insync.replicas=2, DYNAMIC_DEFAULT_BROKER_CONFIG:min.insync.replicas=1, DEFAULT_CONFIG:min.insync.replicas=1}
  unclean.leader.election.enable=false sensitive=false synonyms={DYNAMIC_TOPIC_CONFIG:unclean.leader.election.enable=false, DEFAULT_CONFIG:unclean.leader.election.enable=false}
```

Two differences:

1. A `Dynamic configs for topic payments.authorized are:` header line appears between the alter confirmation and the config lines.
2. Each config line carries a trailing `synonyms={…}` clause listing every config source that resolves the key. For `min.insync.replicas` there are three: the dynamic topic config, the dynamic broker default, and the static default.

## Evidence

- Kafka 4.3.2 `ConfigCommand.scala` prints the `Dynamic configs for … are:` header before the entries, and `describeDynamicConfig` appends the `synonyms` map to each entry.
- The `synonyms` clause is only present when the key resolves from more than one source. A key set at only one level would print without it.

## Impact

Low. The expected strings are `contains` checks and both `min.insync.replicas=2 sensitive=false` and `unclean.leader.election.enable=false sensitive=false` still appear as substrings of the real lines, so the check passes. The only consequence is that a learner comparing the terminal to the doc sees extra text and cannot tell whether it signals a problem.

## Suggested fix

Update the 5.3 expected block to the real output, or trim it to the part that matters. If the full output is pasted, the block becomes:

```text
Completed updating config for topic payments.authorized.
Dynamic configs for topic payments.authorized are:
  min.insync.replicas=2 sensitive=false
  unclean.leader.election.enable=false sensitive=false
```

Note that the second and third lines are prefixes of the real lines, not the whole lines, so they remain valid `contains` matches against the real output.

## Suggested retest step

After the fix, rerun Chapter 5.3's `kafka-configs --describe` and confirm the expected block matches the printed output verbatim.

# [s2-ep04-lab-02] P-01: Chapter 1.3 expects a `Configs:` value that `kafka-topics --describe` never prints

> **WITHDRAWN 2026-11-10 — not reproduced on the VM.** A clean run of 1.3 printed `Configs: min.insync.replicas=1` exactly as the doc promises (Kafka 4.3.2, `apache/kafka:4.3.2`). The source-level reasoning below was wrong for this tool version. Do not file this issue.
>
> Static desk review. Not yet confirmed on a Poridhi VM; confirm before closing.

| Field | Value |
|---|---|
| **Lab ID** | `s2-ep04-lab-02` |
| **Section** | 1.3 Implementation: The Replicated Topic |
| **Kind** | Content |
| **Severity** | **1 Blocker** (a check can never pass) |
| **Commit tested** | N/A — draft |

## Steps to reproduce

1. Environment Setup → Chapter 1.
2. Run the 1.3 block as written:

```bash
kafka kafka-topics $B --create --topic payments.authorized --replica-assignment 1:2:3,2:3:1,3:1:2
kafka kafka-topics $B --describe --topic payments.authorized
```

## Expected

The README's `<!-- expect: contains -->` block:

```text
Created topic payments.authorized.
PartitionCount: 3 ReplicationFactor: 3 Configs: min.insync.replicas=1
Partition: 0 Leader: 1 Replicas: 1,2,3 Isr: 1,2,3
...
```

## Actual

The summary line prints `Configs:` with nothing after it:

```text
Topic: payments.authorized  TopicId: ...  PartitionCount: 3  ReplicationFactor: 3  Configs:
```

`kafka-topics.sh --describe` prints only configs where `!config.isDefault()` (`TopicCommand.java`, 4.3.2, `TopicDescription.printDescription()`). `min.insync.replicas=1` is inherited, not a topic-level override, so it is filtered out. The old `segment.bytes` artifact was removed in KAFKA-13718 (Kafka 3.3.0).

## Evidence

- Kafka 4.3.2 source: `tools/src/main/java/org/apache/kafka/tools/TopicCommand.java`, line ~285: `.filter(config -> !config.isDefault())`.
- KAFKA-13718, fixed in 3.3.0 (default `segment.bytes` no longer shown).

## Impact

The 1.3 expected-output check fails on every run, so the lab's first verification can never pass.

## Suggested fix

Remove the summary line from the expected block (keep the three `Partition:` lines), and reword the bullet:

> `min.insync.replicas` defaults to `1`; it is not shown here because it is not a topic-level override.

The `Elr`/`LastKnownElr` fields appended to the partition lines do not break the other `contains` checks, because those expected strings stop at `Isr:`.

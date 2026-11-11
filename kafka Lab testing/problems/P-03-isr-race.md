# [s2-ep04-lab-02] P-03: Chapter 5.7 durable retry races the ISR recovery

> **REFUTED on the VM, 2026-11-10.** The race did not occur: the durable retry after the failover returned `acked 200, failed 0`, exactly as the doc expects. This was a pre-run theoretical concern about a fixed `sleep 12`; it does not reproduce.

| Field | Value |
|---|---|
| **Lab ID** | `s2-ep04-lab-02` |
| **Section** | 5.7 Experiment: The Same Failure, Durable (run block 2 of 3) |
| **Kind** | Bug (potential, timing) |
| **Severity** | ~~**2 Major**~~ — **not reproduced** |
| **Commit tested** | doc as published 2026-11-10 (doc commit not recorded) |

## Steps to reproduce

1. Create `lab02.incident-durable` with `min.insync.replicas=2`.
2. Pause brokers 2 and 3, wait 15 s (ISR = 1).
3. Run `python run_writer.py --topic lab02.incident-durable --durable -n 200 --out acked-durable-down.txt` (expect 0 acked).
4. Kill broker 1, then `docker unpause` brokers 2 and 3, then `sleep 12`.
5. Immediately run `python run_writer.py --topic lab02.incident-durable --durable -n 200 --out acked-durable.txt`.

## Expected

```text
lab02.incident-durable: acked 200, failed 0
```

## Actual — on the VM, the expected output

```text
lab02.incident-durable: acked 0, failed 200
  failed 200: _MSG_TIMED_OUT
acknowledged IDs saved to acked-durable-down.txt
kafka
kafka
kafka
Topic: lab02.incident-durable   TopicId: IEkpzMeCQMyglpWaWEuNLQ PartitionCount: 1       ReplicationFactor: 3    Configs: min.insync.replicas=2
        Topic: lab02.incident-durable   Partition: 0    Leader: 3       Replicas: 1,2,3 Isr: 2,3        Elr:    LastKnownElr:
lab02.incident-durable: acked 200, failed 0
acknowledged IDs saved to acked-durable.txt
```

The retry returned `acked 200, failed 0`. No `NOT_ENOUGH_REPLICAS` storm and no second `_MSG_TIMED_OUT` batch.

## Why it did not race

The `describe` between the two writers shows `Isr: 2,3` — broker 2 had already rejoined the ISR and broker 3 (the new leader) was leading. The fixed `sleep 12` was enough on this VM: broker 2 was unpaused *before* broker 3, so it had the full 12 seconds to catch up (`replica.lag.time.max.ms` is 10 s on this cluster).

## Residual risk

The finding is refuted, not disproven. The step still relies on a fixed `sleep 12` rather than observing the ISR, so on a slower VM, or with the unpause order reversed (broker 3 first), the retry could still start with an ISR of one and time out. The lab's own text acknowledges the leader can vary, which implies the unpause order is not fixed in the learner's mind.

Two benign log lines appeared and are **not** defects — they are the expected librdkafka behaviour:

```text
%4|...|GETPID|rdkafka#producer-1| [thrd:main]: Failed to acquire idempotence PID from broker 13.212.218.76:9094/1: Broker: Coordinator load in progress: retrying
%3|...|FAIL|rdkafka#producer-1| [thrd:13.212.218.76:9094/bootstrap]: Connect to ipv4#13.212.218.76:9094 failed: Connection refused (after 1ms in state CONNECT)
```

The first is the idempotence producer-ID handshake retrying against the broker that was just killed; the second is a connection refused to the killed broker 1. The doc's Troubleshooting section already covers broker connection noise for 3.7.

## Impact

None observed. The chapter's "0 lost" proof landed as written.

## Suggested fix (optional hardening, not required)

If the maintainers want to remove the timing dependency:

```bash
until kafka kafka-topics $B --describe --topic lab02.incident-durable \
    | grep -q 'Isr: [0-9],[0-9]'; do sleep 3; done
```

## Suggested retest step

Not required — the finding is closed as *not reproduced*. If a learner ever reports the retry timing out, run this step again and check whether the `describe` before the retry showed `Isr: 2,3`.

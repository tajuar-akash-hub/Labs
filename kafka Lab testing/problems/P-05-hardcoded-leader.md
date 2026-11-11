# [s2-ep04-lab-02] P-05: Chapter 4.7 hard-codes the post-failover leader

> **CONFIRMED on the VM, 2026-11-10.** The same failure mode produced two different leaders in one session: broker 2 in Chapter 4.7 and broker 3 in Chapter 5.7, while the doc's 4.7 expected block pins `Leader: 2`.

| Field | Value |
|---|---|
| **Lab ID** | `s2-ep04-lab-02` |
| **Section** | 4.7 Experiment: Reproduce the Incident (expected-output block) |
| **Kind** | Content |
| **Severity** | **3 Minor** |
| **Commit tested** | doc as published 2026-11-10 (doc commit not recorded) |

## Steps to reproduce

1. Create `lab02.incident` with `--replica-assignment 1:2:3 --config unclean.leader.election.enable=true`.
2. Pause brokers 2 and 3, wait 15 s.
3. `python run_writer.py --topic lab02.incident --acks 1 -n 200 --out acked-incident.txt`.
4. `ssh broker-1 docker kill kafka`, unpause 2 and 3, `sleep 12`.
5. `kafka kafka-topics $B --describe --topic lab02.incident`.

## Expected (doc 4.7)

```text
Partition: 0 Leader: 2 Replicas: 1,2,3 Isr: 2,3
```

## Actual — two leaders observed in one session

**Chapter 4.7** (broker 2 unpaused first):

```text
Partition: 0 Leader: 2 Replicas: 1,2,3 Isr: 2,3
```

**Chapter 5.7** (same setup, brokers paused and unpaused the same way):

```text
Partition: 0    Leader: 3       Replicas: 1,2,3 Isr: 2,3        Elr:    LastKnownElr:
```

The 5.7 topic used `min.insync.replicas=2` and clean election rather than unclean, so it is not the identical scenario — but it is the same *shape* (kill broker 1, unpause both followers, sleep 12, describe), and it produced broker 3 as leader.

The 4.7 case is the one that matters: it is the doc's own example, and the leader it elected depends on which follower the controller contacted first after `unpause`. Nothing in the step pins that order.

## Evidence

- The doc's 5.7 section already acknowledges the variance: *"Which follower becomes leader can vary"* — and its expected block correctly asserts only `Replicas: 1,2,3 Isr: 2,3`.
- The doc's 4.7 section does not. Its expected block pins `Leader: 2` with no variance note.
- Chapter 5.7's own output on this run shows the same step shape producing `Leader: 3`.

## Impact

The 4.7 expected-output check can fail on a valid run. A learner whose controller elects broker 3 sees a mismatch in the lab's most important step — the one that reproduces the incident — and has no way to tell whether their run was wrong or the doc was.

## Suggested fix

Assert only `Replicas: 1,2,3 Isr: 2,3`, as Chapter 5.7 already does, and add the same variance note to 4.7. Alternatively state "Leader is 2 or 3".

## Suggested retest step

After the fix, re-run 4.7 and confirm the expected block no longer names a specific leader.

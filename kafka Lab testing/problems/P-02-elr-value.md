# [s2-ep04-lab-02] P-02: Chapter 5.1 promises an `Elr` value that the output it points at cannot contain

> **Partially refuted on the VM, 2026-11-10.** The *value* claim (`Elr: 3` is wrong, should be `2,3`) is **refuted** — the VM printed `Elr: 3`, matching the doc. The *structural* claim (5.1 points at the wrong output block; 5.7's expected line omits `Elr:`) is **still open and valid**. A third question (is `Elr: 3` stable, or an artifact of unpause order?) is **open pending a follow-up probe**.

| Field | Value |
|---|---|
| **Lab ID** | `s2-ep04-lab-02` |
| **Section** | 5.1 What You Will Build; 5.7 Experiment: The Same Failure, Durable |
| **Kind** | Content |
| **Severity** | **2 Major** (structural part) / value part withdrawn |
| **Commit tested** | doc as published 2026-11-10 (doc commit not recorded) |

## Part A — value claim: REFUTED

The original report claimed the ELR set should read `2,3` (both followers dropped from the ISR) and that the doc's `Elr: 3` was wrong.

**Observed on the VM** — this is the lab's own **5.7 block 1** run verbatim (topic `lab02.incident-durable`, `min.insync.replicas=2`, brokers 2 and 3 both `docker pause`d, 15 s wait, then `kafka-topics --describe`):

```text
Created topic lab02.incident-durable.
Topic: lab02.incident-durable   TopicId: IEkpzMeCQMyglpWaWEuNLQ PartitionCount: 1       ReplicationFactor: 3    Configs: min.insync.replicas=2
        Topic: lab02.incident-durable   Partition: 0    Leader: 1       Replicas: 1,2,3 Isr: 1  Elr: 3  LastKnownElr:
```

`Elr: 3` — exactly the value the doc states in 5.1. The claim "should be `2,3`" is wrong on this run and is **withdrawn**. The doc's stated value is what the lab's own expected step produces.

## Part B — structural claim: STILL OPEN (valid)

This part is unaffected by Part A and remains a genuine content bug.

5.1 says:

> "You will see `Elr: 3` in the output below."

but the block that follows in 5.1/5.3 is the `kafka-configs --alter` / `kafka-configs --describe` output:

```text
Completed updating config for topic payments.authorized.
Dynamic configs for topic payments.authorized are:
  min.insync.replicas=2 sensitive=false ...
  unclean.leader.election.enable=false sensitive=false ...
```

`kafka-configs` **never prints an `Elr` field**. The only command in the whole lab that can show ELR is `kafka-topics --describe`, and the partition line the lab shows in 5.7 omits `Elr:` entirely:

```text
Partition: 0    Leader: 1       Replicas: 1,2,3 Isr: 1
```

So the learner is pointed at a block that cannot contain the promised value, and the ELR safety proof the chapter is built around is never actually displayed in the chapter that is supposed to display it.

## Part C — is `Elr: 3` stable? ANSWERED — and it opens a new problem

Observation that needed explaining: **both** followers were paused, yet ELR listed only broker `3` — not `2,3`.

**Resolved by the 5.7 block 2 describe** (after both followers were unpaused and broker 1 was killed):

```text
Topic: lab02.incident-durable   Partition: 0    Leader: 3       Replicas: 1,2,3 Isr: 2,3        Elr:    LastKnownElr:
```

`Elr:` is now **empty**, and the new leader came from the ISR (`Isr: 2,3`), not from the ELR. So:

1. **ELR is a proper set.** It held broker 3 while frozen and emptied once broker 3 became leader and rejoined the ISR. The single member was a genuine transient state, not a truncation of a two-member set.
2. **The `Elr: 3` in 5.1 is order- and timing-dependent.** It named broker 3 because broker 3 was the one that had been the eligible candidate at that moment. A learner who unpauses in a different order may see `Elr: 2`. The doc must not promise a specific number.

### New finding — the 5.1 ELR explanation is contradicted by the run

5.1 tells the learner:

> "If the leader then dies, the controller can elect from the ELR without losing anything."

The VM shows the opposite sequence. At the moment of the election the partition line read `Isr: 2,3` with **`Elr:` empty** — broker 2 was already back in the ISR before the controller elected a leader, so the election was an ordinary ISR election. The ELR was not what made the failover safe in this run; the fact that **zero records had been acknowledged** (the writer got `acked 0, failed 200`) was.

The safety argument the chapter is built on is therefore correct in substance but wrong in mechanism, and the doc's own 5.7 output makes the contradiction visible to the learner: the block that supposedly proves ELR at work shows an empty ELR.

**This is a separate, larger finding than the original P-02 value claim** and should be filed on its own rather than folded into the withdrawn value claim.

## Impact

- Part A: none — the doc's stated value matched the VM on that run.
- Part B: real. The chapter's ELR proof is promised but never shown; a learner comparing the terminal to the doc sees a missing promised value with no way to know why.
- Part C: resolved. `Elr: 3` was a transient, order-dependent value. The doc should not promise a specific number.
- New finding: the 5.1 ELR mechanism is contradicted by 5.7's own output.

## Suggested fix (for Part B)

- 5.1: change "You will see `Elr: 3` in the output below" to point at the `kafka-topics --describe` output in 5.7, e.g. "In the `kafka-topics --describe` output in 5.7 you will see the `Elr:` field."
- 5.7: add the `Elr:` field to the expected partition line, e.g. `Isr: 1  Elr: 3` — **once Part C is settled**, since the exact value may be order-dependent.

## Suggested retest step

After the fix, rerun the 5.7 sequence and confirm the `kafka-topics --describe` partition line printed by the VM contains the `Elr:` value the doc points at, and that the doc points at that block rather than the `kafka-configs` one.

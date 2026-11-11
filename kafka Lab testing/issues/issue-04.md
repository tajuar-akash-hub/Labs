# Issue 4 of 7

**Filed:** [#93](https://github.com/poridhiEng/poridhi-labs/issues/93)

Form: https://github.com/poridhiEng/poridhi-labs/issues/new?template=s2-lab-problem.yml

---

## Title

```
[s2-ep04-lab-02] 5.1: "You will see Elr: 3 in the output below" points at a kafka-configs block that cannot print an Elr field
```

## Body

```
**Lab ID:** s2-ep04-lab-02

**Section:** 5.1 What You Will Build (ELR paragraph); 5.7 Experiment: The Same Failure, Durable (expected-output block)

**Kind:** Content

**Severity:** 2 Major

**Commit tested:** d7aa49e

**Steps to reproduce:**

1. Read 5.1's ELR paragraph, which ends:

   > "You will see `Elr: 3` in the output below."

2. Read the output block immediately below it in 5.3:

```bash
kafka kafka-configs $B --alter --entity-type topics --entity-name payments.authorized \
  --add-config min.insync.replicas=2,unclean.leader.election.enable=false
kafka kafka-configs $B --describe --entity-type topics --entity-name payments.authorized
```

3. Run it. The output is:

```text
Completed updating config for topic payments.authorized.
Dynamic configs for topic payments.authorized are:
  min.insync.replicas=2 sensitive=false synonyms={...}
  unclean.leader.election.enable=false sensitive=false synonyms={...}
```

**Expected:**

The output below shows `Elr: 3`.

**Actual:**

`kafka-configs --describe` never prints an `Elr` field. It prints dynamic topic config entries only. A learner following the instruction literally cannot find the promised value anywhere in that block.

The only command in the lab that can show `Elr` is `kafka-topics --describe`, and the partition line in 5.7's expected block omits the field entirely:

```text
Partition: 0 Leader: 1 Replicas: 1,2,3 Isr: 1
```

**Evidence:**

- Kafka 4.3.2 `kafka-topics --describe` prints `Elr:` and `LastKnownElr:` on each partition line.
- Kafka 4.3.2 `kafka-configs --describe` prints only `min.insync.replicas=... sensitive=...` style entries.
- 5.1's ELR paragraph is the only place in the doc that introduces `Elr`, and it points the reader at the wrong output.

**Impact:**

The chapter's ELR proof is promised but never shown. A learner comparing the terminal to the doc sees a missing promised value with no way to know whether their run is wrong.

A second, smaller point: the promised value `Elr: 3` is not stable. On this run the ELR held broker 3, but the ELR member depends on which follower was the eligible candidate at that moment, so a learner who unpauses the brokers in a different order may see `Elr: 2`. The doc should not promise a specific number.

**Suggested fix:**

- 5.1: change "You will see `Elr: 3` in the output below" to point at the `kafka-topics --describe` output in 5.7, e.g. "In the `kafka-topics --describe` output in 5.7 you will see the `Elr:` field."
- 5.7: add the `Elr:` field to the expected partition line, e.g. `Isr: 1  Elr: 3`, and do not promise a fixed member.
- Consider adding a `kafka-topics --describe` block right after the ELR paragraph in 5.1, so the field is introduced where it is claimed.

**Suggested retest step:**

After the fix, rerun 5.7 and confirm the `kafka-topics --describe` partition line printed by the VM contains the `Elr:` value the doc points at, and that the doc points at that block rather than the `kafka-configs` one.
```

## Labels

```
course:mlops-s2
kind:lab-problem
```

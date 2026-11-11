# Issue 3 of 7

**Filed:** [#92](https://github.com/poridhiEng/poridhi-labs/issues/92)

Form: https://github.com/poridhiEng/poridhi-labs/issues/new?template=s2-lab-problem.yml

---

## Title

```
[s2-ep04-lab-02] 5.1 and 5.7: the ELR election mechanism is explained incorrectly; 5.7's own output shows an empty Elr at the election
```

## Body

```
**Lab ID:** s2-ep04-lab-02

**Section:** 5.1 What You Will Build (ELR paragraph); 5.7 Experiment: The Same Failure, Durable

**Kind:** Content

**Severity:** 2 Major

**Commit tested:** d7aa49e

**Steps to reproduce:**

1. Run 5.7 block 1: create `lab02.incident-durable` with `--replica-assignment 1:2:3 --config min.insync.replicas=2`, pause brokers 2 and 3, wait 15 s, then describe the topic.

```bash
kafka kafka-topics $B --create --topic lab02.incident-durable --replica-assignment 1:2:3 \
  --config min.insync.replicas=2
ssh broker-2 docker pause kafka
ssh broker-3 docker pause kafka
sleep 15
kafka kafka-topics $B1 --describe --topic lab02.incident-durable
```

2. Run 5.7 block 2: write 200 with the durable producer, kill broker 1, unpause brokers 2 and 3, `sleep 12`, then describe the topic again.

```bash
python run_writer.py --topic lab02.incident-durable --durable -n 200 --out acked-durable-down.txt
ssh broker-1 docker kill kafka
ssh broker-2 docker unpause kafka
ssh broker-3 docker unpause kafka
sleep 12
kafka kafka-topics $B --describe --topic lab02.incident-durable
```

**Expected (5.1):**

> "**Eligible leader replicas (ELR).** Kafka 4.x adds one more safety net. When the ISR shrinks below `min.insync.replicas`, the replicas that were dropped are kept in `Elr`: they are not in sync for new writes, but they hold every record that was ever acknowledged with `acks=all`, because no write was accepted after they left. **If the leader then dies, the controller can elect from the ELR without losing anything.** You will see `Elr: 3` in the output below."

And 5.7's prose for the failover step:

> "**After the crash:** a follower became leader through the ELR, safely, because it holds every acknowledged record (there were none to miss)."

**Actual:**

The describe taken at the moment of the election:

```text
Topic: lab02.incident-durable   TopicId: IEkpzMeCQMyglpWaWEuNLQ PartitionCount: 1       ReplicationFactor: 3    Configs: min.insync.replicas=2
        Topic: lab02.incident-durable   Partition: 0    Leader: 3       Replicas: 1,2,3 Isr: 2,3        Elr:    LastKnownElr:
```

**`Elr:` is empty.** The new leader (broker 3) was elected from the ISR (`Isr: 2,3`), not from the ELR. Broker 2 had already rejoined the ISR before the controller elected anyone.

The writer that ran just before the crash had refused everything:

```text
lab02.incident-durable: acked 0, failed 200
  failed 200: _MSG_TIMED_OUT
```

So the failover was safe for a different reason than the doc gives: **zero records had been acknowledged while the followers were frozen**, because `min.insync.replicas=2` made every write fail. There was nothing for the new leader to miss. The ELR played no part in it.

**Evidence:**

- The partition line at the election shows `Isr: 2,3` with an empty `Elr:` and `LastKnownElr:`.
- The pre-crash writer output shows `acked 0, failed 200` - the topic was empty of acknowledged records.
- The earlier describe (5.7 block 1, followers frozen) showed `Isr: 1  Elr: 3`, so ELR *was* populated while frozen and emptied again by the time of the election. ELR is a set that empties as replicas become eligible again - it is not a standing safety net for the next election.
- KIP-966 defines ELR as replicas dropped from the ISR that are retained as leader-election candidates. The doc's own description ("no write was accepted after they left") is about *why they are safe*, not about *when they are used*.

**Impact:**

The chapter's central claim - "the controller elected through the ELR, safely" - is not what the lab's own output shows. A learner who reads the describe output in 5.7 sees an empty `Elr:` directly under a sentence saying the leader was elected through the ELR.

It also weakens the teaching point. The genuinely valuable lesson of 5.7 is "the cluster refused to promise what it could not keep" - the 200 refusals are the story. The ELR is a side detail that, as written, the output contradicts.

**Suggested fix:**

Either of these resolves it.

**Option A - correct the mechanism.** Reword 5.7's prose to describe what actually happened, and make the ELR a supporting detail rather than the cause:

> "**After the crash:** a follower became leader safely. The ELR had held broker 3 while the followers were frozen, and broker 3 held every acknowledged record - of which there were none, because the cluster had refused all 200 writes. The safety came from the refusal, not from the election."

**Option B - make the ELR visible.** If the ELR election is what the chapter wants to teach, the step must observe it: describe the topic at the moment the leader is dead and the followers are *still* frozen (which shows `Elr: 3`), and elect while the followers are still down, so the controller has to choose from the ELR.

**Suggested retest step:**

After the fix, re-run 5.7 and confirm that either (a) the prose matches the `Elr:` value the describe actually prints, or (b) the step now observes a non-empty `Elr:` at the moment of the election.
```

## Labels

```
course:mlops-s2
kind:lab-problem
```

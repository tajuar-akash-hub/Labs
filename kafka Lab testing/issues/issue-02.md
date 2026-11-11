# Issue 2 of 7

**Filed:** [#91](https://github.com/poridhiEng/poridhi-labs/issues/91)

Form: https://github.com/poridhiEng/poridhi-labs/issues/new?template=s2-lab-problem.yml

---

## Title

```
[s2-ep04-lab-02] Environment Setup: the broker container can abort at first boot (quorum not ready) and never restarts
```

## Body

```
**Lab ID:** s2-ep04-lab-02

**Section:** Environment Setup / "Three brokers" (user-data bootstrap)

**Kind:** Content

**Severity:** 2 Major

**Commit tested:** d7aa49e

**Steps to reproduce:**

1. Run Environment Setup → "Three brokers" as written (unchanged user-data.sh).
2. Run the readiness loop from the next block.

**Expected:**

`brokers answering: 3`: each node runs `controller` and `kafka`.

```text
broker-1: controller kafka
broker-2: controller kafka
broker-3: controller kafka
```

**Actual:**

`brokers answering: 2`. One node's broker had exited at boot and stayed down:

```text
== broker-3 ==
kafka Exited (1) 32 minutes ago
controller Up 33 minutes
```

`docker logs kafka` on that node ended with:

```text
ERROR Exiting Kafka due to fatal exception during startup. (kafka.Kafka$)
java.lang.RuntimeException: Received a fatal error while waiting for the
controller to acknowledge that we are caught up
```

**Evidence:**

- `docker ps -a` -> `kafka Exited (1) 32 minutes ago`, `controller Up 33 minutes` on broker-3.
- The node whose user-data finished first starts its broker while the other two controllers are still booting, so the 3-voter quorum is not formed yet and the broker aborts. Nothing restarts it: `user-data.sh` runs `docker run` without `--restart`, and the lab gives no recovery step.
- `docker start kafka` later brought it up and the count went to 3.
- The doc's readiness loop waits for brokers to answer, but it has no timeout and no diagnosis: it simply prints the smaller number and stops. Nothing tells the learner that a container has exited.

**Impact:**

A learner who hits this waits indefinitely for a readiness loop that cannot succeed, with no indication of why. The doc's Troubleshooting section covers `brokers answering: 0` for instances still installing Docker and for a changed VM public IP, but not for a broker container that has exited.

**Suggested fix:**

- Add a restart policy to the broker container (e.g. `--restart unless-stopped`), or make `user-data.sh` wait for the quorum before starting the broker.
- Extend the Troubleshooting section with the case "a broker container has exited": show `docker ps -a` and the restart command.
- Give the readiness loop a bounded attempt count and point at the troubleshooting entry when it gives up.

**Suggested retest step:**

Re-run the Three brokers setup and confirm all three nodes report `controller kafka`, and that killing a broker container brings it back without manual intervention.
```

## Labels

```
course:mlops-s2
kind:lab-problem
```

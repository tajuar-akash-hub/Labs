# [s2-ep04-lab-02] P-14: the broker container can exit on first boot and never restarts

> **Confirmed on the VM, 2026-11-10** (fresh Poridhi VM, `ap-southeast-1`).

| Field | Value |
|---|---|
| **Lab ID** | `s2-ep04-lab-02` |
| **Section** | Environment Setup / "Three brokers" (user-data bootstrap) |
| **Kind** | Content (race in shipped user-data, no restart policy) |
| **Severity** | **2 Major** (lab blocked on some boots; undocumented manual restart) |
| **Commit tested** | doc as published 2026-11-10 (commit ID not recorded) |

## Steps to reproduce

1. Run Environment Setup → "Three brokers" as written.
2. Wait for the readiness loop.

## Expected

`brokers answering: 3`: each node runs `controller` and `kafka`.

## Actual

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

The node whose user-data finished first starts its broker while the other two controllers are still booting, so the 3-voter quorum is not formed yet and the broker aborts. Nothing restarts it: `user-data.sh` runs `docker run` without `--restart`, and the lab gives no recovery step.

## Evidence

- `docker ps -a` → `kafka Exited (1) 32 minutes ago`, `controller Up 33 minutes` on broker-3.
- `docker start kafka` later brought it up and the count went to 3.

## Impact

On a fresh launch the cluster can come up with 2 of 3 brokers, so every Chapter 1+ check fails until the learner manually finds and restarts the dead container — and the lab never tells them how.

## Suggested fix

- Add `--restart unless-stopped` to both `docker run` calls in `user-data.sh`.
- Or make the broker container wait for the controller quorum before starting.
- Add a health line after the readiness loop that runs `docker ps -a` on each node and says to `docker start kafka` if a broker is exited.

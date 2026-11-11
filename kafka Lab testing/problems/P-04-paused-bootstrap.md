# [s2-ep04-lab-02] P-04: Producer bootstraps to paused brokers during the write steps

> Static desk review. Not yet confirmed on a Poridhi VM; confirm before closing.

| Field | Value |
|---|---|
| **Lab ID** | `s2-ep04-lab-02` |
| **Section** | 3.7 Experiment: Two Brokers Down; 4.7 Experiment: Reproduce the Incident |
| **Kind** | Bug (potential, hang) |
| **Severity** | **3 Minor** |
| **Commit tested** | N/A — draft |

## Steps to reproduce

1. Chapter 3.7: stop brokers 2 and 3, then run `python run_writer.py --topic lab02.acks --acks all -n 50`.
2. Chapter 4.7: `docker pause` brokers 2 and 3, then run `python run_writer.py --topic lab02.incident --acks 1 -n 200`.

## Expected

The writer returns promptly (about 10 s of retries for the `min.insync.replicas=2` case; immediate success for `acks=1`).

## Actual

`run_writer.py` uses `$BOOTSTRAP` (all three brokers). The lab already documents that a paused broker accepts TCP but never answers, and tells the learner to use `$B1` for `kafka-topics`, but the producer path has no equivalent. librdkafka can spend up to `socket.timeout.ms` (~60 s per broker) before it settles on the live broker, so the command can look hung for a minute.

## Evidence

Static: `BOOTSTRAP=$H1:9094,$H2:9094,$H3:9094`; `run_writer.py` reads it. The lab's own troubleshooting section notes the paused-broker hang.

## Impact

Adds an unexplained 60 s pause at the two most important steps; a learner may interrupt and misread the result.

## Suggested fix

Let `run_writer.py` accept `--bootstrap`, or temporarily export `BOOTSTRAP=$H1:9094` for these writes, and add one sentence to each step.

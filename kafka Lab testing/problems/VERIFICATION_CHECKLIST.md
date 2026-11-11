# Lab 02 verification checklist (live run)

Purpose: confirm or refute each reported problem while the lab runs on a fresh VM. Mark each row **Confirmed / Not reproduced / Blocked** and paste the exact output into chat.

| Field | Value |
|---|---|
| Lab ID | `s2-ep04-lab-02` |
| Commit tested | _record from the doc repo / `git rev-parse --short HEAD`_ |
| VM start / end | _record_ |
| Total time | _record_ |

## Per-problem checks

| ID | Step | What to capture | Confirm if | Status |
|---|---|---|---|---|
| P-01 | 1.3 `--describe` | The exact `Topic: payments.authorized ... Configs: ...` summary line | `Configs:` is empty (no `min.insync.replicas=1`) and the 1.3 expected block fails | **Not reproduced** — VM printed `Configs: min.insync.replicas=1` exactly as the doc says |
| P-02 | 5.7 `--describe` (while ISR=1) | The exact `Partition: 0 ... Elr: ...` line | `Elr:` shows `2,3` (not `3`), and 5.1's promised value is missing | **Value claim REFUTED** — the dedicated probe on `lab02.incident-durable` (brokers 2+3 paused, `min.insync.replicas=2`) printed `Isr: 1  Elr: 3  LastKnownElr:` — exactly the doc's `Elr: 3`, not `2,3`. **Structural claim still open**: 5.1 points at the `kafka-configs` block, which can never show `Elr:`. **New open question**: both followers were paused yet ELR listed only `3` — set vs. last-to-drop is unresolved; follow-up probe (unpause broker 2 only, then broker 3) queued in `commands.txt` |
| P-03 | 5.7 second `run_writer --durable` | `Isr:` from the describe before the write + writer result | Writer reports `acked 0, failed 200` / `_MSG_TIMED_OUT` when ISR < 2 | **Not reproduced** — the describe before the retry showed `Isr: 2,3` and the retry returned `acked 200, failed 0`. No ISR race. Refuted |
| P-04 | 3.7 and 4.7 `run_writer` with brokers paused/stopped | Wall-clock duration of each writer | Either writer stalls ~60 s before completing | **Not reproduced (weak)** — the 3.7 and 4.7 writers completed without an obvious stall, but the `time` output was not captured, so this is not a clean refutation. Re-run with `time` |
| P-05 | 4.7 post-failover describe | Actual `Leader:` after unpause | Leader is 3 (not 2) on at least one run | **Confirmed** — 4.7 gave `Leader: 2` (matching the doc), but the same step shape in 5.7 gave `Leader: 3`. Leader identity is order-dependent, and 4.7's expected block pins `Leader: 2` with no variance note (5.7 does have one) |
| P-06 | 2.6 → restart block | Whether `LEADER` is still set when the restart block runs | Restart fails with `broker--100` in a fresh shell | **Not exercised** — 2.6 and its restart block ran in the same shell, so `LEADER` was still set. Re-run the restart block in a fresh terminal |

## Secondary checks (not filed as separate reports yet)

| ID | Step | What to capture | Confirm if | Status |
|---|---|---|---|---|
| P-07 | 2.3 console producer | Whether `acks` is stated; topic offsets after 100 | First 100 records not fully replicated before the crash | **Not checked** — 2.3 produced the expected `lab02.failover:0:100`; the `acks` default was not verified |
| P-08 | Setup firewall block | Exact order of the SG describe output | Order is not 22, 9094, 9092-9093 | **Confirmed** — actual order: 9094, 22, 9092-9093 |
| P-09 | Three brokers launch | `$H1..$H3` values right after the wait | Any host value is empty | **Not reproduced** — H1/H2/H3 + BOOTSTRAP all populated |
| ELR | Ch1/Ch2/Ch3 describes | Whether `Elr:` / `LastKnownElr:` appear on partition lines | Fields present but expected blocks still match | **Observed** — `Elr:` appears on every partition line in 4.3.2 and is **empty** when the ISR is full; it shows `3` on `lab02.acks` once brokers 2/3 are stopped. `LastKnownElr:` is empty in every run so far |
| P-16 | 5.7 post-failover describe | The `Elr:` field at the moment of the election | `Elr:` is non-empty and the election came from it | **Confirmed** — the describe showed `Isr: 2,3` with **`Elr:` empty** and `Leader: 3`. The leader was elected from the ISR, not the ELR. 5.1's "the controller can elect from the ELR without losing anything" and 5.7's "a follower became leader through the ELR" are contradicted by the lab's own output. Filed as P-16 |
| P-11 | Setup `ls` | Exact `ls` output | Interactive `ls` prints `run_audit.py  run_writer.py` on one line vs the two-line expected block | Observed (cosmetic) |
| P-15 | 5.3 `kafka-configs --describe` | The exact output lines | A `Dynamic configs for topic … are:` header and `synonyms={…}` appear | **Confirmed** — filed as [P-15](P-15-configs-synonyms.md) |

## Unexpected failures

Record anything else that differs from the doc (error text, missing line, extra warning, check that does not pass), with the section and the exact output.

| Section | What differed |
|---|---|
| 5.3 | `kafka-configs --describe` prints a `Dynamic configs for topic payments.authorized are:` header and a `synonyms={…}` clause on each config line. The doc's expected block shows neither. Filed as P-15. |


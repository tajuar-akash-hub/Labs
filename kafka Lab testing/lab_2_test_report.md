# [s2-ep04-lab-02] Test report: Build a Durable KRaft Cluster

> **Test type: live run on a Poridhi VM (round 1).** Executed in `ap-southeast-1` on 3 × `t3.small` (Ubuntu 24.04.5, `apache/kafka:4.3.2`, Kafka 4.3.2). Setup required two undocumented recoveries (P-13, P-14) before Chapter 1 could run. Findings below are marked as observed on this run or still desk-review only.

| Field | Value |
|---|---|
| **Lab ID** | `s2-ep04-lab-02` |
| **Test round** | 1 (live run) |
| **Commit tested** | doc as published 2026-11-10 (doc commit not recorded); helper repo `6fad7e0f` |
| **Environment** | Poridhi Cloud VM + AWS `ap-southeast-1`, 3 × `t3.small`, Ubuntu 24.04.5, `apache/kafka:4.3.2` |
| **Tracking issue** | [#32](https://github.com/poridhiEng/poridhi-labs/issues/32) |
| **Target time** | 70 min (AWS: 3 x t3.small) |

---

## Sections that worked exactly as written

> "Worked" = observed on this VM run unless marked otherwise. Chapters 1–5 were executed end-to-end. Only the Epilogue's full-suite check and the teardown remain unrun.

- [x] Before you start (clone, `venv`, `aws configure`, region check)
- [x] The network (VPC, subnet, IGW, route table, SG; IDs recorded for teardown)
- [x] Three brokers (key pair, launch, `user-data.sh` path, `10.0.1.1n` mapping) — needed **P-13/P-14** recovery first
- [x] Shortcuts (`ssh broker-N`, `kafka()`, `$B`, `$B1`, `.bashrc` persistence)
- [x] Chapter 1: 1.1, 1.2, 1.4, 1.5, 1.6, 1.7
- [x] Chapter 1: 1.3 expected output — P-01 **not reproduced** (run printed `Configs: min.insync.replicas=1`)
- [x] Chapter 2: 2.1–2.5, 2.6, 2.7 (2.6 passed, but **P-06** — the `LEADER` variable — was not exercised; same shell throughout)
- [x] Chapter 3: 3.1–3.6, 3.7 (3.7 passed; paused-broker stall **P-04** did not reproduce)
- [x] Chapter 4: 4.1–4.7 — incident reproduced exactly (200 acked / 0 readable / 200 lost; `3 passed`)
- [x] Chapter 5: 5.1–5.6 (5.3 output has extra `synonyms={…}` — see P-15)
- [x] Chapter 5: 5.7 blocks 1–2 (durable incident: `acked 0, failed 200` → `acked 200, failed 0`) — **P-03 refuted**, **P-16** (new), **P-05** (confirmed)
- [x] Chapter 5: 5.7 block 3 (restart broker 1, audit `acked 200, readable 200, lost 0`, ch5 checks `3 passed`)
- [ ] Epilogue / End-to-End Verification (13-test arithmetic: 2+2+3+3+3) — **not yet run**; only the per-chapter checks have been executed
- [ ] Teardown (guarded, idempotent, ends with 0-resource counts) — **not yet run**

**Observed on the VM during this run (exact outputs):**

| Step | Doc expects | VM printed | Verdict |
|---|---|---|---|
| 1.3 `--describe` | `PartitionCount: 3 ReplicationFactor: 3 Configs: min.insync.replicas=1` | identical | match — P-01 withdrawn |
| 1.7 stop broker 3 | `Isr: 1,2` / `2,1` / `1,2`, partition 2 leader → 1 | identical | match |
| 1.7 heal | `3` | `3` | match |
| 2.3 create + write | `lab02.failover:0:100` | `lab02.failover:0:100` | match |
| 2.3 crash leader | `Leader: 2 … Isr: 2,3` | `Leader: 2 … Isr: 2,3` | match |
| 2.3 write after crash | `lab02.failover:0:200` | `lab02.failover:0:200` | match |
| 2.6 kill controller | `new active controller elected`, `lab02.failover:0:300` | identical (`LeaderId 103`; dead voter `LogEndOffset -1`) | match |
| 2.6 heal | `2 passed` | `2 passed` | match |
| 3.5 writer | `acked 100, failed 0` + `2 passed` | identical | match |
| 3.7 two brokers down | `Isr: 1`, `acked 0, failed 50`, `acked 50, failed 0` | identical | match — and ELR printed `Elr: 3` |
| 3.7 heal | `3 passed` | `3 passed` | match |
| 4.5 audit clean topic | `acked 100, readable 100, lost 0` + `2 passed` | identical | match |
| 4.7 incident | `acked 200, failed 0`; `Leader: 2 … Isr: 2,3`; `readable 0, lost 200` | identical | match |
| 4.7 restart broker 1 | still `readable 0, lost 200` + `3 passed` | identical | match — truncation proven |
| 5.3 configs alter | `Completed updating config…` | identical | match (extra `synonyms={…}` — P-15) |
| 5.5 ch5 checks | `2 passed` | `2 passed, 1 deselected in 0.11s` | match |
| P-02 ELR probe | `Elr: 3` | `Partition: 0  Leader: 1  Replicas: 1,2,3 Isr: 1  Elr: 3  LastKnownElr:` | match — P-02 value claim refuted; ELR-set semantics still open |
| 5.7 writer (frozen) | `acked 0, failed 200` / `_MSG_TIMED_OUT` | identical | match — P-03 refuted (no ISR race) |
| 5.7 post-failover describe | `Replicas: 1,2,3 Isr: 2,3` | `Leader: 3  Replicas: 1,2,3 Isr: 2,3  Elr:  LastKnownElr:` | match on ISR — but `Elr:` is **empty** and the leader was **3**, not 2 → **P-16** (new), **P-05** (confirmed) |
| 5.7 retry writer | `acked 200, failed 0` | identical | match — P-03 refuted |
| 5.7 restart + audit | `acked 200, readable 200, lost 0` | identical | match |
| 5.7 ch5 checks | `3 passed` | `3 passed in 0.22s` | match |

**Statically verified as correct:** replica assignment `1:2:3,2:3:1,3:1:2` and the resulting leaders; ISR-list order after broker 3 stops; 9 s `broker.session.timeout.ms`; `LeaderId` parsing (`MetadataQuorumCommand` prints no leading space in 4.3.2); the 7-column `describe --replication` table; `NOT_ENOUGH_REPLICAS` / `_MSG_TIMED_OUT` semantics; `audit.py`; teardown order.

**Corrected by the VM run:** the desk review assumed ELR was "populated with `2`" for the Chapter 5 safe election. The VM showed the opposite at the moment of the election — `Elr:` was **empty** and the leader came from the ISR. See **P-16**.

---

## Time taken (minutes)

**In progress.** Guide target is 70 min (75 max). Recorded so far: brokers booted at 09:23 UTC; ~35 min were lost to P-13/P-14 recovery; Chapter 1.7 was executed around 10:12 UTC and 4.7 around 10:20 UTC. Final time to be filled when the run ends.

## Clarity (did you understand every concept without outside help?)

**Chapters 1–5 executed in full.** The "What you will build → Think first → Implement → Verify → Experiment" rhythm held up in practice: every chapter's expected output matched the VM on the first run except for the recorded discrepancies (P-15 in 5.3, the `Elr` field issues in 5.1/5.7).

The concept gap is real and it is the ELR. Three separate problems, all in the same three paragraphs:

- **P-02** — 5.1 promises `Elr` in "the output below", but that block is the 5.3 `kafka-configs` output, which never prints an `Elr` field. A learner following the instruction literally cannot find the promised value.
- **P-16** — 5.1 explains the mechanism as "the controller can elect from the ELR without losing anything", and 5.7 repeats it ("a follower became leader through the ELR"). The lab's own output shows `Elr:` **empty** at the moment of the election, with the leader coming from the ISR. This is the one that matters: it is not a missing field, it is a mechanism the output contradicts. The actual reason the failover was safe is the one the chapter also states but does not connect — the cluster had refused all 200 writes, so there was nothing for a new leader to miss.
- **P-05** — the expected `Leader: 2` is not guaranteed; the same step shape produced broker 3 in 5.7.

A learner who reads only the ELR paragraph of 5.1 and then looks at 5.7's output learns the opposite of what the lab intends: that a durable failover is protected by ELR, when the evidence in front of them shows the protection came from refusing to write.

## Engagement (did the lab make you want to keep going?)

**Chapters 1–5 executed in full.** The incident-first framing and the "acknowledged but lost" audit are the strongest hooks — the 4.7 reproduction landed exactly as written (200 acknowledged, 0 readable, 200 lost), and the truncation proof after restarting broker 1 is the kind of payoff that keeps a learner moving. The gap is the opposite of the doc's intent: the fragile parts of the run were the *setup* (P-13/P-14), not the teaching content.

---

## Problems filed

| ID | Issue | Severity | Section | Kind | Summary |
|---|---|---|---|---|---|
| [P-01](problems/P-01-configs-line.md) | — | ~~1 Blocker~~ **not reproduced** | 1.3 | — | VM run printed `Configs: min.insync.replicas=1`; withdraw this finding |
| [P-02](problems/P-02-elr-value.md) | [#93](https://github.com/poridhiEng/poridhi-labs/issues/93) | **2 Major** | 5.1, 5.7 | Content | **Value claim refuted.** The VM printed `Elr: 3` (5.7 block 1), matching the doc exactly — not `2,3`. **Structural claim still open**: 5.1 promises `Elr` in "the output below" but that block is `kafka-configs`, which can never show an `Elr` field, and 5.7's expected partition line omits `Elr:` |
| [P-03](problems/P-03-isr-race.md) | — | ~~2 Major~~ **not reproduced** | 5.7 | Bug (potential) | Durable retry racing ISR recovery — **refuted on the VM**: the retry returned `acked 200, failed 0`, and the describe before it already showed `Isr: 2,3` |
| [P-16](problems/P-16-elr-mechanism.md) | [#92](https://github.com/poridhiEng/poridhi-labs/issues/92) | **2 Major** | 5.1, 5.7 | Content | **NEW — confirmed.** 5.1 says the controller "can elect from the ELR without losing anything" and 5.7 says "a follower became leader through the ELR". The 5.7 describe shows `Isr: 2,3` with **`Elr:` empty** — the leader came from the ISR. The failover was safe because the cluster had *refused* all 200 writes (`acked 0, failed 200`), not because of ELR |
| [P-04](problems/P-04-paused-bootstrap.md) | — | **3 Minor** | 3.7, 4.7 | Bug (potential) | `run_writer.py` bootstraps to paused brokers; possible ~60 s stall — **not reproduced** on this run: the 3.7 and 4.7 writers completed without a stall. The `time` prefix was applied to the 4.7 writer but the timing line was not captured, so this is *not yet* a clean refutation |
| [P-05](problems/P-05-hardcoded-leader.md) | [#94](https://github.com/poridhiEng/poridhi-labs/issues/94) | **3 Minor** | 4.7 | Content | Expected `Leader: 2` is coupled to unpause order — **confirmed**: 4.7 gave `Leader: 2`, but the same failure shape in 5.7 gave `Leader: 3`. The doc's 5.7 acknowledges the variance; 4.7's expected block pins `Leader: 2` with no note |
| [P-06](problems/P-06-leader-var.md) | — | **3 Minor** | 2.6 | Content | `LEADER` is used in a later block but never persisted — **not exercised**: 2.6 and its restart block ran in the same shell, where `LEADER` was still set |
| ~~P-12~~ | — | withdrawn | 1.5 | — | Lab's `~/venv` has pytest + `ledgerline` + `confluent_kafka`; failure was a different hand-made venv, not a lab defect |
| [P-13](problems/P-13-cloudinit-503.md) | [#90](https://github.com/poridhiEng/poridhi-labs/issues/90) | **2 Major** | Setup / Three brokers | Content | user-data installs Docker once with no retry; a mirror `503` left 2 of 3 nodes without Docker and the readiness loop just reported `0` |
| [P-14](problems/P-14-broker-exits-at-boot.md) | [#91](https://github.com/poridhiEng/poridhi-labs/issues/91) | **2 Major** | Setup / Three brokers | Content | broker container can abort at first boot (quorum not ready) and never restarts; one node stayed down 32 min |
| [P-15](problems/P-15-configs-synonyms.md) | [#96](https://github.com/poridhiEng/poridhi-labs/issues/96) | **4 Polish** | 5.3 | Content | `kafka-configs --describe` prints a `Dynamic configs for topic … are:` header and `synonyms={…}` on each line; the doc's expected block omits both |
| [P-08](problems/P-08-sg-port-order.md) | [#95](https://github.com/poridhiEng/poridhi-labs/issues/95) | **3 Minor** | Setup / The network | Content | The security-group `IpPermissions` order is not guaranteed by the AWS API; the expected block pins the order 22, 9094, 9092-9093 |

Seven issues filed on 2026-11-10 at [New issue → MLOps S2 — Lab problem](https://github.com/poridhiEng/poridhi-labs/issues/new/choose), labels `course:mlops-s2` + `kind:lab-problem`:

```
#90
#91
#92
#93
#94
#95
#96
```

P-01, P-03 and P-12 are withdrawn (not reproduced). P-13, P-14, P-15, P-16, P-05 and P-08 were confirmed during the 2026-11-10 VM run; P-02's value claim is refuted and its structural claim remains confirmed. P-04 and P-06 are the only pre-run reports still without a clean confirmation or refutation on the VM.

**Not filed separately (lower signal, confirm on the run):**

- **P-07 (4 Polish, 2.3)** — first 100 records rely on the console producer default `acks=all`; say it explicitly with `--producer-property acks=all`. **Not yet checked** — 2.3 ran and produced the expected offsets.
- **P-09 (4 Polish, Three brokers)** — public IP is read immediately after `wait instance-running` with no retry. **Not reproduced** — H1/H2/H3 and BOOTSTRAP were all populated.
- **P-10 (4 Polish, whole lab)** — house style: top-level H1, `cat > file <<'EOF'` file creation, `## Teardown`/`## Next Steps` instead of the Poridhi `## Conclusion` shape.

**Filed separately:** P-08 (SG port order) was confirmed on the VM and filed as [#95](https://github.com/poridhiEng/poridhi-labs/issues/95), so it is no longer in this list.

---

## Notes

- **Mapping:** Chapter N = Task N; "Incident" = Experiment 4.7; "Prove completion" = Epilogue `pytest -q ~/ledgerline/checks/ep04/lab-02` → the lab claims `13 passed`. **The full-suite 13-test run has not been executed yet**; only the per-chapter files have been run.
- **Not a blind run:** I read the whole document, including the hidden solutions and expected outputs, before reviewing. Any prediction behaviour is therefore not independent.
- **Not executed:** the helper repo `tahhnik/ledgerline` (branch `ep04-lab02-v1`), `run_writer.py`, `run_audit.py`, `user-data.sh` (`replica.lag.time.max.ms=10s`, container names, listeners), and the five check scripts were not inspected. In particular, verify whether `test_ch1_cluster.py` re-asserts `min.insync.replicas=1` after 5.3 changes it to `2`, and whether the full-suite run is order-independent.
- **What I liked:** the Ledgerline incident thread and "audit the promise, not the configuration". The 4.7 chapter is the strongest single chapter: every expected output matched, and the truncation proof after restarting broker 1 landed as written. The 5.7 pairing of "the cluster refused 200 writes" with "0 lost" is the right lesson — but the ELR explanation attached to it is the part that does not survive contact with the output (**P-16**).
- **What confused me:** 5.1 promises `Elr` in "the output below", but the next output is `kafka-configs`, which cannot show it (**P-02**, structural part still open).
- **What I would cut or shorten:** nothing major. P-02's structural claim and P-16 need fixing before publishing; P-03 is refuted and P-01 withdrawn; the rest are polish.
- **Suggested retest steps:** after a fix, rerun Chapter 1.3's `--describe` and compare; rerun Chapter 4.7 and 5.7 and confirm `Elr`/ISR timing on the VM.
- **Next steps for this run:** (1) run the full 13-test suite to confirm the lab's headline claim and settle whether `test_ch1_cluster.py` is order-independent against 5.3's `min.insync.replicas=2`; (2) run the teardown block and record the zero-resource counts; (3) record the total elapsed time and the doc commit ID.

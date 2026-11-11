# Test report — Lab 02: Build a Durable KRaft Cluster (round 1)

**Filed:** [#97](https://github.com/poridhiEng/poridhi-labs/issues/97)

Form: https://github.com/poridhiEng/poridhi-labs/issues/new?template=s2-test-report.yml

---

## Title

```
[S2 test] s2-ep04-lab-02 · round 1 · Akash
```

## Lab ID

```
s2-ep04-lab-02
```

## Test round

```
1
```

## Commit tested

```
d7aa49e
```

The lab was read from the `feat/v5-poridhi-format` branch of `mlops-with-cloud-labs` on 2026-11-10; the helper repo `tahhnik/ledgerline` (branch `ep04-lab02-v1`) was at `6fad7e0f`.

## Environment

**Dropdown — pick one:**

- [ ] Poridhi Cloud VM (clean)
- [x] **Poridhi Cloud VM (reused)**  ← *select this*
- [ ] Other (describe in notes)

Details: Poridhi Cloud VM + AWS `ap-southeast-1`, 3 × `t3.small`, Ubuntu 24.04.5, `apache/kafka:4.3.2` (Kafka 4.3.2).

## Sections that worked exactly as written

**Checkboxes — tick these:**

- [x] Before you start (restore, smoke test)
- [ ] Concept primer and matching exercise
- [x] Task 1
- [x] Task 2
- [x] Task 3
- [x] Task 4
- [x] Task 5
- [ ] Task 6 (if present)
- [x] Incident
- [ ] Prove completion (`scripts/verify.sh` passed) — `<<FILL: run pytest -q ~/ledgerline/checks/ep04/lab-02, expect 13 passed>>`
- [ ] Teardown — `<<FILL: run the teardown block, expect all four resource counts at 0>>`

Two chapters matched with a caveat worth noting: 1.3 printed `Configs: min.insync.replicas=1` exactly as documented (an earlier report of a mismatch did not reproduce, and is withdrawn), and 5.3 printed two extra lines the expected block does not contain.

## Time taken (minutes)

```
<<FILL: total minutes>>
```

Guide target is 70 minutes (75 max). Brokers booted at 09:23 UTC. About 35 minutes were lost to the two setup failures described below (the Docker install and the broker container that aborts at first boot), which is why the raw run time exceeds the target.

## Clarity (did you understand every concept without outside help?)

**Dropdown — pick one:**

- [ ] 5 Always
- [ ] 4 Mostly
- [x] **3 Sometimes**  ← *select this*
- [ ] 2 Rarely
- [ ] 1 Not at all

Rationale (for the Notes field): the only concept gap was **ELR (Eligible Leader Replicas)**, and it sits in three paragraphs of 5.1 and 5.7:

- 5.1 says "You will see `Elr: 3` in the output below", but the block below it is the 5.3 `kafka-configs` output, which never prints an `Elr` field at all. A learner following the instruction literally cannot find the promised value.
- 5.1 explains the mechanism as "the controller can elect from the ELR without losing anything", and 5.7 repeats it as "a follower became leader through the ELR". The lab's own output shows `Elr:` **empty** at the moment of the election, with the leader coming from the ISR. The failover was safe because the cluster had *refused* all 200 writes, so there was nothing for a new leader to miss — not because of ELR.
- The expected `Leader: 2` in 4.7 is not guaranteed. 4.7 elected broker 2 on this run, but the same step shape in 5.7 elected broker 3.

A learner who reads only the ELR paragraph of 5.1 and then looks at 5.7's output learns the opposite of what the lab intends: that a durable failover is protected by ELR, when the evidence in front of them shows the protection came from refusing to write.

Every other concept landed as intended. The "What you will build → Think first → Implement → Verify → Experiment" rhythm held up in practice: every predict table had a defensible answer, and the answers were checkable afterwards.

## Engagement (did the lab make you want to keep going?)

**Dropdown — pick one:**

- [ ] 5 Hooked
- [x] **4 Interested**  ← *select this*
- [ ] 3 Neutral
- [ ] 2 Dragging
- [ ] 1 Bored

Rationale (for the Notes field): **the incident-first framing is the strongest thing in the lab.** The 4.7 reproduction landed exactly as written — 200 acknowledged, 0 readable, 200 lost — and the truncation proof after restarting broker 1 (still 0 readable, still 200 lost) is exactly the kind of payoff that keeps a learner moving. The audit framing, "audit the promise, not the configuration", is a genuinely good idea and it works.

The gap is the opposite of the doc's intent: **the fragile part of the run was the setup, not the teaching content.** Two undocumented failures in Environment Setup cost about 35 minutes before Chapter 1 could start, and neither had a recovery path in the doc. A learner who hits them will conclude the lab is broken rather than that they are learning something hard. The 5.7 pairing of "the cluster refused 200 payments" with "0 lost" is the right lesson and lands well — the ELR explanation attached to it is the part that does not survive contact with the output.

## Problems filed

```
#90
#91
#92
#93
#94
#95
#96
```

| Issue | Severity | Section | Summary |
|---|---|---|---|
| [#90](https://github.com/poridhiEng/poridhi-labs/issues/90) | 2 Major | Setup / Three brokers | `user-data.sh` installs Docker once with no retry. A mirror `503` left 2 of 3 nodes with no Docker, and the readiness loop only reported `brokers answering: 0` |
| [#91](https://github.com/poridhiEng/poridhi-labs/issues/91) | 2 Major | Setup / Three brokers | The broker container can abort at first boot (quorum not ready) and never restarts. One node stayed down for 32 minutes |
| [#92](https://github.com/poridhiEng/poridhi-labs/issues/92) | 2 Major | 5.1, 5.7 | The ELR mechanism is explained incorrectly: 5.1 says the controller elects from the ELR, but 5.7's own output shows `Elr:` empty at the election and the leader coming from the ISR |
| [#93](https://github.com/poridhiEng/poridhi-labs/issues/93) | 2 Major | 5.1, 5.7 | 5.1 promises `Elr` in "the output below", but that block is `kafka-configs`, which cannot print an `Elr` field; 5.7's expected partition line omits `Elr:` |
| [#94](https://github.com/poridhiEng/poridhi-labs/issues/94) | 3 Minor | 4.7 | The expected output pins `Leader: 2`, but the leader depends on unpause order. This run elected broker 2 in 4.7 and broker 3 in 5.7. 5.7 notes the variance; 4.7 does not |
| [#95](https://github.com/poridhiEng/poridhi-labs/issues/95) | 3 Minor | Setup / The network | The security-group describe output is not sorted, so the port order in the expected block (22, 9094, 9092-9093) is not guaranteed. This run printed 9094, 22, 9092-9093 |
| [#96](https://github.com/poridhiEng/poridhi-labs/issues/96) | 4 Polish | 5.3 | `kafka-configs --describe` prints a `Dynamic configs for topic ... are:` header and a `synonyms={...}` clause on each line; the expected block omits both |

All seven are filed as *MLOps S2 — Lab problem* issues with labels `course:mlops-s2` and `kind:lab-problem`.

## Notes

**What I liked:** the Ledgerline incident thread and "audit the promise, not the configuration". The 4.7 chapter is the strongest single chapter: every expected output matched, and the truncation proof landed as written.

**What confused me:** 5.1 promises `Elr` in "the output below", but the next output is `kafka-configs`, which cannot show it.

**What I would cut or shorten:** nothing major. The ELR paragraph in 5.1 and the failover bullet in 5.7 need rewriting before publishing; the rest are polish.

**Suggested retest steps:** after a fix, rerun Chapter 1.3's `--describe` and compare; rerun Chapter 4.7 and 5.7 and confirm the `Elr` field and the post-failover leader.

**Not a blind run:** I read the whole document, including the hidden solutions and expected outputs, before reviewing, so my prediction behaviour is not independent.

**Not inspected:** the helper repo `tahhnik/ledgerline` (branch `ep04-lab02-v1`), `run_writer.py`, `run_audit.py`, `user-data.sh`, and the five check scripts were not read. One open question for the maintainers: does `test_ch1_cluster.py` re-assert `min.insync.replicas=1` after 5.3 changes that topic to `2`? If it does, the chapter-1 check passes on its own but fails in the full-suite run, because the suites are not order-independent. `<<FILL: the full-suite run answers this - record the result here>>`

Two earlier findings were **not reproduced** and are withdrawn: a mismatch in 1.3's `Configs:` line (the VM printed `Configs: min.insync.replicas=1` exactly as documented), and a missing pytest prerequisite (the lab's `~/venv` does provide pytest, `ledgerline` and `confluent_kafka`).

Two further findings remain open and are not filed yet: a possible ~60 s stall when `run_writer.py` bootstraps to paused brokers (the writers completed without an obvious stall, but the timing was not captured), and the use of a `LEADER` variable in 2.6 that is never persisted (it only worked because the steps ran in the same shell).

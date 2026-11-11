# Issues — Lab 02: Build a Durable KRaft Cluster (round 1)

**Lab ID:** `s2-ep04-lab-02`
**Test round:** 1
**Commit tested:** `d7aa49e`
**Repo:** `poridhiEng/poridhi-labs` (private)

> **Resuming this lab?** Read [`../CONVERSATION_HANDOFF.md`](../CONVERSATION_HANDOFF.md) first. It has the full state, the standing rules, the next two commands to run, and what issue #97 still needs.

Every file in this folder is a plain Markdown document holding the exact text that was
posted to GitHub. Nothing here is generated at run time — these are the source of
truth for what was filed.

## Problem issues

| File | Issue | Title | Severity | Section |
|---|---|---|---|---|
| [issue-01.md](issue-01.md) | [#90](https://github.com/poridhiEng/poridhi-labs/issues/90) | `user-data.sh` installs Docker once with no retry | 2 Major | Setup / Three brokers |
| [issue-02.md](issue-02.md) | [#91](https://github.com/poridhiEng/poridhi-labs/issues/91) | Broker container aborts at first boot and never restarts | 2 Major | Setup / Three brokers |
| [issue-03.md](issue-03.md) | [#92](https://github.com/poridhiEng/poridhi-labs/issues/92) | ELR mechanism is explained incorrectly in 5.1 and 5.7 | 2 Major | 5.1, 5.7 |
| [issue-04.md](issue-04.md) | [#93](https://github.com/poridhiEng/poridhi-labs/issues/93) | "You will see `Elr: 3` in the output below" points at a `kafka-configs` block | 2 Major | 5.1, 5.7 |
| [issue-05.md](issue-05.md) | [#94](https://github.com/poridhiEng/poridhi-labs/issues/94) | 4.7 pins `Leader: 2`, but the leader depends on unpause order | 3 Minor | 4.7 |
| [issue-06.md](issue-06.md) | [#95](https://github.com/poridhiEng/poridhi-labs/issues/95) | Security-group port order in the expected block is not guaranteed | 3 Minor | Setup / The network |
| [issue-07.md](issue-07.md) | [#96](https://github.com/poridhiEng/poridhi-labs/issues/96) | `kafka-configs --describe` prints a header and `synonyms={...}` the block omits | 4 Polish | 5.3 |

## Test report

| File | Issue | Title |
|---|---|---|
| [test-report.md](test-report.md) | [#97](https://github.com/poridhiEng/poridhi-labs/issues/97) | `[S2 test] s2-ep04-lab-02 · round 1 · Akash` |

## File structure of each issue file

```
# Issue N of 7

**Filed:** [#NN](url)

Form: <url of the issue form to file by hand>

---

## Title      <- paste into the issue form's title field
## Body       <- paste into the issue form's body field
## Labels     <- apply these labels
```

## Labels

All 7 problem issues:

```
course:mlops-s2
kind:lab-problem
```

The test report:

```
course:mlops-s2
kind:test-report
```

## Filing by hand

Each issue file carries the form URL. Open it, paste the `## Title` block into the
title field and the `## Body` block into the body field, then apply the labels from
the `## Labels` block.

## Filing automatically

The scripts that posted these live in the testing skill, not in this folder:

```
C:\Users\User\.puku-cli\skills\poridhi_lab_testing_skill\scripts\
  file-issues.mjs           posts every issue-NN.md in this folder
  file-test-report.mjs      posts test-report.md as the test report
  verify-no-ai-trace.mjs    scans the filed issues for AI-tooling traces
```

They need `GITHUB_TOKEN` (a classic PAT with `repo` scope) and
`GITHUB_REPO` (defaults to `poridhiEng/poridhi-labs`).

## Still open

Two items are recorded but not filed:

- A possible ~60 s stall when `run_writer.py` bootstraps to paused brokers. The timing
  was never captured, so there is nothing to file yet.
- The `LEADER` variable used in 2.6 is never persisted. It only worked because the steps
  ran in the same shell.

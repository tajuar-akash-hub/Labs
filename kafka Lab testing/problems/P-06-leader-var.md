# [s2-ep04-lab-02] P-06: `LEADER` is captured in one block and used in a later, separate block

> Static desk review. Not yet confirmed on a Poridhi VM; confirm before closing.

| Field | Value |
|---|---|
| **Lab ID** | `s2-ep04-lab-02` |
| **Section** | 2.6 Test and Verify (controller crash) and the restart block after it |
| **Kind** | Content |
| **Severity** | **3 Minor** |
| **Commit tested** | N/A — draft |

## Steps to reproduce

1. Run the 2.6 block, which sets `LEADER=$(kafka kafka-metadata-quorum $B describe --status | awk '/^LeaderId/{print $2}')`.
2. Open a new terminal (or run the restart block in a fresh shell).
3. Run the restart block: `ssh broker-$((LEADER - 100)) docker start controller`.

## Expected

The controller restarts on the host that was killed.

## Actual

`$B`, `$B1` and `$BOOTSTRAP` are persisted to `~/.bashrc`, but `LEADER` is not. With `LEADER` unset, `$((LEADER - 100))` evaluates to `-100`, and the command becomes `ssh broker--100 docker start controller`, which fails.

## Evidence

Environment Setup persists only `BOOTSTRAP`, `B` and `B1` in `~/.bashrc`; `LEADER` is block-local.

## Impact

The lab breaks for any learner who opens a second terminal between the two blocks, as the setup itself anticipates.

## Suggested fix

Persist it: `echo "$LEADER" > ~/lab/controller-leader` then `LEADER=$(cat ~/lab/controller-leader)`. Or re-derive the stopped voter from `kafka-metadata-quorum describe --replication` (the row that is neither `Leader` nor `Follower`).

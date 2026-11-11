# Issue 6 of 7

**Filed:** [#95](https://github.com/poridhiEng/poridhi-labs/issues/95)

Form: https://github.com/poridhiEng/poridhi-labs/issues/new?template=s2-lab-problem.yml

---

## Title

```
[s2-ep04-lab-02] Environment Setup: the security-group port order in the expected block is not guaranteed by the AWS API
```

## Body

```
**Lab ID:** s2-ep04-lab-02

**Section:** Environment Setup / "The network" (firewall block)

**Kind:** Content

**Severity:** 3 Minor

**Commit tested:** d7aa49e

**Steps to reproduce:**

1. Run Environment Setup → "The network" as written, through the firewall block.
2. Compare the output of the last command with the expected block.

**Expected:**

```text
22 22
9094 9094
9092 9093
```

**Actual:**

```text
9094 9094
22 22
9092 9093
```

**Evidence:**

- The command is `aws ec2 describe-security-groups --group-ids $SG --query 'SecurityGroups[0].IpPermissions[].[FromPort,ToPort]' --output text`.
- The API returns `IpPermissions` as an unordered list. The three ingress rules were added in the order 22, 9094, 9092-9093, but the API does not preserve insertion order, so the describe returned them in a different order on this run.
- All three rules were present and correct - only the order differed. The learner has to compare a set of lines against a fixed expected block.

**Impact:**

The expected block implies an ordering the API does not guarantee. A learner whose describe returns a different order sees a mismatch in the setup, before any Kafka content, and cannot tell whether the firewall is wrong.

**Suggested fix:**

Sort the query so the order is deterministic, e.g.

```bash
aws ec2 describe-security-groups --group-ids $SG \
  --query 'sort_by(SecurityGroups[0].IpPermissions[].[FromPort,ToPort], &@[0])' --output text
```

and update the expected block to the sorted order. Alternatively, note in the expected block that the order varies.

**Suggested retest step:**

Re-run the firewall block and confirm the output order is stable and matches the expected block.
```

## Labels

```
course:mlops-s2
kind:lab-problem
```

# [s2-ep04-lab-02] P-13: user-data installs Docker with no retry; a transient mirror `503` silently leaves nodes without Docker

> **Confirmed on the VM, 2026-11-10** (fresh Poridhi VM, `ap-southeast-1`).

| Field | Value |
|---|---|
| **Lab ID** | `s2-ep04-lab-02` |
| **Section** | Environment Setup / "Three brokers" (user-data bootstrap) |
| **Kind** | Content (fragile bootstrap, no failure detection) |
| **Severity** | **2 Major** (lab blocked; recovery is undocumented and manual) |
| **Commit tested** | doc as published 2026-11-10 (commit ID not recorded) |

## Steps to reproduce

1. Run Environment Setup → "Three brokers" as written (unchanged `user-data.sh`).
2. Run the readiness loop from the next block.

## Expected

`brokers answering: 3` within a few minutes, on every run.

## Actual

`brokers answering: 0`. broker-1 and broker-2 never installed Docker:

```text
== broker-1 ==
status: error
ip-10-0-1-11
no-docker
== broker-2 ==
status: error
ip-10-0-1-12
no-docker
== broker-3 ==
status: done
/usr/bin/docker
controller
```

`/var/log/cloud-init-output.log` on both failed nodes:

```text
Err:3 http://ap-southeast-1.ec2.archive.ubuntu.com/ubuntu .../runc...deb
  503  Service Unavailable [IP: 54.254.225.85 80]
E: Unable to fetch some archives, maybe run apt-get update or try with --fix-missing?
cc_scripts_user.py[WARNING]: Failed to run module scripts_user
```

`user-data.sh` runs `apt-get update -q` and `apt-get install -y -q docker.io` once under `set -euo pipefail`, so the first `503` aborts the rest of the script (Docker install, both containers).

## Evidence

- cloud-init status `error` on 2 of 3 nodes; `no-docker` on both.
- Seven package downloads returned `503 Service Unavailable` from the regional EC2 mirror.
- Re-running `apt-get install -y docker.io` a few minutes later succeeded, proving the mirror recovered.

## Impact

A transient regional mirror failure permanently breaks the bootstrap. The lab's readiness loop only prints a smaller number; it never says the VMs are broken or how to fix them, so the learner is stuck with no path forward.

## Suggested fix

- In `user-data.sh`, retry the install, e.g. `apt-get -o Acquire::Retries=10 -y install docker.io`, or wrap it in a bounded retry loop.
- After the readiness loop prints fewer than 3, tell the learner to check `cloud-init status` and point at the recovery command.

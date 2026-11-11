# [s2-ep04-lab-02] P-12: Chapter 1.5 calls `pytest`, but the VM has no pytest, no venv, and no Kafka client

> **WITHDRAWN 2026-11-10 — not a lab defect.** Environment Setup ("Tools and credentials") does create `~/venv` and `pip install`s the lab requirements plus `~/ledgerline`. On the VM, `~/venv/bin/pytest`, `ledgerline` and `confluent_kafka` are all present. The failure happened because the shell was using a different venv created by hand. Do not file this issue.
>
> **Confirmed on the VM, 2026-11-10** (fresh Poridhi VM, Ubuntu 24.04.5).

| Field | Value |
|---|---|
| **Lab ID** | `s2-ep04-lab-02` |
| **Section** | 1.5 Test and Verify |
| **Kind** | Content (missing prerequisite) |
| **Severity** | **1 Blocker** (the step crashes; the check can never pass as written) |
| **Commit tested** | doc as published 2026-11-10 (commit ID not recorded) |

## Steps to reproduce

1. Follow Environment Setup and Chapter 1 on a fresh VM.
2. Run the 1.5 block as written:

```bash
cd ~/lab && pytest -q ~/ledgerline/checks/ep04/lab-02/test_ch1_cluster.py
```

## Expected

The pytest suite runs (and passes, after 1.3).

## Actual

```text
bash: pytest: command not found
```

And:

```text
$ python3 -m pytest --version
/usr/bin/python3: No module named pytest
```

`~/lab` contains only `aws.env`, `lab02-key.pem`, `run_audit.py`, `run_writer.py` — no `venv`. The harness (`checks/ep04/lab-02/conftest.py`) imports `confluent_kafka`, which is also not installed.

## Evidence

- `ls -a ~/lab` → `.  ..  aws.env  lab02-key.pem  run_audit.py  run_writer.py`
- `python3 -m pytest --version` → `No module named pytest`
- `conftest.py` line 14: `from confluent_kafka.admin import AdminClient, NewTopic`

## Impact

Every chapter check in the lab (1.5 and the later `pytest` steps) is unrunnable on a fresh VM. Learners cannot verify any chapter without hand-building a Python environment the lab never mentions.

## Suggested fix

Add a setup block before 1.5 (or in Environment Setup):

```bash
cd ~/lab
sudo apt-get install -y -q python3-venv
python3 -m venv venv
. venv/bin/activate
pip install -q pytest confluent-kafka
```

and have every `pytest` step run from the activated venv (or call `~/lab/venv/bin/pytest`).

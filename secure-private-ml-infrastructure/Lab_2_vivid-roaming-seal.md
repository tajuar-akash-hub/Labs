# Lab 2 (Adapted): Multi-Region ML Inference Failover — Local PC + AWS EC2 over WireGuard, with MinIO

## Context

The original Lab 2 deploys the same Whisper model in **two AWS regions** and uses **AWS Transit Gateway + BGP route propagation + cross-region peering** to elastically shift traffic between them. The user wants the same failover pattern but with these substitutions:

- **One endpoint on their local PC** (the new "primary"), **one endpoint on an AWS EC2** (the new "standby"), instead of two AWS regions.
- **MinIO** as the object store (replacing S3), because MinIO runs on the player's machines and the user prefers it.
- **WireGuard** as the connectivity fabric, replacing TGW + cross-region peering.
- **Route 53 + Lambda** as the failover brain (replacing TGW route-table mutations).
- **Prometheus + Grafana** retained for observability, since that's the pedagogically valuable part of the lab.

The goal is to keep the active-passive failover, health-driven control plane, and observability story intact while collapsing the network footprint from "two regions + S3" to "one region + a tunnel to your home lab".

### User-confirmed substitutions
- Connectivity: **WireGuard (self-managed VPN)**.
- Storage: **MinIO on PC (primary); EC2 fetches weights over VPN**.
- Failover brain: **Lambda + Route 53 failover** record.
- Observability: **Keep Prometheus + Grafana + node_exporter + failover dashboard**.

### Showstoppers to flag up front
1. PC must be **always-on and internet-up** for the primary to be reachable.
2. Home public IP is **dynamic**; WireGuard must be **PC-initiated** with `PersistentKeepalive` so the tunnel survives sleep/wake.
3. The **S3 Gateway Endpoint is gone** — EC2 pulls weights over the tunnel using `aws s3 cp --endpoint-url http://10.99.0.2:9000`.
4. **EventBridge rate(1 minute)** is the minimum granularity; sub-minute polling is achieved with `PersistentKeepalive` + `rate(1 minute)`.
5. **Original lab's BGP pedagogical point is weakened** — failover becomes DNS-driven, not BGP-driven. This is intentional and noted in the plan.

---

## Topology at a glance

| Component | Where | Address | Port(s) |
|---|---|---|---|
| WireGuard server | EC2 `wg-server` (Elastic IP) | `10.99.0.1/24` (tunnel) | UDP 51820 |
| WireGuard client | Your PC | `10.99.0.2/24` (tunnel) | — |
| MinIO | Your PC | `10.99.0.2:9000` / `:9001` (console) | 9000/9001 |
| Whisper (primary) | Your PC | `10.99.0.2:8000` | 8000 |
| Whisper (standby) | EC2 `whisper-ec2` | `10.0.1.30:8000` | 8000 |
| Prometheus + Grafana | EC2 `client-ec2` | `10.0.1.31:9090` / `:3000` | 9090/3000 |
| node_exporter (PC) | Your PC | `10.99.0.2:9100` | 9100 |
| node_exporter (EC2) | EC2s | `10.0.1.30/31:9100` | 9100 |

VPC CIDR: `10.0.0.0/16`. Public subnet: `10.0.1.0/24`. Tunnel subnet: `10.99.0.0/24`. Single AWS region: `ap-southeast-1`.

---

## Implementation Steps

### Step 1 — Reserve region, key pair, Elastic IP
- Region `ap-southeast-1`. Create/select key pair `puku-lab.pem` (`chmod 400`).
- Allocate **one Elastic IP** `eip-wg` (this is the stable WireGuard endpoint).

### Step 2 — Create the VPC
- VPC `10.0.0.0/16`, public subnet `10.0.1.0/24` (auto-assign public IPv4), IGW `igw-lab`, route table entry `0.0.0.0/0 → igw-lab`.
- **No NAT Gateway** (cost). EC2s get public IPs and use the IGW. The WireGuard server acts as the "tunnel router" — it has `ip_forward=1` so traffic from the PC can reach EC2s and vice versa.

### Step 3 — Security groups
- `sg-wg`: UDP 51820 from `0.0.0.0/0`, TCP 22 from your home IP, all traffic from `10.99.0.0/24` and `10.0.0.0/16`.
- `sg-whisper-ec2`: TCP 22 from your home IP, TCP 8000/9100 from `10.99.0.0/24`, all egress (apt + MinIO pull).
- `sg-client-ec2`: TCP 22 from your home IP, TCP 9090/3000/9100 from `10.99.0.0/24` and your home IP.
- `sg-lambda`: no ingress; egress to `10.99.0.2:8000` (PC Whisper via tunnel), Route 53 HTTPS, CloudWatch.

### Step 4 — Launch `wg-server`
`t3.micro`, Amazon Linux 2023, public subnet, public IP enabled, `sg-wg`. User-data:
```bash
amazon-linux-extras install -y epel
yum install -y wireguard-tools iptables-services
echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
sysctl -w net.ipv4.ip_forward=1
systemctl enable --now iptables
iptables -t nat -A POSTROUTING -s 10.99.0.0/24 -o eth0 -j MASQUERADE
service iptables save
```

### Step 6 — Configure `wg0.conf` on the server
```ini
[Interface]
Address = 10.99.0.1/24
ListenPort = 51820
PrivateKey = <SERVER_PRIVATE_KEY>

[Peer]
PublicKey = <PC_PUBLIC_KEY>
AllowedIPs = 10.99.0.2/32, 10.0.0.0/16
PersistentKeepalive = 25
```
`systemctl enable --now wg-quick@wg0`.

### Step 7 — WireGuard on the PC (PC-initiated)
`/etc/wireguard/wg0.conf` (or client UI on Mac/Windows):
```ini
[Interface]
Address = 10.99.0.2/24
PrivateKey = <PC_PRIVATE_KEY>
PostUp = ip route add 10.0.0.0/16 dev wg0 metric 100

[Peer]
PublicKey = <SERVER_PUBLIC_KEY>
Endpoint = <EIP_OF_WG_SERVER>:51820
AllowedIPs = 10.99.0.0/24, 10.0.0.0/16
PersistentKeepalive = 25
```
Linux: `systemctl enable --now wg-quick@wg0`. The **PC** initiates the connection — even if your public IP changes, the tunnel comes back up because the PC keeps trying. Test with `ping 10.99.0.1` from PC and `ping 10.99.0.2` from `wg-server`.

### Step 8 — MinIO on the PC (replaces S3)
```bash
mkdir -p ~/minio/data ~/minio/run
docker run -d --name minio --restart=always \
  -p 9000:9000 -p 9001:9001 \
  -v ~/minio/data:/data \
  -e "MINIO_ROOT_USER=<rootuser>" -e "MINIO_ROOT_PASSWORD=<rootpass>" \
  quay.io/minio/minio server /data --console-address ":9001"
```
Save creds to `~/minio/.env` (chmod 600). Create bucket `whisper-models`. Upload `base.pt` once via the console. Bucket is reachable from EC2s as `http://10.99.0.2:9000`.

### Step 9 — node_exporter on the PC
```bash
docker run -d --name nodeexp --restart=always \
  -p 9100:9100 \
  -v "/proc:/host/proc:ro" -v "/sys:/host/sys:ro" -v "/:/rootfs:ro" \
  prom/node-exporter:v1.8.0 \
  --path.rootfs=/rootfs --collector.filesystem.mount-points-exclude='^/(sys|proc|dev|host|etc)($$|/)'
```
Reachable as `http://10.99.0.2:9100/metrics` once WireGuard is up.

### Step 10 — Whisper (FastAPI) on the PC
Service `app.py` (FastAPI + `faster-whisper`):
```python
from fastapi import FastAPI, UploadFile, File
from faster_whisper import WhisperModel
import uvicorn
model = WhisperModel("base", compute_type="int8")
app = FastAPI()

@app.get("/healthz")
def healthz(): return {"ok": True, "model": "base", "host": "pc"}

@app.post("/predict")
def predict(audio: UploadFile = File(...)):
    segs, _ = model.transcribe(audio.file)
    return {"text": " ".join(s.text for s in segs)}

@app.get("/metrics")  # Prometheus exposition from prometheus_client counters/histograms
def metrics(): return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
```
Run with `uvicorn app:app --host 0.0.0.0 --port 8000` as a systemd service or docker-compose. Confirm from `wg-server`: `curl http://10.99.0.2:8000/healthz`.

### Step 11 — Launch `whisper-ec2` (standby)
`t3.small`, Amazon Linux 2023, public subnet, **fixed private IP `10.0.1.30`**, `sg-whisper-ec2`. User-data:
```bash
yum install -y docker python3 pip3 awscli
systemctl enable --now docker
pip3 install fastapi uvicorn faster-whisper

mkdir -p /opt/whisper/models
AWS_ACCESS_KEY_ID=<rootuser> AWS_SECRET_ACCESS_KEY=<rootpass> \
  aws s3 cp --recursive --endpoint-url http://10.99.0.2:9000 \
  s3://whisper-models/base/ /opt/whisper/models/base/

# Same app.py deployed to /opt/whisper; run with uvicorn bound 0.0.0.0:8000
nohup uvicorn app:app --host 0.0.0.0 --port 8000 &
docker run -d --name nodeexp --restart=always -p 9100:9100 prom/node-exporter:v1.8.0
```
The key replacement for the original lab's S3 Gateway Endpoint: weights are fetched via `aws s3 cp --endpoint-url http://10.99.0.2:9000`. Set `~/.aws/config` `addressing_style = path`.

### Step 12 — Launch `client-ec2` (Prometheus + Grafana)
`t3.small`, Amazon Linux 2023, public subnet, private IP `10.0.1.31`, `sg-client-ec2`. User-data:
```bash
yum install -y docker
systemctl enable --now docker
docker run -d --name prom --restart=always -p 9090:9090 \
  -v /opt/prom:/etc/prometheus prom/prometheus:v2.54.0
docker run -d --name grafana --restart=always -p 3000:3000 grafana/grafana
```
`/opt/prom/prometheus.yml`:
```yaml
scrape_configs:
  - job_name: pc-node           ; static_configs: [{ targets: ['10.99.0.2:9100'] }]
  - job_name: pc-whisper        ; static_configs: [{ targets: ['10.99.0.2:8000'] }]
  - job_name: ec2-whisper-node  ; static_configs: [{ targets: ['10.0.1.30:9100'] }]
  - job_name: ec2-whisper-app   ; static_configs: [{ targets: ['10.0.1.30:8000'] }]
```

### Step 13 — IAM for the failover Lambda
Role `lambda-route53-failover`:
- `AWSLambdaVPCAccessExecutionRole` (managed).
- `route53:ChangeResourceRecordSets` on the hosted zone ARN.
- `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents` on the function log group.
- `dynamodb:GetItem`, `dynamodb:PutItem` on the state table.

### Step 14 — DynamoDB state table `failover-state`
Free-tier, on-demand. PK `id` (string). Stores `fails` (counter) and `active` (current A-record value). DynamoDB replaces the original lab's Lambda module-level `state` dict so multiple invocations survive cold starts.

### Step 15 — Route 53 private hosted zone `hybrid.lab.`
Create private hosted zone for the VPC. Single A record `whisper.hybrid.lab.` with **TTL 30**. The Lambda updates this record's value (`UPSERT`) when failover or failback happens. (Alternative: AWS-native Route 53 health check failover routing policy. We chose programmatic switch for parity with the original Lambda-driven pattern.)

### Step 16 — Failover Lambda `route53-failover`
Python 3.12, attached to VPC subnet `10.0.1.0/24` with `sg-lambda`. Environment: `HZ_ID`, `RECORD_NAME`, `PRIMARY_IP=10.99.0.2`, `STANDBY_IP=10.0.1.30`, `FAIL_THRESHOLD=3`, `STATE_TABLE=failover-state`.

```python
import os, json, boto3, urllib.request
r53 = boto3.client("route53")
ddb = boto3.resource("dynamodb").Table(os.environ["STATE_TABLE"])

def probe(ip):
    try:
        with urllib.request.urlopen(f"http://{ip}:8000/healthz", timeout=2) as r:
            return r.status == 200
    except Exception:
        return False

def upsert_a(value):
    r53.change_resource_record_sets(
        HostedZoneId=os.environ["HZ_ID"],
        ChangeBatch={"Changes": [{"Action": "UPSERT",
            "ResourceRecordSet": {"Name": os.environ["RECORD_NAME"], "Type": "A", "TTL": 30,
                                 "ResourceRecords": [{"Value": value}]}}]})

def handler(event, context):
    primary_ok = probe(os.environ["PRIMARY_IP"])
    s = ddb.get_item(Key={"id": "failover"}).get("Item") or {"fails": 0, "active": os.environ["PRIMARY_IP"]}
    fails, active = int(s.get("fails", 0)), s.get("active", os.environ["PRIMARY_IP"])
    if primary_ok:
        if active != os.environ["PRIMARY_IP"]: upsert_a(PRIMARY_IP); active = PRIMARY_IP
        fails = 0
    else:
        fails += 1
        if fails >= int(os.environ["FAIL_THRESHOLD"]) and active != os.environ["STANDBY_IP"]:
            upsert_a(STANDBY_IP); active = STANDBY_IP
    ddb.put_item(Item={"id": "failover", "fails": fails, "active": active})
    return {"primary_ok": primary_ok, "fails": fails, "active": active}
```

### Step 17 — Schedule the Lambda
EventBridge rule `rate(1 minute)` → Lambda ARN. Lambda reserved concurrency = 1.

### Step 18 — Grafana dashboard
Import the original lab's failover dashboard JSON; replace panels with:
- **PC request rate**: `rate(whisper_requests_total{job="pc-whisper"}[1m])`.
- **EC2 request rate**: `rate(whisper_requests_total{job="ec2-whisper-app"}[1m])`.
- **DNS target**: `route53_record_value{record="whisper.hybrid.lab."}` (small custom exporter) or just a stat panel updated by a Lambda-side webhook.
- **WireGuard handshake age** on the PC: `time() - wg_latest_handshake_seconds{peer=...}` (custom node_exporter textfile collector).

### Step 19 — Test failover
1. Baseline: `dig +short whisper.hybrid.lab.` from inside the VPC → `10.99.0.2`. `curl http://whisper.hybrid.lab.:8000/healthz` from `client-ec2` returns `{"host": "pc"}`.
2. On the PC: `sudo systemctl stop whisper` (or `docker stop whisper`).
3. After ~3 Lambda ticks (~3 min), `dig` returns `10.0.1.30`. Grafana shows PC RPS → 0, EC2 RPS climbing.

### Step 20 — Test failback
1. On the PC: `sudo systemctl start whisper`. Verify `http://10.99.0.2:8000/healthz` returns 200 from `wg-server`.
2. Next Lambda tick: `primary_ok=True`, `active` flips back to `10.99.0.2`.
3. `dig` returns `10.99.0.2` again.

### Step 21 — Teardown (reverse order)
1. Delete EventBridge rule.
2. Delete Lambda.
3. Delete DynamoDB table.
4. Delete Route 53 records → hosted zone.
5. Release `eip-wg`.
6. Terminate `whisper-ec2`, `client-ec2`, `wg-server` (in this order).
8. Delete IAM role.
9. On PC: `docker stop minio nodeexp whisper`; `wg-quick down wg0`; remove `wg0.conf` and systemd unit.
10. Delete security groups, route table, subnet, IGW, VPC.
11. Delete CloudWatch log groups.

---

## Critical files / assets

### To be created
- `/tmp/health-lambda/route53_failover.py` — the failover Lambda source.
- `/tmp/whisper-userdata/primary.sh` — PC Whisper launch script.
- `/tmp/whisper-userdata/standby.sh` — EC2 Whisper launch script (used in Step 11).
- `/tmp/wg-server-userdata.sh` — WireGuard server bootstrap (Step 4).
- `/tmp/client-userdata.sh` — Prometheus + Grafana bootstrap (Step 12).
- `/etc/wireguard/wg0.conf` on PC and on `wg-server`.

### To be reused / referenced
- **Original Lab 2** `app.py` FastAPI body — same code on PC and EC2.
- **Original Lab 2** Grafana dashboard JSON — replaced panels as in Step 18.

---

## Verification

Mirror of the original lab's verification list with substitutions:

- [ ] `wg-quick show wg0` on both sides shows recent handshake (≤ 2 min).
- [ ] `ping 10.99.0.1` from PC works; `ping 10.99.0.2` from `wg-server` works.
- [ ] `ping 10.0.1.30` from PC over `wg0` works; `ping 10.99.0.2` from `client-ec2` works.
- [ ] `aws --endpoint-url http://10.99.0.2:9000 s3 ls` from `whisper-ec2` lists `whisper-models`.
- [ ] `curl http://10.99.0.2:8000/healthz` → `{"host": "pc"}`.
- [ ] `curl http://10.0.1.30:8000/healthz` → `{"host": "ec2"}`.
- [ ] `/metrics` reachable on both endpoints.
- [ ] Prometheus `http://10.0.1.31:9090/targets` shows all four jobs `UP`.
- [ ] `dig whisper.hybrid.lab.` from inside VPC → `10.99.0.2`.
- [ ] Lambda logs in `/aws/lambda/route53-failover` show one invocation/minute, `fails=0`, `active=10.99.0.2`.
- [ ] Grafana dashboard renders PC + EC2 metrics.
- [ ] **Failover drill**: kill PC Whisper → `dig` flips to `10.0.1.30` within ~3 min, Grafana panel flips.
- [ ] **Failback drill**: restart PC Whisper → `dig` flips back to `10.99.0.2` within ~1 min.
- [ ] **Cost guardrail**: no ELIPs, no NAT GW, no ALB. Only t3.micro/t3.small instances. Tear down immediately after testing.

---

## Known limitations / things to flag

1. **Failover latency is ~3 minutes** because EventBridge is `rate(1 minute)` and `FAIL_THRESHOLD=3`. The original lab also uses 1-minute scheduling with a 3-streak threshold, so parity is preserved. For sub-minute, implement a self-rescheduling Lambda loop as in the original lab's notes.
2. **No NAT on the PC side** — when EC2 fetches weights from PC, EC2 → WG-server → PC uses server-side NAT (`MASQUERADE`). The PC's local network sees traffic come from the WG server's tunnel IP, not the EC2's IP. Acceptable for the lab.
3. **Lambda module state was the original lab's pattern.** DynamoDB is added here because EC2 cold starts can reset module state and we want the failover state to be durable. Documented as a deliberate departure.
4. **No internet-isolation guarantee on the PC** — the PC can still reach the internet via its local network. The lab does not enforce Lab 1's "no IGW" rule on the PC. Documented and noted.
5. **BGP pedagogical point weakened** — this lab deliberately substitutes DNS-driven failover. If they want to preserve the BGP feel, the alternative is to add a small `bird` BGP daemon on the WG server advertising routes to a simulated upstream, but this is out of scope.
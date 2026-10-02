# Lab 2 Walkthrough: Hybrid ML Inference Failover with WireGuard, MinIO, and Route 53

A from-scratch, follow-along guide. Every command is spelled out. Every screenshot slot has a filename and a one-line caption explaining what should be in it. Drop your captured PNGs into the `screenshots/` folder next to this file, with the filenames shown in the captions, and the lab becomes a self-documenting proof of work.

## Before you start

What this lab proves : you can build a working active-passive failover for an ML inference service that survives a primary endpoint going down, with a health-driven control plane (Route 53 + Lambda) and full observability (Prometheus + Grafana). The "primary" is a Whisper speech-to-text server running on your laptop, reachable over a WireGuard tunnel into an AWS VPC. The "standby" is the same Whisper server running on an EC2 in the same VPC. A Lambda checks both endpoints once a minute and flips the Route 53 A record for `whisper.hybrid.lab.` when the primary stops responding.

Time estimate : about 90 minutes for a first-time run, most of which is waiting for EC2 instances and user-data scripts to finish. Subsequent runs are about 30 minutes.

What you need :

- A PC that can stay on for the whole lab. **Windows + WSL2, macOS, or bare Linux all work.**
- An AWS account with a credit card attached (free tier covers most of this if you tear down promptly).
- A pair of small files for the YOLO workload if you continue into the extension: a 5 MB audio file (WAV or MP3) and an image file (JPG or PNG). The base lab does not need these.
- About 30 screenshot slots to fill. The list of filenames is in `screenshot-inventory.md` (same folder) and inline below.

## Phase 0.A : Install the toolchain on the PC

Before you can do anything, the PC needs the right binaries. WireGuard handles the tunnel, Docker runs MinIO and Whisper, OpenSSL handles certs later in the extension, and the AWS CLI drives every later step.

If you are on Windows 10/11, the cleanest path is WSL2. Open PowerShell as Administrator (right-click the Start menu, choose "Terminal (Admin)" or "Windows PowerShell (Admin)"), then run:

```powershell
wsl --install -d Ubuntu-22.04
wsl --set-default-version 2
wsl -l -v
```

You should see `Ubuntu-22.04` listed with VERSION 2. If you are on macOS, skip WSL and use the built-in Terminal.

Open the WSL window (Start menu → "Ubuntu 22.04") or, on macOS, open Terminal. Inside, run:

```bash
sudo apt update
sudo apt install -y wireguard wireguard-tools docker.io docker-compose-plugin \
  openssl dnsutils curl jq unzip python3-pip ca-certificates
sudo usermod -aG docker $USER
newgrp docker
docker run --rm hello-world
```

Expected : the last line of `docker run hello-world` is "Hello from Docker!". If you see "permission denied" on `/var/run/docker.sock`, log out of the WSL/Ubuntu session and back in so the docker group membership refreshes.

On macOS, the equivalent is:

```bash
brew install wireguard-tools docker docker-compose openssl bind jq python@3.11
open -a Docker
```

Docker Desktop launches; accept the privileged helper prompt that appears.

Screenshot `screenshots/01-wsl2-installed.png` (the `wsl -l -v` output showing Ubuntu-22.04 / VERSION 2).
Screenshot `screenshots/02-apt-install-done.png` (terminal showing the successful install summary).
Screenshot `screenshots/03-docker-hello-world.png` (terminal showing "Hello from Docker!").

## Phase 0.B : Create the AWS account and the IAM user

Open https://console.aws.amazon.com/ in your browser. Sign in with your root account, or click **Create a new AWS account** if this is your first time. AWS asks for a credit card even for free-tier usage; new accounts get 12 months free tier plus some always-free services.

Once you are in the console, click the region selector in the top-right (it shows something like "US East (N. Virginia)" by default) and choose **Asia Pacific (Singapore) ap-southeast-1**. Every later step assumes this region.

Now create a billing alarm. Click the search bar at the top of the console, type **Billing and Cost Management**, and open it. In the left sidebar, click **Budgets** → orange **Create budget** button → choose **Cost budget** → click **Next**. Set Name to "lab-budget-listing", Amount to 5 USD, Period to Monthly. Click **Next** until you reach **Notifications**. Add a notification: Threshold 85%, enter your real email. Click **Create budget**. AWS will email you when you cross 85% of $5.

Now create the IAM user you will use from the CLI. In the console search bar type **IAM** and press Enter. In the left sidebar click **Users** → orange **Create user** button. **User name**: `lab2-admin`. Click **Next**. On the permissions step, choose **Attach policies directly** → scroll down and tick **AdministratorAccess** (this is a lab account; production would scope this much tighter). Click **Next** → **Next** → **Create user**.

Click the new user name (`lab2-admin`) in the list. Go to the **Security credentials** tab. Scroll to **Access keys** and click **Create access key**. Choose **Command Line Interface (CLI)** as the use case, tick the acknowledgement, click **Next**. Set a description tag of "lab2-cli", click **Create access key**. The next page shows your **Access key ID** (starts with `AKIA...`) and **Secret access key**. **Copy both now**; AWS will never show the secret again. Click **Done**.

Back in the terminal on the PC:

```bash
cat > ~/aws-creds.env <<EOF
export AWS_ACCESS_KEY_ID=AKIA...paste here...
export AWS_SECRET_ACCESS_KEY=...paste here...
export AWS_DEFAULT_REGION=ap-southeast-1
EOF
chmod 600 ~/aws-creds.env
ls -l ~/aws-creds.env
```

The `ls -l` output should report permissions `-rw-------` (exactly `600`). Anything looser and your secret is world-readable; tighten with `chmod 600 ~/aws-creds.env`.

Screenshot `screenshots/06-iam-user-created.png` (IAM console showing the `lab2-admin` user with the access key listed).

## Phase 0.C : Install and configure the AWS CLI

Still in the PC terminal:

```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o /tmp/awscliv2.zip
cd /tmp && unzip -o awscliv2.zip && sudo ./aws/install
aws --version
```

Expected : `aws-cli/2.x.x` (the exact patch version does not matter, but it should be a 2.x).

Now wire the keys into the AWS CLI:

```bash
source ~/aws-creds.env
aws configure set aws_access_key_id "$AWS_ACCESS_KEY_ID"
aws configure set aws_secret_access_key "$AWS_SECRET_ACCESS_KEY"
aws configure set default.region ap-southeast-1
aws configure set default.output json

aws sts get-caller-identity
aws s3 ls
```

Expected : `aws sts get-caller-identity` returns JSON with your Account ID and the `arn:aws:iam::...:user/lab2-admin` ARN. `aws s3 ls` returns `An error occurred (AccessDenied)` because no buckets exist yet; that error is the proof that your keys are valid.

Screenshot `screenshots/04-aws-sts-get-caller-identity.png` (the JSON response).
Screenshot `screenshots/05-aws-region-selector.png` (AWS console with ap-southeast-1 selected in the top-right).

## Phase 0.D : Build the AWS side and the home network

This is the bulk of the lab. Each sub-step below covers one logical piece, ends with a screenshot slot, and is small enough to debug if something goes wrong.

### 0.D.1 : Reserve region, key pair, Elastic IP

The Elastic IP is the stable address your WireGuard server will live at, even if you later stop and restart the instance. Allocate it now so it can associate with the WireGuard instance once that launches.

```bash
export AWS_REGION=ap-southeast-1
aws ec2 describe-availability-zones --region $AWS_REGION \
  --query 'AvailabilityZones[0].ZoneName' --output text
```

Expected : `ap-southeast-1a`.

```bash
mkdir -p ~/keys && cd ~/keys
aws ec2 create-key-pair --key-name puku-lab --query 'KeyMaterial' --output text > puku-lab.pem
chmod 400 puku-lab.pem
ls -l ~/keys/puku-lab.pem
```

Expected : `-r--------` on the `.pem` file. Without `400` AWS will refuse to use the key.

```bash
EIP_ALLOC=$(aws ec2 allocate-address --domain vpc \
  --tag-specifications 'ResourceType=elastic-ip,Tags=[{Key=Name,Value=eip-wg}]' \
  --query 'AllocationId' --output text)
EIP=$(aws ec2 describe-addresses --allocation-ids $EIP_ALLOC \
  --query 'Addresses[0].PublicIp' --output text)
echo "export EIP=$EIP" >> ~/aws-creds.env
echo "export EIP_ALLOC=$EIP_ALLOC" >> ~/aws-creds.env
echo "Elastic IP: $EIP"
```

Expected : a fresh IPv4 like `54.251.x.y`. Save `$EIP` mentally; you will paste it into the WireGuard client config in 0.D.5.

Screenshot `screenshots/09-eip-allocated.png` (EC2 console → Elastic IPs, showing `eip-wg` and its public IP).

### 0.D.2 : Create the VPC, subnet, route table, and IGW

The whole lab fits inside one VPC. The public subnet `10.0.1.0/24` holds the WireGuard server and the two EC2s. There is no NAT Gateway (cost); the EC2s reach the internet through the IGW directly.

```bash
VPC=$(aws ec2 create-vpc --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=lab2-vpc}]' \
  --query 'Vpc.VpcId' --output text)

SUBNET=$(aws ec2 create-subnet --vpc-id $VPC --cidr-block 10.0.1.0/24 \
  --availability-zone ap-southeast-1a --map-public-ip-on-launch \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=lab2-public-subnet}]' \
  --query 'Subnet.SubnetId' --output text)

aws ec2 modify-vpc-attribute --vpc-id $VPC --enable-dns-hostnames
aws ec2 modify-vpc-attribute --vpc-id $VPC --enable-dns-support

IGW=$(aws ec2 create-internet-gateway \
  --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=lab2-igw}]' \
  --query 'InternetGateway.InternetGatewayId' --output text)
aws ec2 attach-internet-gateway --internet-gateway-id $IGW --vpc-id $VPC

RTB=$(aws ec2 create-route-table --vpc-id $VPC \
  --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=lab2-rt}]' \
  --query 'RouteTable.RouteTableId' --output text)
aws ec2 create-route --route-table-id $RTB --destination-cidr-block 0.0.0.0/0 --gateway-id $IGW
aws ec2 associate-route-table --subnet-id $SUBNET --route-table-id $RTB

cat >> ~/aws-creds.env <<EOF
export VPC=$VPC
export SUBNET=$SUBNET
export IGW=$IGW
export RTB=$RTB
EOF
```

Expected : four IDs starting with `vpc-`, `subnet-`, `igw-`, `rtb-`. If `create-route` complains "Route Already Exists", a default route was added by the AWS CLI automatically; that is fine.

Screenshot `screenshots/07-vpc-created.png` (VPC console with `lab2-vpc` selected, CIDR `10.0.0.0/16`).
Screenshot `screenshots/08-subnet-route-table.png` (Route table console with the destination `0.0.0.0/0` pointing at `lab2-igw`).

### 0.D.3 : Create the three security groups

Each EC2 gets its own security group. The WireGuard server accepts UDP 51820 from the world and SSH from your home IP. The Whisper standby accepts Whisper traffic only from the tunnel subnet (`10.99.0.0/24`) so the model is not exposed to the internet. The client EC2 (Prometheus/Grafana) accepts the UI ports from your home IP and from the tunnel subnet.

```bash
HOME_IP=$(curl -s https://checkip.amazonaws.com)
echo "Your home IP: $HOME_IP"

SG_WG=$(aws ec2 create-security-group --group-name sg-wg --description "WireGuard server" \
  --vpc-id $VPC --query 'GroupId' --output text)
aws ec2 authorize-security-group-ingress --group-id $SG_WG --protocol udp --port 51820 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $SG_WG --protocol tcp --port 22 --cidr $HOME_IP/32
aws ec2 authorize-security-group-ingress --group-id $SG_WG --protocol tcp --port 0-65535 --cidr 10.99.0.0/24
aws ec2 authorize-security-group-ingress --group-id $SG_WG --protocol tcp --port 0-65535 --cidr 10.0.0.0/16
aws ec2 authorize-security-group-ingress --group-id $SG_WG --protocol icmp --port -1 --cidr 10.99.0.0/24

SG_WHISPER=$(aws ec2 create-security-group --group-name sg-whisper-ec2 --description "Whisper standby" \
  --vpc-id $VPC --query 'GroupId' --output text)
aws ec2 authorize-security-group-ingress --group-id $SG_WHISPER --protocol tcp --port 22 --cidr $HOME_IP/32
aws ec2 authorize-security-group-ingress --group-id $SG_WHISPER --protocol tcp --port 8000 --cidr 10.99.0.0/24
aws ec2 authorize-security-group-ingress --group-id $SG_WHISPER --protocol tcp --port 9100 --cidr 10.99.0.0/24

SG_CLIENT=$(aws ec2 create-security-group --group-name sg-client-ec2 --description "Client EC2 monitoring" \
  --vpc-id $VPC --query 'GroupId' --output text)
aws ec2 authorize-security-group-ingress --group-id $SG_CLIENT --protocol tcp --port 22 --cidr $HOME_IP/32
aws ec2 authorize-security-group-ingress --group-id $SG_CLIENT --protocol tcp --port 9090 --cidr 10.99.0.0/24
aws ec2 authorize-security-group-ingress --group-id $SG_CLIENT --protocol tcp --port 3000 --cidr 10.99.0.0/24
aws ec2 authorize-security-group-ingress --group-id $SG_CLIENT --protocol tcp --port 9100 --cidr 10.99.0.0/24
aws ec2 authorize-security-group-ingress --group-id $SG_CLIENT --protocol tcp --port 9090 --cidr $HOME_IP/32
aws ec2 authorize-security-group-ingress --group-id $SG_CLIENT --protocol tcp --port 3000 --cidr $HOME_IP/32

SG_LAMBDA=$(aws ec2 create-security-group --group-name sg-lambda --description "Failover Lambda" \
  --vpc-id $VPC --query 'GroupId' --output text)

cat >> ~/aws-creds.env <<EOF
export SG_WG=$SG_WG
export SG_WHISPER=$SG_WHISPER
export SG_CLIENT=$SG_CLIENT
export SG_LAMBDA=$SG_LAMBDA
EOF
```

Expected : four IDs starting with `sg-`. Verify any one with `aws ec2 describe-security-groups --group-ids $SG_WG --query 'SecurityGroups[0].IpPermissions'` and you should see the rules listed.

### 0.D.4 : Launch the WireGuard server

```bash
AMI=$(aws ec2 describe-images --owners 137112412989 \
  --filters "Name=name,Values=al2023-ami-2023.*-x86_64" \
  --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' --output text)
echo "AMI: $AMI"

WG_USERDATA='#!/bin/bash
amazon-linux-extras install -y epel
yum install -y wireguard-tools iptables-services
echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
sysctl -w net.ipv4.ip_forward=1
systemctl enable --now iptables
iptables -t nat -A POSTROUTING -s 10.99.0.0/24 -o eth0 -j MASQUERADE
service iptables save'

WG_INSTANCE=$(aws ec2 run-instances \
  --image-id $AMI --instance-type t3.micro \
  --subnet-id $SUBNET --associate-public-ip-address \
  --security-group-ids $SG_WG \
  --key-name puku-lab \
  --private-ip-address 10.0.1.10 \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=wg-server}]' \
  --user-data "$WG_USERDATA" \
  --query 'Instances[0].InstanceId' --output text)

aws ec2 wait instance-running --instance-ids $WG_INSTANCE
aws ec2 associate-address --instance-id $WG_INSTANCE --allocation-id $EIP_ALLOC
echo "export WG_INSTANCE=$WG_INSTANCE" >> ~/aws-creds.env
echo "wg-server: $WG_INSTANCE at $EIP"
```

Expected : the instance is `running` and the Elastic IP is now associated. If `associate-address` says "Address already associated", your EIP was linked by an earlier `run-instances` call that auto-associated a public IP; that is harmless but you will lose the EIP on termination unless you disassociate first.

Screenshot `screenshots/10-wg-server-launched.png` (EC2 console with `wg-server` selected, showing the Elastic IP `eip-wg` in the public IPv4 field).

### 0.D.5 : Generate WireGuard keys and write both configs

WireGuard is asymmetric: each peer has its own keypair. The server's `[Peer]` section gets the **PC's public key**; the PC's `[Peer]` section gets the **server's public key**.

Generate both keypairs on the PC (this is just where you happen to be running the commands; the private keys then get copied to the right machine).

```bash
wg genkey | tee ~/keys/wg_server_private.key | wg pubkey > ~/keys/wg_server_public.key
wg genkey | tee ~/keys/pc_private.key       | wg pubkey > ~/keys/pc_public.key
chmod 600 ~/keys/wg_server_private.key ~/keys/pc_private.key
echo "Server pub: $(cat ~/keys/wg_server_public.key)"
echo "PC pub:     $(cat ~/keys/pc_public.key)"
```

Expected : two base64 lines, 44 characters each.

Build the **server** config and push it to `wg-server`:

```bash
SERVER_PRIV=$(cat ~/keys/wg_server_private.key)
PC_PUB=$(cat ~/keys/pc_public.key)

cat > /tmp/wg0-server.conf <<EOF
[Interface]
Address = 10.99.0.1/24
ListenPort = 51820
PrivateKey = $SERVER_PRIV

[Peer]
PublicKey = $PC_PUB
AllowedIPs = 10.99.0.2/32, 10.0.0.0/16
PersistentKeepalive = 25
EOF

scp -i ~/keys/puku-lab.pem /tmp/wg0-server.conf ec2-user@$EIP:/tmp/wg0.conf
ssh -i ~/keys/puku-lab.pem ec2-user@$EIP "sudo mv /tmp/wg0.conf /etc/wireguard/wg0.conf && \
  sudo chmod 600 /etc/wireguard/wg0.conf && \
  sudo systemctl enable --now wg-quick@wg0 && \
  sudo wg show wg0"
```

Expected : `sudo wg show wg0` on the server reports `interface: wg0`, `public key: <server pub>`, `listening port: 51820`, and no peer yet.

Build the **PC** config and bring the interface up:

```bash
SERVER_PUB=$(cat ~/keys/wg_server_public.key)
PC_PRIV=$(cat ~/keys/pc_private.key)

sudo tee /etc/wireguard/wg0.conf >/dev/null <<EOF
[Interface]
Address = 10.99.0.2/24
PrivateKey = $PC_PRIV
PostUp = ip route add 10.0.0.0/16 dev wg0 metric 100

[Peer]
PublicKey = $SERVER_PUB
Endpoint = $EIP:51820
AllowedIPs = 10.99.0.0/24, 10.0.0.0/16
PersistentKeepalive = 25
EOF

sudo chmod 600 /etc/wireguard/wg0.conf
sudo systemctl enable --now wg-quick@wg0
sudo wg show wg0
```

Expected : the `peer` section now shows an `endpoint: $EIP:51820` and `latest handshake:` is fresh (within the last 30 seconds).

Screenshot `screenshots/11-wg-keys-generated.png` (terminal with the four key files and their content).
Screenshot `screenshots/12-wg0-conf-server.png` (the `cat /etc/wireguard/wg0.conf` on the server, plus `wg show wg0`).
Screenshot `screenshots/13-wg0-conf-pc.png` (the same on the PC).

### 0.D.6 : Confirm the tunnel works in both directions

```bash
# On the PC, ping the server's tunnel address
ping -c 3 10.99.0.1
```

Expected : `3 transmitted, 3 received, 0% packet loss`.

```bash
# On the server, ping the PC's tunnel address
ssh -i ~/keys/puku-lab.pem ec2-user@$EIP "ping -c 3 10.99.0.2"
```

Expected : `3 transmitted, 3 received, 0% packet loss`. If the second ping fails but the first works, your iptables MASQUERADE rule did not persist. Re-run on the server:

```bash
ssh -i ~/keys/puku-lab.pem ec2-user@$EIP "sudo iptables -t nat -A POSTROUTING -s 10.99.0.0/24 -o eth0 -j MASQUERADE && sudo service iptables save"
```

Screenshot `screenshots/14-wg-handshake.png` (`wg show wg0` on the PC with a fresh handshake and non-zero transfer).
Screenshot `screenshots/15-ping-both-ways.png` (two terminal panes side by side, both pings succeeding).

### 0.D.7 : MinIO on the PC

MinIO is an S3-compatible object store. We use it as the model registry instead of S3 so the lab does not depend on any AWS service beyond EC2/IAM.

```bash
mkdir -p ~/minio/data ~/minio/run
cat > ~/minio/.env <<EOF
MINIO_ROOT_USER=rootuser
MINIO_ROOT_PASSWORD=$(openssl rand -hex 16)
EOF
chmod 600 ~/minio/.env
source ~/minio/.env

docker run -d --name minio --restart=always \
  -p 9000:9000 -p 9001:9001 \
  -v ~/minio/data:/data \
  -e "MINIO_ROOT_USER=$MINIO_ROOT_USER" \
  -e "MINIO_ROOT_PASSWORD=$MINIO_ROOT_PASSWORD" \
  quay.io/minio/minio server /data --console-address ":9001"

# Wait for MinIO to be ready
for i in $(seq 1 30); do
  curl -sf http://10.99.0.2:9000/minio/health/live && break
  sleep 2
done
echo "MinIO is up"

# Install and use the MinIO client
wget -q https://dl.min.io/client/mc/release/linux-amd64/mc -O ~/mc && chmod +x ~/mc
~/mc alias set local http://10.99.0.2:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD"
~/mc mb local/whisper-models

# Upload a dummy base.pt so the EC2 pull has something to fetch
echo "dummy weights for $(date)" > ~/minio/data/whisper-models/base.pt
~/mc cp ~/minio/data/whisper-models/base.pt local/whisper-models/base.pt
~/mc ls local/whisper-models
```

Expected : `mc ls` lists `base.pt`. Open `http://10.99.0.2:9001` in a browser (the address goes over the tunnel; if you are off the home network, use SSH local forwarding: `ssh -L 9001:10.99.0.2:9001 user@home`, then open `http://localhost:9001`). Log in with the credentials from `~/minio/.env`. You should see the `whisper-models` bucket.

Screenshot `screenshots/16-minio-console.png` (browser showing the `whisper-models` bucket in MinIO's web console).
Screenshot `screenshots/17-basept-uploaded.png` (`mc ls` showing `base.pt`).

### 0.D.8 : node_exporter on the PC

```bash
docker run -d --name nodeexp --restart=always \
  -p 9100:9100 \
  -v "/proc:/host/proc:ro" -v "/sys:/host/sys:ro" -v "/:/rootfs:ro" \
  prom/node-exporter:v1.8.0 \
  --path.rootfs=/rootfs \
  --collector.filesystem.mount-points-exclude='^/(sys|proc|dev|host|etc)($$|/)'

sleep 5
curl -s http://10.99.0.2:9100/metrics | head -10
```

Expected : the response starts with `# HELP go_gc_duration_seconds ...` and `# TYPE go_gc_duration_seconds summary`. If "connection refused", the container is not up; `docker ps -a` and `docker logs nodeexp`.

### 0.D.9 : Whisper FastAPI on the PC

```bash
mkdir -p ~/whisper && cd ~/whisper
cat > app.py <<'EOF'
from fastapi import FastAPI
from fastapi.responses import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import uvicorn

app = FastAPI()

@app.get("/healthz")
def healthz():
    return {"ok": True, "model": "base", "host": "pc"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

pip3 install --user fastapi uvicorn prometheus_client

sudo tee /etc/systemd/system/whisper.service >/dev/null <<EOF
[Unit]
Description=Whisper FastAPI on PC
After=network.target

[Service]
User=$USER
WorkingDirectory=$HOME/whisper
ExecStart=$HOME/.local/bin/uvicorn app:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now whisper
sleep 5
curl http://10.99.0.2:8000/healthz
```

Expected : `{"ok": true, "model": "base", "host": "pc"}` with HTTP 200.

Screenshot `screenshots/18-whisper-pc-healthz.png` (the curl response above).

### 0.D.10 : Launch the Whisper standby EC2

The user-data script for the standby pulls the dummy `base.pt` from the PC's MinIO over the WireGuard tunnel, then starts the same Whisper FastAPI service.

```bash
source ~/minio/.env

WHISPER_USERDATA=$(cat <<EOF
#!/bin/bash
yum install -y docker python3-pip
systemctl enable --now docker
pip3 install fastapi uvicorn prometheus_client

mkdir -p /opt/whisper
cat > /opt/whisper/app.py <<'PYEOF'
from fastapi import FastAPI
from fastapi.responses import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import uvicorn
app = FastAPI()
@app.get("/healthz")
def healthz(): return {"ok": True, "model": "base", "host": "ec2"}
@app.get("/metrics")
def metrics(): return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
PYEOF

mkdir -p /opt/whisper/models
AWS_ACCESS_KEY_ID=$MINIO_ROOT_USER AWS_SECRET_ACCESS_KEY=$MINIO_ROOT_PASSWORD \\
  aws s3 cp --recursive --endpoint-url http://10.99.0.2:9000 \\
  s3://whisper-models/ /opt/whisper/models/

nohup uvicorn app:app --host 0.0.0.0 --port 8000 &
docker run -d --name nodeexp --restart=always -p 9100:9100 prom/node-exporter:v1.8.0
EOF
)

WHISPER_INSTANCE=$(aws ec2 run-instances \\
  --image-id $AMI --instance-type t3.small \\
  --subnet-id $SUBNET --associate-public-ip-address \\
  --security-group-ids $SG_WHISPER \\
  --key-name puku-lab \\
  --private-ip-address 10.0.1.30 \\
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=whisper-ec2}]' \\
  --user-data "$WHISPER_USERDATA" \\
  --query 'Instances[0].InstanceId' --output text)

echo "whisper-ec2: $WHISPER_INSTANCE"
aws ec2 wait instance-running --instance-ids $WHISPER_INSTANCE
echo "export WHISPER_INSTANCE=$WHISPER_INSTANCE" >> ~/aws-creds.env
echo "Waiting 60s for user-data..."
sleep 60
curl http://10.0.1.30:8000/healthz
```

Expected : `{"ok": true, "model": "base", "host": "ec2"}` with HTTP 200. If you see "connection refused", wait another 30 seconds; user-data is still running.

Screenshot `screenshots/19-whisper-ec2-healthz.png` (the curl response above).

### 0.D.11 : Launch the client EC2 (Prometheus + Grafana)

```bash
CLIENT_USERDATA='#!/bin/bash
yum install -y docker
systemctl enable --now docker
mkdir -p /opt/prom
cat > /opt/prom/prometheus.yml <<YAMLEOF
global:
  scrape_interval: 5s
scrape_configs:
  - job_name: pc-node
    static_configs: [{ targets: ["10.99.0.2:9100"] }]
  - job_name: pc-whisper
    static_configs: [{ targets: ["10.99.0.2:8000"] }]
  - job_name: ec2-whisper-node
    static_configs: [{ targets: ["10.0.1.30:9100"] }]
  - job_name: ec2-whisper-app
    static_configs: [{ targets: ["10.0.1.30:8000"] }]
YAMLEOF

docker run -d --name prom --restart=always -p 9090:9090 \\
  -v /opt/prom:/etc/prometheus prom/prometheus:v2.54.0
docker run -d --name grafana --restart=always -p 3000:3000 grafana/grafana'

CLIENT_INSTANCE=$(aws ec2 run-instances \\
  --image-id $AMI --instance-type t3.small \\
  --subnet-id $SUBNET --associate-public-ip-address \\
  --security-group-ids $SG_CLIENT \\
  --key-name puku-lab \\
  --private-ip-address 10.0.1.31 \\
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=client-ec2}]' \\
  --user-data "$CLIENT_USERDATA" \\
  --query 'Instances[0].InstanceId' --output text)

aws ec2 wait instance-running --instance-ids $CLIENT_INSTANCE
CLIENT_PUBLIC_IP=$(aws ec2 describe-instances --instance-ids $CLIENT_INSTANCE \\
  --query 'Reservations[].Instances[].[PublicIpAddress]' --output text)
echo "client-ec2 public IP: $CLIENT_PUBLIC_IP"
echo "export CLIENT_PUBLIC_IP=$CLIENT_PUBLIC_IP" >> ~/aws-creds.env
echo "export CLIENT_INSTANCE=$CLIENT_INSTANCE" >> ~/aws-creds.env
sleep 60
curl -s http://10.0.1.31:9090/-/ready
```

Expected : "Prometheus Server is ready."

Open the browser to `http://<CLIENT_PUBLIC_IP>:9090/targets`. All four jobs should be `UP`.

Screenshot `screenshots/20-prometheus-targets.png` (browser at `:9090/targets` showing four jobs UP).

### 0.D.12 : IAM role for the failover Lambda

The Lambda needs to (a) write CloudWatch logs, (b) modify Route 53 records in the hosted zone, (d) read/write the DynamoDB state table.

```bash
cat > /tmp/trust.json <<'EOF'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Service": "lambda.amazonaws.com" },
    "Action": "sts:AssumeRole"
  }]
}
EOF
ROLE_ARN=$(aws iam create-role --role-name lambda-route53-failover \\
  --assume-role-policy-document file:///tmp/trust.json \\
  --query 'Role.Arn' --output text)
aws iam attach-role-policy --role-name lambda-route53-failover \\
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole

cat > /tmp/lambda-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    { "Effect": "Allow", "Action": "route53:ChangeResourceRecordSets",
      "Resource": "arn:aws:route53:::hostedzone/*" },
    { "Effect": "Allow", "Action": ["dynamodb:GetItem","dynamodb:PutItem"],
      "Resource": "arn:aws:dynamodb:$AWS_REGION:*:table/failover-state" }
  ]
}
EOF
aws iam put-role-policy --role-name lambda-route53-failover \\
  --policy-name failover-inline --policy-document file:///tmp/lambda-policy.json
echo "export ROLE_ARN=$ROLE_ARN" >> ~/aws-creds.env
```

Expected : an ARN like `arn:aws:iam::123456789012:role/lambda-route53-failover`.

### 0.D.13 : DynamoDB `failover-state` table

```bash
aws dynamodb create-table --table-name failover-state \\
  --attribute-definitions AttributeName=id,AttributeType=S \\
  --key-schema AttributeName=id,KeyType=HASH \\
  --billing-mode PAY_PER_REQUEST --region $AWS_REGION
aws dynamodb wait table-exists --table-name failover-state
aws dynamodb describe-table --table-name failover-state \\
  --query 'Table.[TableName,TableStatus,ItemCount]' --output text
```

Expected : `failover-state  ACTIVE  0`.

### 0.D.14 : Route 53 private hosted zone `hybrid.lab.`

The hosted zone is private, meaning it only answers DNS queries from inside the VPC that it is associated with. The first A record points at `10.99.0.2`, the PC's tunnel IP.

```bash
HZ_ID=$(aws route53 create-hosted-zone --name hybrid.lab. \\
  --vpc VPCRegion=$AWS_REGION,VPCId=$VPC \\
  --caller-reference $(date +%s) \\
  --query 'HostedZone.Id' --output text)
HZ_ID=${HZ_ID##*/}
echo "export HZ_ID=$HZ_ID" >> ~/aws-creds.env

cat > /tmp/a-record.json <<'EOF'
{
  "Changes": [{
    "Action": "UPSERT",
    "ResourceRecordSet": {
      "Name": "whisper.hybrid.lab.",
      "Type": "A",
      "TTL": 30,
      "ResourceRecords": [{ "Value": "10.99.0.2" }]
    }
  }]
}
EOF
aws route53 change-resource-record-sets --hosted-zone-id $HZ_ID \\
  --change-batch file:///tmp/a-record.json
```

Expected : a change ID, then `aws route53 get-change --id <change-id>` eventually returns `Status: INSYNC`.

Screenshot `screenshots/22-route53-hosted-zone.png` (Route 53 console showing `hybrid.lab.` and the `whisper.hybrid.lab.` A record).

### 0.D.15 : Failover Lambda code, deploy, attach to VPC

```bash
mkdir -p ~/lambda && cd ~/lambda
cat > route53_failover.py <<'EOF'
import os, urllib.request
import boto3
r53 = boto3.client("route53")
ddb = boto3.resource("dynamodb").Table(os.environ["STATE_TABLE"])

def probe(ip):
    try:
        with urllib.request.urlopen(f"http://{ip}:8000/healthz", timeout=2) as r:
            return r.status == 200
    except Exception:
        return False

def upsert(value):
    r53.change_resource_record_sets(
        HostedZoneId=os.environ["HZ_ID"],
        ChangeBatch={"Changes": [{"Action": "UPSERT",
            "ResourceRecordSet": {"Name": os.environ["RECORD_NAME"], "Type": "A", "TTL": 30,
                                  "ResourceRecords": [{"Value": value}]}}]})

def handler(event, context):
    primary_ok = probe(os.environ["PRIMARY_IP"])
    s = ddb.get_item(Key={"id": "failover"}).get("Item") or {"fails": 0, "active": os.environ["PRIMARY_IP"]}
    fails = int(s.get("fails", 0))
    active = s.get("active", os.environ["PRIMARY_IP"])
    if primary_ok:
        if active != os.environ["PRIMARY_IP"]:
            upsert(os.environ["PRIMARY_IP"])
            active = os.environ["PRIMARY_IP"]
        fails = 0
    else:
        fails += 1
        if fails >= int(os.environ["FAIL_THRESHOLD"]) and active != os.environ["STANDBY_IP"]:
            upsert(os.environ["STANDBY_IP"])
            active = os.environ["STANDBY_IP"]
    ddb.put_item(Item={"id": "failover", "fails": fails, "active": active})
    return {"primary_ok": primary_ok, "fails": fails, "active": active}
EOF

pip3 install --target ./package boto3 >/dev/null
(cd package && zip -r ../lambda.zip . >/dev/null)
zip -j lambda.zip route53_failover.py

LAMBDA_ARN=$(aws lambda create-function --function-name route53-failover \\
  --runtime python3.12 --role $ROLE_ARN --handler route53_failover.handler \\
  --zip-file fileb://lambda.zip --timeout 10 --memory-size 256 \\
  --vpc-config SubnetIds=$SUBNET,SecurityGroupIds=$SG_LAMBDA \\
  --environment "Variables={HZ_ID=$HZ_ID,RECORD_NAME=whisper.hybrid.lab.,PRIMARY_IP=10.99.0.2,STANDBY_IP=10.0.1.30,FAIL_THRESHOLD=3,STATE_TABLE=failover-state}" \\
  --query 'FunctionArn' --output text)
echo "export LAMBDA_ARN=$LAMBDA_ARN" >> ~/aws-creds.env
aws lambda update-function-configuration --function-name route53-failover \\
  --reserved-concurrent-executions 1

aws lambda invoke --function-name route53-failover --payload '{}' /tmp/lambda-out.json
cat /tmp/lambda-out.json
```

Expected : `{"primary_ok": true, "fails": 0, "active": "10.99.0.2"}`. If `primary_ok` is false, check `sg-lambda` egress to `10.99.0.2:8000` (it inherits the VPC's route table; the tunnel IP is reachable only because the WireGuard server's iptables MASQUERADE is in place).

### 0.D.16 : EventBridge rule `rate(1 minute)`

```bash
aws events put-rule --name route53-failover-tick \\
  --schedule-expression "rate(1 minute)" --state ENABLED
aws events put-targets --rule route53-failover-tick \\
  --targets "Id=1,Arn=$LAMBDA_ARN"

aws lambda add-permission --function-name route53-failover \\
  --statement-id AllowEvents --action lambda:InvokeFunction \\
  --principal events.amazonaws.com \\
  --source-arn arn:aws:events:$AWS_REGION:$(aws sts get-caller-identity --query Account --output text):rule/route53-failover-tick
```

Expected : the rule is enabled. Wait ~90 seconds, then check CloudWatch → Log groups → `/aws/lambda/route53-failover`; new log streams appear once per minute.

Screenshot `screenshots/23-lambda-schedule.png` (EventBridge console with the rule visible and state ENABLED).

### 0.D.17 : Grafana dashboard

Open Grafana at `http://<CLIENT_PUBLIC_IP>:3000`. Default credentials are `admin` / `admin`; change immediately when prompted.

Add a data source: Configuration (gear icon) → Data sources → Add data source → Prometheus. URL: `http://10.0.1.31:9090`. Save & test.

Create a dashboard with four panels:

1. **PC request rate** : `rate(http_requests_total_received{job="pc-whisper"}[1m])` (the Prometheus client default counter, until your app emits custom ones).
2. **EC2 request rate** : same with `job="ec2-whisper-app"`.
3. **DNS target (active endpoint)** : `up{job="pc-whisper"}` and `up{job="ec2-whisper-app"}` shown as stat panels (1 = active, 0 = down).
4. **PC and EC2 health** : `probe_success` once you wire up the blackbox exporter, or simply `up` on the four jobs.

Save the dashboard as `Lab 2 Base Failover`.

Screenshot `screenshots/21-grafana-failover-dashboard.png` (Grafana with all four panels visible).

### 0.D.18 : First failover drill

This is the milestone. You will kill the PC's Whisper, watch the DNS record flip to the standby, and watch it flip back when you restart.

```bash
# Baseline
ssh -i ~/keys/puku-lab.pem ec2-user@$EIP "dig +short whisper.hybrid.lab."
```

Expected : `10.99.0.2`.

Screenshot `screenshots/24-failover-drill-before.png` (the dig response).

```bash
# Kill PC Whisper
sudo systemctl stop whisper
curl -s http://10.99.0.2:8000/healthz
# Expected: connection refused
```

Wait about 200 seconds (3 EventBridge ticks, each 60 seconds apart, then FAIL_THRESHOLD=3 fires):

```bash
echo "Waiting 200 seconds for the Lambda to flip the record..."
sleep 200
ssh -i ~/keys/puku-lab.pem ec2-user@$EIP "dig +short whisper.hybrid.lab."
```

Expected : `10.0.1.30`.

Screenshot `screenshots/25-failover-drill-after.png` (the dig response, now `10.0.1.30`).

Open Grafana and check the dashboard. The "DNS target" panel should show EC2 as active, PC request rate dropping to 0, EC2 request rate climbing as new probes hit it.

Screenshot `screenshots/26-grafana-failover-event.png` (Grafana dashboard with the failover transition visible).

Restore:

```bash
sudo systemctl start whisper
sleep 90
ssh -i ~/keys/puku-lab.pem ec2-user@$EIP "dig +short whisper.hybrid.lab."
```

Expected : `10.99.0.2` again. If the failback does not happen, your Lambda is not actually probing `10.99.0.2` over the tunnel; double-check `sg-lambda` egress rules and the `wg-server` iptables MASQUERADE rule (the original step 0.D.6 verification covered the symmetric case).

## Phase 0.E : Re-verify the five checks

This is the spot check the extension's Step 1B re-runs before every later change.

```bash
# 1. WireGuard is up
wg show wg0 | grep -E "latest handshake|transfer"
ping -c 2 10.99.0.1

# 2. Whisper PC
curl http://10.99.0.2:8000/healthz

# 3. MinIO PC
curl http://10.99.0.2:9000/minio/health/live

# 4. Bucket + base.pt
~/mc ls local/whisper-models

# 5. Route 53 from inside the VPC
ssh -i ~/keys/puku-lab.pem ubuntu@10.0.1.31 "dig +short whisper.hybrid.lab."
```

Expected : every check passes. Capture the terminal output in `screenshots/27-five-checks-passing.png`.

## Phase 1 : The extension (TLS, second region, replication, paging, chaos drills)

You are now caught up to where the extension lab file expects you to be. Open `poridhi-lab2-hybrid-failover-extended.md` in another window and run **Steps 2-17** in order. Each step adds one production concern (TLS in transit, an `ap-southeast-2` regional standby, MinIO server-side replication, dual-channel SNS paging, the chaos drill matrix).

The extension's Step 2 generates the local PKI and re-enables Microservice as TLS (`screenshots/28-tls-pki-tree.png` shows the resulting `~/pki/` directory). Step 5 launches the second-region standby (`screenshots/29-second-region-launched.png`). Step 16 has you run the seven chaos drills; capture the output in `screenshots/30-chaos-drill-results.png`.

After Step 17, run the Verification section at the bottom of the extension file. Every box should tick.

## Screenshot inventory

| Slot | File | What to capture |
|---|---|---|
| 01 | `screenshots/01-wsl2-installed.png` | `wsl -l -v` output with Ubuntu-22.04 / VERSION 2 |
| 02 | `screenshots/02-apt-install-done.png` | terminal after the `apt install` block, no errors |
| 03 | `screenshots/03-docker-hello-world.png` | "Hello from Docker!" message |
| 04 | `screenshots/04-aws-sts-get-caller-identity.png` | the JSON `get-caller-identity` response |
| 05 | `screenshots/05-aws-region-selector.png` | AWS console top-right showing ap-southeast-1 |
| 06 | `screenshots/06-iam-user-created.png` | IAM Users console with `lab2-admin` and one access key |
| 07 | `screenshots/07-vpc-created.png` | VPC console with `lab2-vpc` selected |
| 08 | `screenshots/08-subnet-route-table.png` | route table showing `0.0.0.0/0 → lab2-igw` |
| 09 | `screenshots/09-eip-allocated.png` | Elastic IPs console with `eip-wg` |
| 10 | `screenshots/10-wg-server-launched.png` | EC2 console with `wg-server` running |
| 11 | `screenshots/11-wg-keys-generated.png` | terminal showing the four key files |
| 12 | `screenshots/12-wg0-conf-server.png` | `cat /etc/wireguard/wg0.conf` on the server |
| 13 | `screenshots/13-wg0-conf-pc.png` | `cat /etc/wireguard/wg0.conf` on the PC |
| 14 | `screenshots/14-wg-handshake.png` | `wg show wg0` with fresh handshake and transfer counters |
| 15 | `screenshots/15-ping-both-ways.png` | two terminals, both pings succeeding |
| 16 | `screenshots/16-minio-console.png` | browser at `http://10.99.0.2:9001` with `whisper-models` bucket |
| 17 | `screenshots/17-basept-uploaded.png` | `mc ls local/whisper-models` showing `base.pt` |
| 18 | `screenshots/18-whisper-pc-healthz.png` | `curl http://10.99.0.2:8000/healthz` returning `{"host": "pc"}` |
| 19 | `screenshots/19-whisper-ec2-healthz.png` | same against `10.0.1.30`, returning `{"host": "ec2"}` |
| 20 | `screenshots/20-prometheus-targets.png` | `:9090/targets` with all four jobs UP |
| 21 | `screenshots/21-grafana-failover-dashboard.png` | Grafana dashboard with the four panels |
| 22 | `screenshots/22-route53-hosted-zone.png` | Route 53 console with `hybrid.lab.` and the A record |
| 23 | `screenshots/23-lambda-schedule.png` | EventBridge rule in ENABLED state |
| 24 | `screenshots/24-failover-drill-before.png` | `dig` returning `10.99.0.2` before the drill |
| 25 | `screenshots/25-failover-drill-after.png` | `dig` returning `10.0.1.30` after killing PC Whisper |
| 26 | `screenshots/26-grafana-failover-event.png` | Grafana showing the failover transition |
| 27 | `screenshots/27-five-checks-passing.png` | the terminal output of all five checks in Phase 0.E |
| 28 | `screenshots/28-tls-pki-tree.png` | `find ~/pki -type f` after extension Step 2 |
| 29 | `screenshots/29-second-region-launched.png` | Sydney VPC + EC2 in the AWS console (extension Step 5) |
| 30 | `screenshots/30-chaos-drill-results.png` | the seven-row chaos drill matrix executed (extension Step 16) |

## What to do when something goes wrong

The `screenshots/` folder is empty by design. The walkthrough does not run anything for you; you do. If a command in the walkthrough returns an error, do not move on. The most common causes and fixes:

- **`AccessDenied` from any AWS CLI command** : your access key is missing a permission. Re-check that `lab2-admin` has `AdministratorAccess` attached (Phase 0.B).
- **WireGuard handshake never appears** : the Elastic IP is not associated with the right instance, or UDP 51820 is blocked by your home router. From the PC, `nc -zuv $EIP 51820` should report "succeeded".
- **`ping` works PC→server but not server→PC** : the iptables MASQUERADE rule is missing on the server (0.D.6).
- **MinIO "access denied" on `mc ls`** : the credentials in `~/minio/.env` do not match the ones you passed to `docker run`. Re-source the env file and restart the container.
- **Lambda returns `primary_ok: false` even though Whisper is up** : `sg-lambda` does not allow egress to `10.99.0.2:8000` over the tunnel; the route from the Lambda's subnet to `10.99.0.2` goes via the `wg-server` instance, which only NATs if iptables MASQUERADE is in place.
- **`dig` returns NXDOMAIN from `client-ec2`** : the Route 53 private hosted zone is not associated with the primary VPC. Re-check with `aws route53 list-hosted-zones-by-vpc --vpc-id $VPC --vpc-region $AWS_REGION`.

When a check fails, fix it before screenshotting. The whole point of the screenshot slots is to be evidence that the lab works end-to-end, so a screenshot of a broken state is worse than no screenshot.
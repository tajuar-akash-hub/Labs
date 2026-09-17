# Lab 1: VPC-Isolated ML Inference Endpoint

## Introduction

In production-grade ML systems, exposing a model publicly on the internet is a serious security risk. A Vision Transformer (ViT) or any other ML model placed in a public subnet can be discovered, probed, and abused — either for unauthorized inference (cost abuse) or for model exfiltration. This lab teaches you how to deploy an ML inference endpoint that lives entirely inside a private network, accessible **only** to authorized internal services through AWS Transit Gateway.

In this lab, you will build a two-VPC architecture: a **Model VPC** that hosts the FastAPI + ViT inference server inside a private subnet (no public IP), and a **Client VPC** that hosts an internal test client. The two VPCs are connected via an AWS Transit Gateway (TGW) using internal, private routing — completely isolated from the public internet. Model weights are stored in S3 and downloaded by the EC2 instance on launch.

By the end of this lab, you will have a fully functional, production-ready ML inference endpoint that authorized internal services can call — but the public internet cannot reach.

---

## Architecture

### Architecture Structure

```text
AWS Cloud
├── Amazon S3 (Model Weights — e.g. HuggingFace ViT model)
│       |
│       v  (download model weights)
├── VPC 1 — Model VPC (10.0.0.0/16)
│   ├── Private Subnet
│   │   └── EC2 (Model Server) — FastAPI + ViT Model
│   └── Route Table (Model VPC)
│       ├── 10.0.0.0/16    → local
│       ├── 10.1.0.0/16    → tgw-rtb  (route to Client VPC via TGW)
│       └── 0.0.0.0/0      → (no route)  ← no internet
│
├── AWS Transit Gateway (TGW)  ← internal bridge
│       |
│       v  (Internal Traffic: VPC to VPC via TGW)
├── VPC 2 — Client VPC (10.1.0.0/16)
│   ├── Private Subnet
│   │   └── Client App / Tester (Internal Service) — sends image, gets inference result
│   └── Route Table (Client VPC)
│       ├── 10.1.0.0/16    → local
│       ├── 10.0.0.0/16    → tgw-rtb  (route to Model VPC via TGW)
│       └── 0.0.0.0/0      → (no route)  ← no internet
│
└── Public Internet  ← ❌ Not Accessible (No public IP, no IGW)
```

### Architecture Explanation

**Model VPC (VPC 1):** Contains a private subnet with an EC2 instance running FastAPI and a HuggingFace ViT model for image classification. This instance has **no public IP** and no route to the internet. Model weights are downloaded from S3 on startup.

**Client VPC (VPC 2):** Contains a private subnet with a Client App / Tester that sends image files to the inference server and receives predictions. This client is also private — it has no public IP.

**AWS Transit Gateway (TGW):** Acts as the central private bridge connecting the two VPCs. Traffic between the model and client flows VPC-to-VPC through the TGW using internal AWS networking. Neither VPC has an Internet Gateway, so the public internet cannot reach either endpoint.

**Key design points:**
- Model weights in S3 (HuggingFace ViT model).
- Model server in private subnet (no public IP).
- Two VPCs connected via Transit Gateway.
- Client VPC accesses model internally via TGW.
- No direct internet access to the model endpoint.

---

## Learning Objectives

By the end of this lab, you will be able to:

- Design a **multi-VPC architecture** using AWS Transit Gateway for private service-to-service communication.
- Deploy a **Vision Transformer (ViT) inference server** using FastAPI inside a private subnet.
- Configure **route tables** to direct inter-VPC traffic through TGW only.
- Use **S3 + IAM** to securely deliver model weights to a private EC2 instance.
- Validate that the model endpoint is **completely inaccessible from the public internet**.
- Build a **secure, production-ready ML inference architecture**.

---

## Prerequisites

Before starting this lab, ensure you have:

- An **active AWS account** with free tier or paid access.
- **Basic understanding** of VPCs, subnets, route tables, and EC2.
- Familiarity with **Linux/SSH** and **Python**.
- **AWS region selection:** `us-east-1` (N. Virginia) recommended.
- IAM permissions to create VPCs, subnets, route tables, EC2 instances, IAM roles, and Transit Gateways.

---

## Prologue

You will build a VPC-isolated ML inference endpoint — a Vision Transformer model served via FastAPI inside a private subnet, reachable only by an authorized client in a separate VPC via AWS Transit Gateway. The public internet is completely locked out.

This is the production-grade pattern for serving internal ML models inside large organizations where models must be protected from unauthorized access but still be callable by trusted services.

---

## Step-by-Step Implementation

### Step 1: Create Two VPCs

Create two VPCs using the VPC Dashboard:

**VPC 1 — Model VPC**
```text
Name tag: Model-VPC
IPv4 CIDR block: 10.0.0.0/16
Tenancy: Default
```

**VPC 2 — Client VPC**
```text
Name tag: Client-VPC
IPv4 CIDR block: 10.1.0.0/16
Tenancy: Default
```

### Step 2: Create Private Subnets in Each VPC

**Model Private Subnet:**
```text
VPC ID: Model-VPC
Subnet name: Model-Private-Subnet
Availability Zone: us-east-1a
IPv4 CIDR block: 10.0.1.0/24
Auto-assign public IPv4: Disabled
```

**Client Private Subnet:**
```text
VPC ID: Client-VPC
Subnet name: Client-Private-Subnet
Availability Zone: us-east-1a
IPv4 CIDR block: 10.1.1.0/24
Auto-assign public IPv4: Disabled
```

### Step 3: Create the Transit Gateway (TGW)

VPC Dashboard → Transit Gateways → Create Transit Gateway:

```text
Name tag: ML-Inference-TGW
Description: TGW for ML inference
Amazon side ASN: 64512
Auto accept shared attachments: Enable
Default route table association: Enable
Default route table propagation: Enable
DNS support: Enable
```

Wait until the TGW state becomes `available` before continuing.

### Step 4: Attach Both VPCs to the Transit Gateway

Transit Gateways → Transit Gateway Attachments → Create attachment:

**Attachment 1 (Model VPC):**
```text
Attachment type: VPC
Transit Gateway: ML-Inference-TGW
VPC ID: Model-VPC
Subnet IDs: Model-Private-Subnet
```

**Attachment 2 (Client VPC):**
```text
Attachment type: VPC
Transit Gateway: ML-Inference-TGW
VPC ID: Client-VPC
Subnet IDs: Client-Private-Subnet
```

Wait until both attachments show `available`.

### Step 5: Configure Route Tables

**Model VPC Route Table:**
```text
Destination     Target
10.0.0.0/16     local
10.1.0.0/16     tgw-ML-Inference-TGW
0.0.0.0/0       (no route)   ← IMPORTANT: no internet
```

**Client VPC Route Table:**
```text
Destination     Target
10.1.0.0/16     local
10.0.0.0/16     tgw-ML-Inference-TGW
0.0.0.0/0       (no route)   ← IMPORTANT: no internet
```

### Step 6: Create Security Groups

**Model-SG (attached to Model EC2):**

| Type | Protocol | Port Range | Source | Description |
|------|----------|------------|--------|-------------|
| Custom TCP | TCP | 8000 | 10.1.0.0/16 | FastAPI from Client VPC |
| SSH | TCP | 22 | 10.1.0.0/16 | SSH from Client VPC |

VPC: Model-VPC

**Client-SG (attached to Client EC2):**

| Type | Protocol | Port Range | Source | Description |
|------|----------|------------|--------|-------------|
| SSH | TCP | 22 | My IP | SSH from your local machine |

VPC: Client-VPC

### Step 7: Create S3 Bucket for Model Weights

S3 → Create bucket:

```text
Bucket name: ml-model-weights-<unique-name>
Region: us-east-1
Block all public access: ON (very important)
```

Upload your pre-downloaded HuggingFace ViT model to the bucket under a folder (e.g. `s3://ml-model-weights-<unique>/vit-model/`).

To download the model locally first:

```bash
pip install transformers torch
python -c "
from transformers import ViTForImageClassification
ViTForImageClassification.from_pretrained('google/vit-base-patch16-224').save_pretrained('./vit-model')
"
aws s3 cp ./vit-model s3://ml-model-weights-<unique>/vit-model/ --recursive
```

### Step 8: Create IAM Role for EC2 → S3 Access

IAM → Roles → Create role:

```text
Trusted entity type: AWS service
Use case: EC2
Permissions policy: AmazonS3ReadOnlyAccess
Role name: EC2-S3-Read-Role
```

### Step 9: Launch the Model EC2 (in Model Private Subnet)

EC2 → Launch instance:

```text
Name: ML-Model-Server
AMI: Ubuntu Server 22.04 LTS
Instance type: t3.medium  (or g4dn.xlarge for GPU)
Key pair: create/select existing
Network:
  VPC: Model-VPC
  Subnet: Model-Private-Subnet
  Auto-assign Public IP: Disabled
  Security group: Model-SG
  IAM instance profile: EC2-S3-Read-Role
```

**User data (advanced details):**

```bash
#!/bin/bash
apt update -y
apt install python3-pip -y
pip3 install fastapi uvicorn transformers torch boto3 pillow

mkdir -p /home/ubuntu/model
aws s3 cp s3://ml-model-weights-<unique>/vit-model/ /home/ubuntu/model/ --recursive

cat > /home/ubuntu/app.py << 'EOF'
from fastapi import FastAPI, File, UploadFile
from transformers import ViTImageProcessor, ViTForImageClassifier
from PIL import Image
import io

app = FastAPI()
processor = ViTImageProcessor.from_pretrained("./model")
model = ViTForImageClassifier.from_pretrained("./model")

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    image = Image.open(io.BytesIO(await file.read())).convert("RGB")
    inputs = processor(images=image, return_tensors="pt")
    outputs = model(**inputs)
    predicted_class = outputs.logits.argmax(-1).item()
    label = model.config.id2label[predicted_class]
    return {"class_id": predicted_class, "label": label}
EOF

cd /home/ubuntu
nohup uvicorn app:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &
```

### Step 10: Launch the Client EC2 (in Client Private Subnet)

EC2 → Launch instance:

```text
Name: Client-App-Tester
AMI: Ubuntu Server 22.04
Instance type: t3.micro
Network:
  VPC: Client-VPC
  Subnet: Client-Private-Subnet
  Auto-assign Public IP: Disabled
  Security group: Client-SG
  IAM instance profile: EC2-S3-Read-Role   (for SSM session manager later)
```

### Step 11: Connect to Private EC2s Using Session Manager

Since both EC2s are in private subnets, SSH directly is not possible. Use AWS Systems Manager Session Manager:

**Step 11.1:** Create an additional IAM role `EC2-SSM-Role` with `AmazonSSMManagedInstanceCore` policy and attach to **both** EC2s.

**Step 11.2:** From the EC2 console, select each instance → Connect → Session Manager → Connect.

### Step 12: Get the Model EC2 Private IP

From the EC2 console → Instances → ML-Model-Server → Details tab → note the **Private IPv4 address** (e.g. `10.0.1.50`).

### Step 13: Test Connectivity from the Client

From the **Client EC2 Session Manager terminal**:

```bash
ping 10.0.1.50
```

Expected: successful pings.

### Step 14: Test the Inference Endpoint

From the **Client EC2**:

```bash
# Upload any test image (here we download a sample cat image)
curl -o /tmp/test.jpg https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/Cat_November_2010-1a.jpg/1200px-Cat_November_2010-1a.jpg

# Send to the model
curl -X POST http://10.0.1.50:8000/predict -F "file=@/tmp/test.jpg"
```

Expected response:

```json
{"class_id":281,"label":"tabby, tabby cat"}
```

### Step 15: Verify Public Internet is Blocked

From the **Model EC2 Session Manager terminal**:

```bash
curl http://google.com      # Should FAIL: Could not resolve host
ping 8.8.8.8                # Should FAIL: Network unreachable
```

Expected: both commands fail, confirming the model endpoint has no internet access.

---

## Verification

After completing the implementation, verify each piece:

- [ ] `Model-VPC` (10.0.0.0/16) and `Client-VPC` (10.1.0.0/16) exist.
- [ ] `Model-Private-Subnet` and `Client-Private-Subnet` exist with public IP auto-assignment disabled.
- [ ] `ML-Inference-TGW` is in `available` state.
- [ ] Both VPCs are attached to the TGW and attachments are `available`.
- [ ] Route tables route `10.1.0.0/16` and `10.0.0.0/16` to the TGW (no `0.0.0.0/0` route).
- [ ] `ML-Model-Server` is running in Model-Private-Subnet with **no public IP**.
- [ ] `Client-App-Tester` is running in Client-Private-Subnet with **no public IP**.
- [ ] `Model-SG` only allows port 8000 from `10.1.0.0/16` (Client VPC CIDR).
- [ ] S3 bucket has **block all public access** enabled.
- [ ] Model EC2 can `ping` Client EC2 and vice versa via TGW.
- [ ] `curl http://<model-private-ip>:8000/predict` from the Client EC2 returns a valid classification.
- [ ] Model EC2 cannot reach `google.com` or `8.8.8.8`.

---

## Testing

### Test 1: Inter-VPC Connectivity via TGW

From Client EC2:

```bash
ping 10.0.1.50   # Model private IP
```

Expected: successful pings.

### Test 2: Image Inference

From Client EC2:

```bash
curl -X POST http://10.0.1.50:8000/predict -F "file=@/tmp/test.jpg"
```

Expected: `{"class_id":281,"label":"tabby, tabby cat"}` (or another ImageNet label depending on the test image).

### Test 3: Internet Isolation

From Model EC2:

```bash
curl http://google.com   # Should FAIL
ping 8.8.8.8            # Should FAIL
```

Expected: both fail — model is completely isolated from the internet.

### Test 4: Security Group Behavior

From a machine **outside** the Client VPC (or from the Client EC2 trying to reach an unauthorized port):

```bash
curl http://10.0.1.50:22    # Should FAIL — port 22 only open from 10.1.0.0/16 in Model-SG
```

Expected: connection refused / timeout, proving least-privilege network access.

---

## Troubleshooting

| Problem | Likely Cause | Fix |
|---------|--------------|-----|
| TGW attachment stuck in `pending` | TGW still provisioning | Wait 2–3 minutes for TGW to reach `available` state |
| `ping` to model IP fails from client | Route table missing entry to other VPC | Add route `10.0.0.0/16 → tgw-XXX` in Client VPC route table |
| `curl http://10.0.1.50:8000/predict` times out | Security group missing port 8000 | Add rule: Custom TCP, port 8000, source `10.1.0.0/16` |
| `curl http://10.0.1.50:8000/predict` connection refused | uvicorn not running on model EC2 | SSH via SSM, check `ps aux | grep uvicorn`, restart if needed |
| `Connection refused` to S3 from model EC2 | IAM role not attached or wrong policy | Confirm `EC2-S3-Read-Role` is attached; policy has `s3:GetObject` |
| Session Manager "Instance not in list" | SSM agent not running or IAM role missing | Attach `AmazonSSMManagedInstanceCore` to the EC2, restart SSM agent |
| `curl https://google.com` succeeds on model EC2 | Internet Gateway accidentally attached | Confirm there is no IGW attached to Model-VPC; remove if present |
| Model returns 500 / wrong predictions | Model not fully downloaded | Check `ls -la /home/ubuntu/model/` shows config + weights files; re-run `aws s3 cp` |

---

## Cleanup

To avoid unnecessary charges, delete resources in this exact order:

1. **Terminate EC2 instances** (`ML-Model-Server`, `Client-App-Tester`).
2. **Delete Transit Gateway attachments** (Model VPC, Client VPC).
3. **Delete Transit Gateway.**
4. **Delete S3 bucket** (objects first, then bucket).
5. **Delete VPCs** (`Model-VPC`, `Client-VPC`) — subnets, route tables, and SGs are removed automatically or manually as needed.
6. **Delete IAM role** `EC2-S3-Read-Role` (optional).

```bash
# AWS CLI teardown example
aws ec2 terminate-instances --instance-ids i-MODEL_ID i-CLIENT_ID
aws ec2 delete-transit-gateway-vpc-attachment --transit-gateway-attachment-id tgw-attach-MODEL
aws ec2 delete-transit-gateway-vpc-attachment --transit-gateway-attachment-id tgw-attach-CLIENT
aws ec2 delete-transit-gateway --transit-gateway-id tgw-XXXXX
aws s3 rm s3://ml-model-weights-<unique> --recursive
aws s3 rb s3://ml-model-weights-<unique>
aws ec2 delete-vpc --vpc-id vpc-MODEL_ID
aws ec2 delete-vpc --vpc-id vpc-CLIENT_ID
```

---

## Epilogue

You have successfully deployed a **fully VPC-isolated ML inference endpoint** using a Vision Transformer model. The model endpoint is reachable only by the authorized Client VPC through AWS Transit Gateway, and is completely inaccessible from the public internet. Model weights were securely delivered through S3 + IAM, and the EC2 instance never needed a public IP.

This is the canonical pattern for serving internal ML models securely inside an organization, where the model is a valuable asset that must be protected from external abuse.

---

## Principles

This lab demonstrates several core security and architecture principles:

- **Defense in depth** — multiple isolation layers (subnet, route table, SG, no IGW).
- **Least privilege networking** — SG only allows traffic from the Client VPC CIDR.
- **Zero public exposure** — model has no public IP and no IGW route.
- **Private service-to-service communication** — TGW provides internal-only routing.
- **Separation of model and clients** — different VPCs isolate blast radius.
- **IAM-based access** — S3 access via role, not access keys.
- **Cost awareness** — explicit cleanup order avoids orphan resources.

---

## What You Learned

- Designing a multi-VPC, isolated ML inference architecture.
- Configuring AWS Transit Gateway as a private VPC-to-VPC bridge.
- Deploying a HuggingFace ViT model with FastAPI on a private EC2.
- Downloading model weights securely via S3 + IAM.
- Configuring route tables and security groups for least-privilege traffic.
- Verifying that the model endpoint is fully isolated from the public internet.
- Cleaning up AWS resources to avoid unexpected billing.

---

## Next Steps

- Add **authentication** (API keys, mTLS, or IAM SigV4) to the inference API.
- Add **CloudWatch monitoring** and **alarms** for inference latency.
- Replace EC2 with **ECS Fargate** or **EKS** for horizontal scaling.
- Add an **Application Load Balancer** inside the Model VPC for multi-instance inference.
- Add **model versioning** with S3 prefixes and dynamic model selection.
- Extend with a **third VPC** (e.g. analytics VPC) connected via the same TGW.

---

## Additional Resources

- [AWS Transit Gateway Documentation](https://docs.aws.amazon.com/vpc/latest/tgw/what-is-transit-gateway.html)
- [VPC Route Tables](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Route_Tables.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/index)
- [AWS Systems Manager Session Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html)
- [AWS S3 Block Public Access](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-best-practices.html)
- [Poridhi Labs](https://www.poridhi.io/)

---
---

# Lab 2: Secure AI/ML Inference with Multi-VPC Architecture Using Transit Gateway

## Introduction

In modern enterprise environments, AI/ML workloads often need to operate across both on-premises data centers and cloud infrastructure. Maintaining security, low latency, and scalability while bridging these two worlds is a real engineering challenge. This Poridhi Labs tutorial walks you through building a production-style hybrid AI inference pipeline.

In this lab, you will design a multi-VPC architecture where a FastAPI-based inference server runs privately inside AWS (no public IP), and a simulated on-premises environment sends text data to it over an encrypted BGP-enabled VPN tunnel. The model used is a pre-trained transformer from Hugging Face, served via FastAPI inside a private subnet. Communication flows through an AWS Transit Gateway (TGW), which acts as the central hub connecting the on-premises simulated VPC and the private inference VPC.

By the end of this lab, you will have built a complete end-to-end encrypted AI inference pipeline — from on-premises client, through a VPN tunnel and Transit Gateway, to a private VPC hosting the FastAPI inference server — and back again with results displayed on an on-premises dashboard.

---

## Architecture

### Architecture Structure

```text
On-Prem (Simulated via EC2)
  |
  +-- Text Data
        |
        v
  [Encrypted BGP Tunnel]
        |
        v
  [Transit Gateway] <-----> [Private VPC]
                                   |
                                   +-- [Private Subnet]
                                          |
                                          +-- [FastAPI Inference Server]
                                                 |
                                                 +-- [HuggingFace Transformer Model]
        |
        v
  [Response to Dashboard]
```

### Architecture Explanation

**On-Premises Environment (Simulated via EC2):**
The on-premises client is simulated using an EC2 instance (`OnPrem-Client`) running a FastAPI-based dashboard. This client sends text data to the cloud-based inference server over an encrypted VPN tunnel. The instance runs strongSwan (for IPsec) and FRRouting (for BGP, ASN 65000) to establish the encrypted tunnel and exchange routes dynamically.

**AWS Cloud Infrastructure:**
- **Private VPC (10.0.0.0/16)** — `ML-Inference-VPC` is a logically isolated network hosting the inference server with no public IP. This ensures that the AI inference workload is protected from direct internet exposure.
- **Transit Gateway (TGW)** — `Secure-TGW` (Amazon ASN 64512) acts as a central hub connecting the on-premises environment and the AWS VPC. It enables private, encrypted communication between them via the VPN attachment.
- **FastAPI Inference Server** — Runs inside the private subnet, processes incoming text using a HuggingFace transformer model, and returns predictions through a secure API endpoint on port 8000.
- **VPN Connection with BGP** — Establishes a secure, dynamic routing connection between the on-premises environment and the AWS Transit Gateway using Border Gateway Protocol (BGP).

**Communication Flow:**
1. OnPrem-Client sends text data over the encrypted IPsec VPN tunnel (data flows through TGW into the private VPC).
2. Transit Gateway routes the traffic to the Inference-Server EC2 inside the private VPC.
3. FastAPI inference server processes the text using the HuggingFace transformer model.
4. The response is sent back through the same encrypted tunnel to the OnPrem-Client dashboard.

---

## Learning Objectives

By the end of this lab, you will be able to:

- Design a **multi-VPC architecture** for AI/ML workloads.
- Configure **AWS Transit Gateway (TGW)** to enable secure inter-VPC communication.
- Deploy a **FastAPI-based AI inference server** in a private VPC with no public IP.
- Set up a **VPN-based encrypted tunnel** between an on-premises simulated environment and AWS.
- Implement **BGP routing** to dynamically exchange routes between on-premises and AWS.
- Send data from an on-premises client to a cloud-hosted inference server over an encrypted channel.
- Display inference results on an **on-premises dashboard**.

---

## Prerequisites

Before starting this lab, ensure you have:

- An **active AWS account** with free tier or paid access.
- **Basic understanding of networking concepts** (VPC, subnets, routing, IPsec, BGP).
- **Familiarity with Linux commands and SSH**.
- **AWS region selection:** `us-east-1` (N. Virginia) recommended.
- A **HuggingFace transformer model** (or use the pre-uploaded `poridhilabs/models/text_classification_model.zip`).
- IAM permissions to create VPCs, EC2 instances, Transit Gateways, VPN connections, and Customer Gateways.

---

## Prologue

You will build a complete hybrid AI inference pipeline where:
1. An on-premises simulated environment (using an EC2 instance) sends text data to a private VPC in AWS.
2. A FastAPI inference server processes the text using a pre-trained transformer model.
3. The result is sent back through the encrypted VPN tunnel to the on-premises dashboard.

This mirrors a real-world enterprise scenario where sensitive ML inference must happen in a private cloud while clients remain on on-prem infrastructure — all with end-to-end encryption.

---

## Step-by-Step Implementation

### Step 1: Create the Private VPC

Create a VPC named `ML-Inference-VPC` with CIDR `10.0.0.0/16`.

**Console path:** VPC Dashboard → Your VPCs → Create VPC

```text
Name tag: ML-Inference-VPC
IPv4 CIDR block: 10.0.0.0/16
Tenancy: Default
```

### Step 2: Create a Private Subnet

Create a private subnet named `Private-Subnet-1` with CIDR `10.0.1.0/24` in `us-east-1a`.

**Disable auto-assign public IP:**
- Go to the subnet settings.
- Turn off **"Auto-assign public IPv4 address."**

**Why a private subnet?**
A private subnet has no direct internet access, which is ideal for hosting an inference server that should not be exposed to the public internet.

```text
VPC ID: ML-Inference-VPC
Subnet name: Private-Subnet-1
Availability Zone: us-east-1a
IPv4 CIDR block: 10.0.1.0/24
Auto-assign public IPv4: Disabled
```

### Step 3: Launch EC2 for Inference Server (Private)

Launch an EC2 instance in the private subnet:

```text
Name: Inference-Server
AMI: Ubuntu Server 22.04 LTS (Free tier eligible)
Instance Type: t2.micro (Free tier eligible)
Key Pair: Create or select an existing key pair
Subnet: Private-Subnet-1
Auto-assign Public IP: Disabled
IAM Role: Attach a role with AmazonS3ReadOnlyAccess and AmazonEC2ReadOnlyAccess
```

### Step 4: Configure Security Group for Inference Server

Create a security group named `Inference-SG` with the following inbound rules:

| Type | Protocol | Port Range | Source Type | Source |
|------|----------|------------|-------------|--------|
| SSH | TCP | 22 | Custom | On-Prem-CIDR (10.100.0.0/16) |
| Custom TCP | TCP | 8000 | Custom | On-Prem-CIDR (10.100.0.0/16) |
| All ICMP - IPv4 | ICMP | All | Custom | On-Prem-CIDR (10.100.0.0/16) |

### Step 5: Create a Customer Gateway

```text
Name: on-prem-cgw
IP Address: <ON_PREM_PUBLIC_IP>   # Replace with actual public IP of OnPrem-Client EC2
BGP ASN: 65000
```

### Step 6: Create a Transit Gateway

```text
Name: Secure-TGW
Description: Transit Gateway for Secure Inference
Amazon side ASN: 64512
Auto accept shared attachments: Enable
Default route table association: Enable
Default route table propagation: Enable
```

Wait until the TGW state becomes `available` before proceeding.

### Step 7: Create a VPN Attachment

Create a VPN attachment to the Transit Gateway:

```text
Name: on-prem-vpn-attachment
Transit Gateway ID: Secure-TGW
Customer Gateway ID: on-prem-cgw
Routing Options: Dynamic (BGP)
```

> **Note:** This process may take 5–10 minutes.

After creation, download the **configuration file** from the VPN connection. You will need:
- Tunnel 1 inside IP CIDR
- Tunnel 1 outside IP
- Pre-Shared Key (PSK)

### Step 7.5: Configure TGW Route Table

After the VPN attachment is created, edit the default TGW route table:

- Add a **propagation** for the VPN attachment (so routes from on-premises are propagated into the TGW).
- Add a **static route** for the on-premises CIDR `10.100.0.0/16` pointing to the VPN attachment.

### Step 8: Launch On-Premises Simulated EC2 (Public Subnet)

> **Important:** This EC2 simulates the on-premises environment and must be in a PUBLIC subnet.

Create a new VPC for on-premises simulation:

```text
VPC Name: OnPrem-VPC
CIDR: 10.100.0.0/16
Public Subnet Name: OnPrem-Public-Subnet
CIDR: 10.100.0.0/24
Availability Zone: us-east-1a
```

**Create an Internet Gateway:**
- Name: `OnPrem-IGW`
- Attach it to the `OnPrem-VPC`.

**Update Route Table:**
- Add route: Destination `0.0.0.0/0` → Target `OnPrem-IGW`.

**Launch EC2:**
```text
Name: OnPrem-Client
AMI: Ubuntu Server 22.04 LTS
Instance Type: t2.micro
Subnet: OnPrem-Public-Subnet
Auto-assign Public IP: Enabled
IAM Role: Attach a role with AmazonEC2ReadOnlyAccess
```

### Step 9: Configure Security Group for OnPrem Client

Create a security group named `OnPrem-SG` with the following inbound rules:

| Type | Protocol | Port Range | Source Type | Source |
|------|----------|------------|-------------|--------|
| SSH | TCP | 22 | My IP | Your local IP |
| Custom TCP | TCP | 8000 | My IP | Your local IP |
| All ICMP - IPv4 | ICMP | All | My IP | Your local IP |
| UDP | UDP | 500 | Custom | 10.0.0.0/16 |
| UDP | UDP | 4500 | Custom | 10.0.0.0/16 |

### Step 10: Configure VPN on OnPrem-Client EC2

SSH into the OnPrem-Client EC2 and run:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install strongswan -y
```

### Step 11: Configure IPsec VPN (strongSwan)

Edit the IPsec configuration:

```bash
sudo nano /etc/ipsec.conf
```

Add the following configuration:

```bash
config setup
    charondebug="all"
    uniqueids=no

conn aws-vpn
    type=tunnel
    leftid=<ON_PREM_PUBLIC_IP>
    left=<ON_PREM_PUBLIC_IP>
    leftsubnet=10.100.0.0/16
    right=<TUNNEL1_INSIDE_CIDR>      # Example: 169.254.10.2/30
    rightsubnet=10.0.0.0/16
    ike=aes256-sha1-modp1024!
    ikelifetime=28800s
    esp=aes256-sha1!
    lifetime=3600s
    keyexchange=ikev1
    authby=secret
    keyingtries=%forever
    auto=start
```

Set the Pre-Shared Key (PSK):

```bash
sudo nano /etc/ipsec.secrets
```

Add:

```bash
<ON_PREM_PUBLIC_IP> <TUNNEL1_OUTSIDE_IP> : PSK "<PRE_SHARED_KEY>"
```

Restart IPsec:

```bash
sudo ipsec restart
sudo ipsec status
```

### Step 12: Configure BGP (FRRouting)

Install and configure FRR for BGP:

```bash
sudo apt install frr -y
sudo nano /etc/frr/daemons
```

Set `bgpd=yes`.

Configure BGP:

```bash
sudo nano /etc/frr/bgpd.conf
```

```bash
router bgp 65000
 bgp router-id <ON_PREM_PUBLIC_IP>
 neighbor <TUNNEL1_INSIDE_CIDR> remote-as 64512
 neighbor <TUNNEL1_INSIDE_CIDR> timers 10 30
 !
 address-family ipv4
  network 10.100.0.0/16
 exit-address-family
```

Restart FRR:

```bash
sudo service frr restart
```

### Step 13: Configure Routes on OnPrem-Client

Add route for VPC CIDR through the VPN tunnel:

```bash
sudo ip route add 10.0.0.0/16 via <TUNNEL1_INSIDE_CIDR> dev eth0
```

For persistence:

```bash
sudo nano /etc/rc.local
# Add: ip route add 10.0.0.0/16 via <TUNNEL1_INSIDE_CIDR> dev eth0
sudo chmod +x /etc/rc.local
```

### Step 14: Configure VPC Route Table

Go to the VPC dashboard and update the route table of `ML-Inference-VPC` to route traffic destined for `10.100.0.0/16` to the Transit Gateway.

### Step 15: Download Model and Set Up Inference Server

SSH into the **Inference-Server EC2** using a **bastion host** (since it has no public IP) or via **AWS Systems Manager Session Manager** and run:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip -y
sudo apt install unzip -y
```

Download the Hugging Face model from S3:

```bash
aws s3 cp s3://poridhilabs/models/text_classification_model.zip ~/
unzip ~/text_classification_model.zip -d ~/model/
cd ~/
pip3 install --no-cache-dir torch transformers fastapi uvicorn
```

Create the FastAPI app `app.py`:

```python
from fastapi import FastAPI, Request
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

app = FastAPI()

model_path = "/home/ubuntu/model"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path)
model.eval()

class TextInput(BaseModel):
    text: str

@app.post("/classify")
def classify(input: TextInput):
    inputs = tokenizer(
        input.text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=512
    )
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        predicted_class = torch.argmax(logits, dim=1).item()
        label = model.config.id2label[predicted_class]
    return {"input": input.text, "classification": label}
```

Run the server:

```bash
nohup uvicorn app:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &
```

### Step 16: Set Up FastAPI Dashboard on OnPrem-Client

SSH into the OnPrem-Client EC2 and install dependencies:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip -y
pip3 install fastapi uvicorn jinja2 requests
```

Create `dashboard.py`:

```python
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests

app = FastAPI()
templates = Jinja2Templates(directory="templates")

INFERENCE_SERVER_URL = "http://10.0.1.146:8000/classify"

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "result": None})

@app.post("/classify", response_class=HTMLResponse)
async def classify(request: Request, text: str = Form(...)):
    try:
        response = requests.post(INFERENCE_SERVER_URL, json={"text": text})
        result = response.json()
    except Exception as e:
        result = {"error": str(e)}
    return templates.TemplateResponse("index.html", {"request": request, "result": result})
```

Create `templates/index.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>OnPrem Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f4f9; color: #333; }
        .container { max-width: 600px; margin: 50px auto; padding: 20px; background: white; border-radius: 8px; }
        h1 { text-align: center; }
        textarea { width: 100%; padding: 10px; }
        button { background: #007BFF; color: white; padding: 10px 20px; border: none; border-radius: 5px; }
        .result { margin-top: 20px; padding: 15px; background: #e9ecef; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔒 Secure AI/ML Inference</h1>
        <form action="/classify" method="post">
            <textarea name="text" rows="4" placeholder="Enter text to classify..." required></textarea><br>
            <button type="submit">Classify</button>
        </form>
        {% if result %}
        <div class="result">
            <strong>Input:</strong> {{ result.input }}<br>
            <strong>Classification:</strong> {{ result.classification }}
        </div>
        {% endif %}
    </div>
</body>
</html>
```

Run the dashboard:

```bash
nohup uvicorn dashboard:app --host 0.0.0.0 --port 80 > dashboard.log 2>&1 &
```

### Step 17: Set Up Session Manager for Private EC2 Access

To SSH into the private Inference-Server without a bastion:

1. Create an IAM role named `SSM-Role-For-Private-EC2` with the policy `AmazonSSMManagedInstanceCore`.
2. Attach this role to the Inference-Server EC2.
3. Install SSM Agent on the EC2.
4. Use **AWS Systems Manager → Session Manager** to connect.

Install SSM Agent (Ubuntu):

```bash
sudo snap install amazon-ssm-agent --classic
sudo systemctl enable snap.amazon-ssm-agent.amazon-ssm-agent.service
sudo systemctl start snap.amazon-ssm-agent.amazon-ssm-agent.service
```

---

## Verification

After completing the implementation, verify each piece:

- [ ] `ML-Inference-VPC` exists with CIDR `10.0.0.0/16`.
- [ ] `Private-Subnet-1` exists with CIDR `10.0.1.0/24` and public IP auto-assignment disabled.
- [ ] `Inference-Server` EC2 is running in `Private-Subnet-1` with no public IP.
- [ ] `Secure-TGW` exists and is in `available` state.
- [ ] VPN attachment to TGW is in `available` state.
- [ ] TGW route table propagates the on-prem CIDR `10.100.0.0/16`.
- [ ] `OnPrem-VPC` and `OnPrem-Public-Subnet` exist with IGW attached.
- [ ] `OnPrem-Client` EC2 has a public IP and is reachable via SSH.
- [ ] strongSwan shows `ESTABLISHED` tunnel state: `sudo ipsec status`.
- [ ] FRR BGP session is `Established`: `sudo vtysh -c "show ip bgp summary"`.
- [ ] Inference server is listening: `curl http://10.0.1.x:8000/` returns a FastAPI response.

---

## Testing

### Test 1: Connectivity (OnPrem → Inference Server)

From the OnPrem-Client EC2:

```bash
ping 10.0.1.146   # Private IP of Inference Server
```

Expected: Successful replies.

### Test 2: Inference API Directly

```bash
curl -X POST http://10.0.1.146:8000/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "I love this product!"}'
```

Expected response:

```json
{"input":"I love this product!","classification":"positive"}
```

### Test 3: End-to-End via Dashboard

1. Get the public IP of the OnPrem-Client EC2.
2. Open `http://<ON_PREM_PUBLIC_IP>/` in a browser.
3. Enter text and click **Classify**.
4. Verify the classification result appears.

### Sample Test Outputs

| Input Text | Classification |
|------------|----------------|
| I love this product, it works perfectly! | positive |
| This is the worst experience I've ever had. | negative |
| The package arrived on time as expected. | neutral |
| Absolutely fantastic service, highly recommend! | positive |

---

## Troubleshooting

| Problem | Likely Cause | Fix |
|---------|--------------|-----|
| `ipsec status` shows no connection | Wrong PSK or public IP in `/etc/ipsec.conf` | Re-download the AWS VPN config and verify `leftid`, `right`, and the PSK in `/etc/ipsec.secrets` |
| BGP session stuck in `Active` | FRR not enabled or wrong neighbor IP | Set `bgpd=yes` in `/etc/frr/daemons`, restart FRR, verify neighbor IP matches tunnel inside CIDR |
| `ping 10.0.1.146` fails from OnPrem | Missing route to VPC CIDR | Add `ip route add 10.0.0.0/16 via <TUNNEL_INSIDE_IP>` |
| Can't SSH to Inference-Server | EC2 has no public IP | Use AWS Systems Manager Session Manager or a bastion host |
| `curl http://10.0.1.146:8000/` times out | Security group missing port 8000 inbound rule | Add rule: Custom TCP, port 8000, source `10.100.0.0/16` |
| `requests.post` from dashboard returns connection error | Inference server not running or wrong IP | SSH into Inference-Server (via SSM), check `ps aux | grep uvicorn`, restart if needed |
| TGW attachment stays in `pending` for too long | VPN still provisioning | Wait 5–10 minutes; refresh VPN connection page |
| Dashboard port 80 in use | Another service bound to port 80 | Change dashboard to port 8080: `--host 0.0.0.0 --port 8080` |

---

## Cleanup

To avoid unnecessary charges, delete resources in this exact order:

1. **Terminate EC2 instances** (Inference-Server, OnPrem-Client).
2. **Delete VPN Connection.**
3. **Delete Transit Gateway Attachment.**
4. **Delete Transit Gateway.**
5. **Delete Customer Gateway.**
6. **Detach and delete Internet Gateway** (`OnPrem-IGW`).
7. **Delete VPCs** (`ML-Inference-VPC`, `OnPrem-VPC`).
8. **Delete S3 bucket** (objects first, then bucket).

```bash
# Example teardown order (AWS CLI):
aws ec2 terminate-instances --instance-ids i-INFERENCE_ID i-ONPREM_ID
aws ec2 delete-vpn-connection --vpn-connection-id vpn-XXXXX
aws ec2 delete-transit-gateway-vpc-attachment --transit-gateway-attachment-id tgw-attach-XXXXX
aws ec2 delete-transit-gateway --transit-gateway-id tgw-XXXXX
aws ec2 delete-customer-gateway --customer-gateway-id cgw-XXXXX
aws ec2 detach-internet-gateway --internet-gateway-id igw-XXXXX --vpc-id vpc-ONPREM_ID
aws ec2 delete-internet-gateway --internet-gateway-id igw-XXXXX
aws ec2 delete-vpc --vpc-id vpc-ML_ID
aws ec2 delete-vpc --vpc-id vpc-ONPREM_ID
aws s3 rm s3://poridhilabs/models/text_classification_model.zip
```

---

## Epilogue

You have successfully built a production-grade hybrid AI inference pipeline that spans an on-premises simulated environment and an AWS private VPC, with an encrypted IPsec VPN tunnel and dynamic BGP routing through an AWS Transit Gateway. The FastAPI inference server is safely hidden from the public internet while remaining accessible to authorized on-prem clients, and a clean dashboard surfaces results back to the user.

This pattern is the foundation for many real-world enterprise ML deployments where sensitive data, regulatory compliance, or low-latency private connectivity make a fully public cloud endpoint unacceptable.

---

## Principles

This lab demonstrates several core engineering and security principles:

- **Defense in depth** — No public IP on the inference server; multiple layers (subnet, SG, TGW, VPN).
- **Least privilege networking** — Security groups only allow traffic from the explicit on-prem CIDR.
- **End-to-end encryption** — IPsec tunnel encrypts all on-prem ↔ AWS traffic.
- **Dynamic routing with BGP** — Routes are exchanged automatically; no static entries required for new subnets.
- **Centralized connectivity** — Transit Gateway serves as a single hub for future VPCs and on-prem sites.
- **Separation of concerns** — Client dashboard, VPN/BGP stack, and inference server run as distinct, independently configurable units.
- **Cost awareness** — Explicit cleanup order prevents orphaned billable resources.

---

## What You Learned

- Designing a multi-VPC architecture for AI/ML workloads.
- Configuring AWS Transit Gateway for secure inter-VPC connectivity.
- Deploying a FastAPI inference server in a private VPC with no public exposure.
- Establishing a BGP-enabled VPN tunnel using strongSwan and FRRouting.
- Building an on-premises dashboard to interact with a cloud-hosted AI service.
- Implementing end-to-end encryption for AI inference traffic.
- Using AWS Systems Manager Session Manager to access private EC2 instances.
- Cleaning up AWS resources to avoid unexpected billing.

---

## Next Steps

- Add **authentication** (mutual TLS or API keys) to the inference API.
- Integrate **AWS PrivateLink** for private connectivity without VPN.
- Add **AWS WAF** and **AWS Shield** for additional security layers.
- Deploy the inference server using **containers (ECS/EKS)** for scalability.
- Implement **model versioning** and **A/B testing** for production AI workloads.
- Add **Prometheus + Grafana** for monitoring the VPN tunnel and inference latency.

---

## Additional Resources

- [AWS Transit Gateway Documentation](https://docs.aws.amazon.com/vpc/latest/tgw/what-is-transit-gateway.html)
- [strongSwan Documentation](https://strongswan.org/documentation/)
- [FRRouting (FRR) User Guide](https://docs.frrouting.org/en/latest/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/index)
- [AWS Site-to-Site VPN](https://docs.aws.amazon.com/vpn/latest/s2svpn/VPC_VPN_Concepts.html)
- [BGP Protocol Overview](https://www.cloudflare.com/learning/security/glossary/what-is-bgp/)
- [AWS Systems Manager Session Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html)
- [Poridhi Labs](https://www.poridhi.io/)

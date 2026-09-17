# AWS for DevOps — Class Notes

> **Course:** DevOps
> **Class:** AWS Introduction
> **Last updated:** 2026-09-17
> **Style:** Beginner-friendly with analogies. Read top-to-bottom for a logical learning flow.

---

## Table of Contents

0. [Learning Path / How to Read This Document](#0-learning-path--how-to-read-this-document)
1. [Quick Clarifications / Q&A](#1-quick-clarifications--qa)
2. [AWS Cloud Basics — Region, AZ, Data Center, Primitives](#2-aws-cloud-basics--region-az-data-center-primitives)
3. [Networking Fundamentals — Host, Network, Packet, IP](#3-networking-fundamentals--host-network-packet-ip)
4. [Routing — Router, Route Table, Virtual Router, Linux as a Router](#4-routing--router-route-table-virtual-router-linux-as-a-router)
5. [VPC — AWS's Virtual Network](#5-vpc--awss-virtual-network)
6. [Linux, Bash, Shell Scripts — The Automation Layer](#6-linux-bash-shell-scripts--the-automation-layer)
7. [AWS CLI — Talking to AWS from the Terminal](#7-aws-cli--talking-to-aws-from-the-terminal)
8. [Putting It All Together — A Typical AWS Lab Workflow](#8-putting-it-all-together--a-typical-aws-lab-workflow)
9. [Key Mental Models](#9-key-mental-models)
10. [Common Beginner Mistakes & Corrections](#10-common-beginner-mistakes--corrections)
11. [Commands Cheat Sheet](#11-commands-cheat-sheet)
12. [Final Big Picture](#12-final-big-picture)

---

## 0. Learning Path / How to Read This Document

The notes are arranged so each concept builds on the previous one:

```text
AWS Cloud Basics
      ↓
Networking Fundamentals
      ↓
Routing (how traffic moves)
      ↓
VPC (AWS's logical network)
      ↓
Linux + Bash (tools to automate)
      ↓
AWS CLI (tool to talk to AWS)
      ↓
Putting it all together
```

If something in a later section confuses you, scroll up — the missing concept is probably explained earlier.

---

## 1. Quick Clarifications / Q&A

### Q1: What does "compute" mean in AWS?
**Compute = renting a server.** Instead of buying a physical machine, you rent virtual CPU + RAM + OS on demand.

AWS Compute services: **EC2** (virtual servers), **Lambda** (serverless), **ECS/EKS** (containers), **Fargate** (serverless containers), **Lightsail** (simple VPS).

> 💡 **Analogy:** Compute is like renting an apartment instead of building a house. You pay only while you live there.

---

### Q2: To connect a user to two servers, do we need a router and a switch?
**Yes — both, but they do different jobs:**

```text
User → ROUTER (network entry point) → SWITCH (delivers to the right server locally) → Server A or B
```

| Device | Job | Layer | Uses |
|--------|-----|-------|------|
| **Switch** | Connects devices inside the **same** network | L2 | MAC address |
| **Router** | Connects **different** networks | L3 | IP address |

> 🏙️ **Analogy:** Switch = roads inside a city. Router = highway/bridge between cities.

---

### Q3: What is the difference between Docker and a VM?
**Both isolate apps, but in very different ways:**

| Feature | 🖥️ VM | 🐳 Docker |
|---------|--------|-----------|
| Own OS? | ✅ Yes (full Guest OS) | ❌ No (shares host kernel) |
| Boot time | Minutes | Seconds |
| Size | GBs | MBs |
| Density per host | ~10s | 100s–1000s |
| Best for | Different OSes, strong isolation | Microservices, CI/CD |

> 🏠 **Analogy:** VM = a whole house (own foundation, plumbing, electricity). Container = a rented room in a building (infrastructure already exists, you just bring your stuff).

> 🎯 **Key idea:** **VM virtualizes hardware. Container virtualizes the OS/application layer.**

In AWS, EC2 (VM) often hosts Docker containers inside it.

---

### Q4: What are AWS primitives?
**AWS primitives = fundamental building blocks** you can combine like LEGO to build systems.

```text
AWS Primitives
    |
    +-- Compute       → EC2
    +-- Storage       → S3
    +-- Networking    → VPC
    +-- Database      → RDS
    +-- Identity      → IAM
    +-- DNS           → Route 53
    +-- Messaging     → SQS
```

Example: A production ML API = `VPC + EC2 + S3 + IAM + Load Balancer`.

> 🧱 **Analogy:** Primitives are like LEGO pieces. Each piece has one job; together they build anything.

---

### Q5: What is an AWS DC (Data Center)?
**DC = Data Center** — a physical facility with:

```text
Physical Servers · CPUs · RAM · Storage · Network Equipment · Power · Cooling
```

The hierarchy:

```text
AWS Region  (e.g., "us-east-1" — a geographic area)
    |
    +-- Availability Zone (one or more data centers, isolated)
    |       |
    |       +-- Physical infrastructure
    |
    +-- Availability Zone
            |
            +-- Physical infrastructure
```

| Term | Meaning |
|------|---------|
| **Region** | A geographic AWS location containing multiple AZs |
| **Availability Zone (AZ)** | An isolated location within a Region |
| **Data Center** | A physical facility |
| **VPC** | A *logical* network (NOT a physical data center) |

> 🏢 **Analogy:** Region = country. AZ = city inside that country. Data Center = building inside that city.

---

### Q6: What is a packet?
**A packet = a small chunk of data traveling over a network.**

```text
Large Data → split into many Packets → each packet travels independently → reassembled at destination
```

Structure of an IP packet:

```text
+--------------------------+
| Header                   |
|  - Source IP             |
|  - Destination IP        |
|  - Protocol              |
+--------------------------+
| Payload (actual data)    |
+--------------------------+
```

> 📦 **Analogy:** A packet is like a letter. The header is the envelope (from/to addresses). The payload is the letter inside.

---

### Q7: What is the difference between a host and a network?
- **Network** = a *range* of IP addresses (e.g., `192.168.1.0/24`).
- **Host** = an *individual device* inside that network (e.g., `192.168.1.10`).

```text
Network: 192.168.1.0/24
    |
    +-- 192.168.1.10  Laptop
    +-- 192.168.1.20  Server
    +-- 192.168.1.30  Printer
```

> 🏘️ **Analogy:** Network = a neighborhood. Host = one house inside that neighborhood.

---

### Q8: What is `.sh`? What does `vpc.sh` mean?
- **`.sh`** = common file extension for **shell scripts**.
- **`vpc.sh`** = a shell script whose name suggests it deals with VPC stuff.

```bash
#!/bin/bash
aws ec2 create-vpc --cidr-block 10.0.0.0/16
```

> 📝 **Analogy:** `.sh` is like `.docx` for Word docs — it just tells you the file type.

---

### Q9: What is `#!/bin/bash`?
**A shebang** — tells the OS which interpreter to use when running the script directly.

```text
#!        → interpreter marker
/bin/bash → path to the Bash program
```

Equivalent forms:
```bash
#!/bin/bash         # hardcoded path
#!/usr/bin/env bash # looks up Bash in $PATH (more portable)
```

> 🎬 **Analogy:** The shebang is like a "play this video with VLC" instruction. It tells the system which tool opens the file.

---

### Q10: What does `chmod +x` mean?
- **`chmod`** = change mode (change file permissions)
- **`+x`** = add execute permission

```bash
chmod +x vpc.sh    # adds execute permission
./vpc.sh           # now you can run it directly
bash vpc.sh        # works without +x because you call bash yourself
```

Permission symbols:
```text
r = read · w = write · x = execute
```

> 🔑 **Analogy:** `chmod +x` is like unlocking a door. The file was there before, but you couldn't enter. Now you can.

---

### Q11: Why use `aws configure`?
To set up the **AWS CLI** on your machine. It asks for:

```text
AWS Access Key ID
AWS Secret Access Key
Default region name
Default output format
```

Stored in `~/.aws/credentials` and `~/.aws/config`.

> ⚠️ **`aws configure` does NOT create an AWS account.** It just configures the CLI to use an existing account.

> 🪪 **Analogy:** `aws configure` is like saving your login to a website — the account already exists; you're just remembering the credentials locally.

---

### Q12: What is Bash scripting?
**Writing commands + logic in a `.sh` file** so the shell can execute them automatically.

```bash
#!/bin/bash

NAME="Akash"
for server in server1 server2 server3
do
  echo "Checking $server"
done
```

Used for: installs, deployments, CI/CD, AWS automation, Docker workflows.

> 🤖 **Analogy:** Bash scripting is like giving your computer a to-do list it can run without you typing each step.

---

## 2. AWS Cloud Basics — Region, AZ, Data Center, Primitives

### The Big Picture

```text
AWS Global Infrastructure
        |
        +-- Regions (geographic areas, e.g., us-east-1, eu-west-1)
                |
                +-- Availability Zones (1+ data centers, isolated)
                        |
                        +-- Physical Data Centers
                                |
                                +-- Servers, Storage, Network
```

### Why multiple AZs?

**High availability.** If one data center has a power outage, your app can still run in another AZ in the same region.

> 🏥 **Analogy:** A hospital has multiple wings. If one wing has a problem, patients are moved to another.

### AWS Primitives (the LEGO pieces)

| Category | Service |
|----------|---------|
| Compute | EC2 |
| Storage | S3 |
| Networking | VPC |
| Database | RDS |
| Identity | IAM |
| DNS | Route 53 |
| Messaging | SQS |

You rarely use just one — production systems combine many primitives.

---

## 3. Networking Fundamentals — Host, Network, Packet, IP

### Host vs Network

```text
Network = a range of addresses     (e.g., 10.1.0.0/16)
Host    = one device in that range (e.g., 10.1.2.10)
```

### CIDR notation explained

```text
10.1.0.0/16
       ^^
       |
       +-- "First 16 bits are the network prefix. The remaining 16 bits are for hosts."
```

> 🏘️ **Analogy:** Think of a postal code system. `/16` is like saying "the first 16 characters of an address identify the region; the rest identify the specific house."

### Packet structure

```text
+-------------------+
| Header            |
|   - Source IP     |
|   - Destination IP|
|   - Protocol      |
+-------------------+
| Payload (data)    |
+-------------------+
```

### The networking stack (top → bottom)

```text
Application Data
        ↓
Transport Segment       (TCP/UDP)
        ↓
IP Packet               ← the unit we call "packet"
        ↓
Network Frame           (Ethernet)
        ↓
Physical Signals        (electrical / light)
```

> 🚚 **Analogy:** Imagine sending a package. App data = the goods. TCP = packaging. IP packet = the box labeled with source/destination addresses. Frame = the truck carrying it. Physical signals = the road.

---

## 4. Routing — Router, Route Table, Virtual Router, Linux as a Router

### What is a Router?

A device (physical or virtual) that **forwards packets between networks** based on destination IP.

```text
Packet comes in
     ↓
Look at destination IP
     ↓
Check routing table
     ↓
Choose next hop / interface
     ↓
Forward packet
```

> 🚦 **Analogy:** A router is the highway interchange that decides which exit a car takes based on its destination.

### Physical Router vs Virtual Router

| | Physical Router | Virtual Router |
|--|-----------------|----------------|
| Implementation | Dedicated hardware | Software |
| Used in | Offices, ISPs | AWS VPC, cloud, VMs |
| Example brands | Cisco, Juniper | AWS VPC Router, Linux box |

### Route Table — the rules, NOT the action

```text
Destination       Target
--------------------------------
10.1.0.0/16       local
10.2.0.0/16       Transit Gateway
0.0.0.0/0         Internet Gateway
```

`0.0.0.0/0` means **"everything else"** — the default route.

> 🗺️ **Analogy:**
> ```
> Route Table = Map         (tells you where to go)
> Router      = Driver     (actually drives)
> Packet      = Package    (the thing being moved)
> Destination = Customer   (where it's going)
> ```

### Linux as a Router

**Yes, you can.** Linux routes traffic if IP forwarding is enabled and the interfaces are set up.

```bash
# Check current routing table
ip route

# Check if IP forwarding is on
sysctl net.ipv4.ip_forward
# If it returns 0, forwarding is OFF

# Enable IP forwarding (temporary)
sudo sysctl -w net.ipv4.ip_forward=1
```

```text
Network A (192.168.1.0/24)        Network B (10.0.0.0/24)
        |                                  |
        +--------→ Linux Router <---------+
                  eth0: 192.168.1.1
                  eth1: 10.0.0.1
```

> 🐧 **Analogy:** A Linux box with two network cables and IP forwarding on is essentially a homemade router.

---

## 5. VPC — AWS's Virtual Network

### What is a VPC?

**VPC = Virtual Private Cloud** — a **logical, isolated network** inside AWS.

A VPC is **NOT** a physical data center. It runs on top of AWS physical infrastructure.

```text
Physical AWS Infrastructure
            ↓
Logical VPC
            ↓
    +-- Subnets
    +-- Route Tables
    +-- Security Groups
    +-- Gateways (Internet Gateway, NAT Gateway)
```

### Key VPC components

| Component | Job |
|-----------|-----|
| **Subnet** | A sub-range of IPs inside a VPC, in one AZ |
| **Route Table** | Routing rules for the VPC/subnet |
| **Internet Gateway** | Lets the VPC reach the public internet |
| **NAT Gateway** | Lets private subnet reach internet (but not vice versa) |
| **Security Group** | Virtual firewall for EC2 instances |
| **NACL** | Stateless firewall at subnet level |

> 🏙️ **Analogy:** VPC = a private gated community. Subnets = different neighborhoods. Internet Gateway = the main gate. Security Group = door locks on individual houses.

### Physical vs Logical — DON'T confuse these

```text
❌ WRONG: "VPC is a data center"
✅ RIGHT: "VPC is a logical network that runs ON TOP of data centers"
```

---

## 6. Linux, Bash, Shell Scripts — The Automation Layer

### The Three Different Things

```text
Linux          = the operating system
Bash           = the command interpreter (shell)
Bash Script    = a file (.sh) containing Bash commands
```

> 🍔 **Analogy:** Linux = the kitchen. Bash = the chef. Bash Script = a recipe the chef follows.

### A typical script

```bash
#!/bin/bash

# Create a project folder
mkdir -p my-project
cd my-project

# Create files
touch app.py
echo "Hello, world!" > message.txt

# Show what we did
ls -la
```

### How to run it

```bash
chmod +x script.sh    # 1. Add execute permission
./script.sh           # 2. Run directly (uses shebang)
# OR
bash script.sh        # 2b. Run explicitly with Bash (no +x needed)
```

### Bash supports real programming

```bash
# Variables
NAME="Akash"
echo "Hello $NAME"

# Condition
if [ -f "app.py" ]; then
  echo "File exists"
fi

# Loop
for server in server1 server2 server3; do
  echo "Checking $server"
done

# Function
create_vpc() {
  aws ec2 create-vpc --cidr-block 10.0.0.0/16
}
```

### What Bash scripting is used for in DevOps

```text
Bash Script
    |
    +-- Install packages
    +-- Configure Linux
    +-- Start/stop services
    +-- Build Docker images
    +-- Run tests
    +-- Configure AWS resources
    +-- Deploy applications
```

---

## 7. AWS CLI — Talking to AWS from the Terminal

### What is AWS CLI?

A command-line tool that lets you **create, read, update, and delete AWS resources** using text commands.

> 📞 **Analogy:** AWS Console = calling AWS on the phone. AWS CLI = texting AWS instead.

### Setup

```bash
aws configure
# Provide: Access Key, Secret Key, Region, Output format
```

Stored in:
```text
~/.aws/credentials   → authentication
~/.aws/config        → region & preferences
```

### Common commands

```bash
# List your VPCs
aws ec2 describe-vpcs

# Create a VPC
aws ec2 create-vpc --cidr-block 10.0.0.0/16

# List S3 buckets
aws s3 ls

# Describe EC2 instances
aws ec2 describe-instances
```

### ⚠️ Security reminders

- ❌ Never hard-code credentials in scripts
- ❌ Never commit `.aws/credentials` or access keys to Git
- ✅ Use IAM roles whenever possible
- ✅ Rotate keys regularly

---

## 8. Putting It All Together — A Typical AWS Lab Workflow

```bash
# Step 1: Configure AWS CLI with your credentials
aws configure

# Step 2: Create a script file
nano vpc.sh
```

Type inside:
```bash
#!/bin/bash

aws ec2 create-vpc \
    --cidr-block 10.0.0.0/16
```

```bash
# Step 3: Allow it to be executed
chmod +x vpc.sh

# Step 4: Run it
./vpc.sh
```

### What just happened?

```text
You (typed ./vpc.sh)
    ↓
Linux kernel sees execute bit + shebang
    ↓
Bash interpreter reads the script
    ↓
AWS CLI command runs
    ↓
AWS API call is made over the network
    ↓
AWS creates the VPC and returns a response
```

---

## 9. Key Mental Models

### Networking

```text
Network   → a range of IP addresses
Host      → one device inside a network
Packet    → a chunk of data with source/dest IPs
Router    → forwards packets between networks
Route Table → rules telling the router where to send packets
```

### Linux + Bash

```text
Linux      → OS
Bash       → Shell / command interpreter
Bash Script → file of commands (.sh)
#!/bin/bash → tells OS which interpreter to use
chmod +x   → adds "executable" permission
```

### AWS

```text
Region     → geographic area (e.g., us-east-1)
AZ         → isolated location inside a Region
Data Center → physical building inside an AZ
VPC        → logical private network (NOT physical)
EC2        → virtual server inside a VPC
```

---

## 10. Common Beginner Mistakes & Corrections

| ❌ Wrong belief | ✅ Correct understanding |
|-----------------|-------------------------|
| "VPC is a data center" | VPC is a **logical** network on top of AWS physical infra |
| "Route table forwards packets" | Route table only **holds rules**; the routing system forwards |
| "`.sh` is an AWS thing" | `.sh` is just a **shell script** extension; used everywhere in Linux |
| "`#!/bin/bash` means Bash = Linux" | **Linux** = OS, **Bash** = shell; they are different layers |
| "`chmod +x` runs the script" | `chmod +x` only adds permission; you still need to `./script.sh` |
| "`aws configure` creates my account" | It only **configures the CLI** on your machine; account is separate |
| "EC2 is a server" | EC2 is a **virtual server** (VM) running on AWS hardware |

---

## 11. Commands Cheat Sheet

```bash
# --- Bash basics ---
which bash                # find Bash location
chmod +x script.sh        # add execute permission
./script.sh               # run script (needs shebang + x permission)
bash script.sh            # run script explicitly (no x needed)

# --- Linux networking ---
ip route                                  # show routing table
sysctl net.ipv4.ip_forward                # check IPv4 forwarding
sudo sysctl -w net.ipv4.ip_forward=1      # enable IPv4 forwarding

# --- AWS CLI ---
aws configure                             # configure AWS CLI
aws ec2 describe-vpcs                     # list your VPCs
aws ec2 create-vpc --cidr-block 10.0.0.0/16   # create a VPC
aws ec2 describe-instances                # list EC2 instances
aws s3 ls                                 # list S3 buckets
```

---

## 12. Final Big Picture

Everything in this class connects like this:

```text
        AWS Global Infrastructure
                  |
        +---------+---------+
        |                   |
    Regions              AZs
        |                   |
        |             Data Centers (physical)
        |                   |
        +---→  VPC (logical network)
                    |
        +-----------+-----------+
        |           |           |
    Subnets    Route Tables   Gateways
        |           |           |
    EC2 Hosts    Routing Rules Internet
        |           |
        +---+-------+
            |
         Packets
            |
      Routing System
            |
      Next Hop / Target
```

And on your laptop / Linux machine:

```text
Linux
  ├── Bash (shell)
  │     └── Bash Scripts (.sh files)
  ├── Network Stack
  │     ├── Routing Table
  │     ├── IP Forwarding
  │     └── Network Interfaces
  └── AWS CLI
        └── Talks to AWS API
```

### The one sentence that ties everything together:

> **Networks contain hosts. Hosts send packets. Routers forward packets using route tables. Linux can act as a router. Bash scripts automate commands. The AWS CLI lets Bash scripts talk to AWS. AWS provides primitives (like EC2, VPC, S3) that you can combine to build systems, all running on top of physical data centers organized into Regions and Availability Zones.**

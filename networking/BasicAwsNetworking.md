`AWS_Networking_Fundamentals_Preparation_Notes.md`

````markdown
# AWS Networking Fundamentals: Preparation Notes

## Purpose

These notes collect the networking fundamentals discussed before working with AWS VPC and EC2 networking labs.

The goal is to understand **why each AWS networking component exists**, not just memorize AWS console steps.

---

# 1. What You Need to Know Before the Labs

The most important concepts, in order, are:

1. IP address
2. IPv4 structure
3. Private vs. public IP
4. CIDR notation
5. Network vs. host/address
6. Network
7. Subnet
8. Routing
9. Route
10. Default route
11. Gateway
12. Internet Gateway
13. Port
14. TCP
15. Security Group
16. DNS resolution
17. VPC
18. Public vs. private subnet
19. EC2 networking

The four concepts that should become especially solid are:

> **IP → CIDR → Subnet → Routing**

Once these are clear, VPC, route tables, Internet Gateways, security groups, and public/private subnets become much easier.

---

# 2. IP Address

An IP address is an address used to identify a network interface on a network.

Example:

```text
10.0.0.5
192.168.1.10
````

Think of it like an address for network communication.

A computer needs an IP address so other devices know where to send network traffic.

---

# 3. IPv4

IPv4 addresses contain **32 bits**.

They are normally written as four groups called octets:

```text
10.0.0.5
```

Each octet contains 8 bits:

```text
8 + 8 + 8 + 8 = 32 bits
```

An 8-bit value has:

```text
2^8 = 256
```

possible values.

Those values are:

```text
0 through 255
```

Therefore, an IPv4 octet cannot be larger than 255.

For example:

```text
10.0.0.255
```

is valid.

But:

```text
10.0.0.256
```

is not a valid IPv4 address.

---

# 4. Why Does an IPv4 Address Look Like 10.0.0.0?

There is nothing special about `10.0.0.0`.

It is one possible IPv4 address.

For private networks, common private ranges include:

```text
10.0.0.0/8
172.16.0.0/12
192.168.0.0/16
```

Therefore, this is also a valid private IP:

```text
192.168.1.1
```

Your AWS lab uses:

```text
10.0.0.0/16
```

because `10.0.0.0` is a convenient private address range for the lab.

---

# 5. Private IP vs. Public IP

A private IP is used inside a private network.

Example:

```text
10.0.0.10
```

A public IP can be used to communicate over the public Internet.

Example:

```text
52.221.245.83
```

An EC2 instance can have both:

```text
EC2
|
+-- Private IP: 10.0.0.10
|
+-- Public IP: 52.221.245.83
```

The private IP is used inside the VPC.

The public IP allows communication with the instance from outside the VPC, subject to routing and security rules.

---

# 6. CIDR

CIDR stands for **Classless Inter-Domain Routing**.

CIDR notation looks like:

```text
10.0.0.0/16
10.0.0.0/24
10.0.0.5/32
```

The number after `/` tells you how many of the 32 IPv4 bits are fixed.

## /16

```text
10.0.0.0/16
```

Means:

```text
16 bits fixed
16 bits can change
```

Therefore:

```text
2^16 = 65,536 addresses
```

The range is:

```text
10.0.0.0
through
10.0.255.255
```

Conceptually:

```text
10.0 | X.X
```

The first 16 bits define the network range, while the remaining 16 bits provide the address space inside that range.

## /24

```text
10.0.0.0/24
```

Means:

```text
24 bits fixed
8 bits can change
```

Therefore:

```text
2^8 = 256 addresses
```

Range:

```text
10.0.0.0
through
10.0.0.255
```

Conceptually:

```text
10.0.0 | X
```

## /32

```text
10.0.0.5/32
```

Means:

```text
32 bits fixed
0 bits can change
```

Therefore:

```text
2^0 = 1 address
```

So `/32` represents exactly one IP address.

## General Formula

```text
Number of addresses = 2^(32 - CIDR prefix)
```

Examples:

```text
/16 → 2^16 = 65,536
/24 → 2^8  = 256
/28 → 2^4  = 16
/32 → 2^0  = 1
```

The important idea is:

> The CIDR prefix tells you how many bits are fixed. The remaining bits can vary.

---

# 7. What Does "For the Network" Mean?

When we say:

```text
10.0.0.0/24
```

has 24 fixed bits, it does not mean that an individual device has 24 bits assigned to it.

It means the CIDR range defines a group of addresses where those 24 bits remain the same.

For example:

```text
10.0.0.1
10.0.0.2
10.0.0.3
...
10.0.0.255
```

The `/24` describes the common network portion of those addresses.

---

# 8. Network and Host

A network is a range of addresses that can contain multiple network interfaces or devices.

Conceptually:

```text
Network
|
+-- Device
+-- Device
+-- Device
+-- Device
```

For example:

```text
10.0.0.0/24
```

provides a range of addresses within that network.

When you create a smaller subnet from a larger network, some bits that were previously available become part of the subnet's network definition.

---

# 9. VPC

VPC means **Virtual Private Cloud**.

An AWS VPC is a logically isolated virtual network in AWS.

For example:

```text
VPC
10.0.0.0/16
```

This gives the VPC an address space containing:

```text
65,536 IPv4 addresses
```

Important clarification:

> `10.0.0.0/16` is not one IP address assigned to the VPC. It is a CIDR range associated with the VPC.

---

# 10. Example: Model VPC

Suppose you create:

```text
Name: Model-VPC
IPv4 CIDR: 10.0.0.0/16
```

This means the VPC has the address range:

```text
10.0.0.0
through
10.0.255.255
```

It contains 65,536 IPv4 addresses.

---

# 11. Example: Client VPC

Suppose you create:

```text
Name: Client-VPC
IPv4 CIDR: 10.1.0.0/16
```

This is another VPC with:

```text
10.1.0.0
through
10.1.255.255
```

The two VPCs do not overlap:

```text
Model-VPC:
10.0.0.0/16

Client-VPC:
10.1.0.0/16
```

Non-overlapping CIDRs are important when networks need to communicate with each other.

---

# 12. VPC vs. Subnet

A VPC is the larger network space.

A subnet is a smaller section inside the VPC.

Example:

```text
VPC
10.0.0.0/16
|
+-- Subnet
|   10.0.0.0/24
|
+-- Subnet
|   10.0.1.0/24
|
+-- Subnet
    10.0.2.0/24
```

Think:

```text
VPC    = large network
Subnet = smaller network section
```

A subnet's CIDR must be inside the VPC's CIDR and cannot overlap with another subnet in the same VPC.

---

# 13. How a /24 Fits Inside a /16

Suppose the VPC is:

```text
10.0.0.0/16
```

It has:

```text
16 fixed bits
16 variable bits
```

Now create:

```text
10.0.0.0/24
```

The subnet has:

```text
24 fixed bits
8 variable bits
```

Therefore, some of the 16 bits that were available inside the VPC are now used to define the subnet.

Conceptually:

```text
VPC /16:

10.0 | X.X


Subnet /24:

10.0.0 | X
```

The remaining 8 bits provide 256 addresses in the subnet.

---

# 14. Subnet Design Basics

When designing a VPC and subnets, keep these ideas in mind:

### Choose an appropriate VPC CIDR

Leave enough room for future growth.

### Subnets must be inside the VPC

A subnet cannot use an address range outside the VPC CIDR.

### Subnets cannot overlap

For example:

```text
10.0.0.0/24
10.0.1.0/24
```

do not overlap.

### Plan public and private subnets

Some resources may need Internet access.

Other resources, such as databases, may need to remain private.

### Consider Availability Zones

Production architectures commonly spread resources across multiple Availability Zones for resilience.

### Avoid overlapping networks

If VPCs need to communicate, overlapping CIDRs can create routing problems.

---

# 15. What Is Routing?

Routing means deciding where network traffic should go.

Imagine a road map:

```text
You
 |
 | "I want to go to Dhaka"
 v
Road map
 |
 | "Take this road"
 v
Dhaka
```

Networking works similarly:

```text
Computer
 |
 | "I want to reach 8.8.8.8"
 v
Route Table
 |
 | "Send it this way"
 v
Next destination
```

Routing is one of the most important networking concepts for AWS.

---

# 16. What Is a Route?

A route is an instruction about where traffic should go.

A simple route looks like:

```text
Destination → Target
```

For example:

```text
10.0.0.0/16 → Local
0.0.0.0/0    → Internet Gateway
```

The route table uses these rules to decide where traffic should go.

---

# 17. What Is a Route Table?

A route table is a collection of routing rules.

Think of it as a map containing instructions:

```text
"If the destination is X, send the traffic to Y."
```

Example:

```text
Destination       Target
-----------       ----------------
10.0.0.0/16       Local
0.0.0.0/0         Internet Gateway
```

The first route handles traffic inside the VPC.

The second route handles destinations outside the VPC.

---

# 18. What Is 0.0.0.0/0?

This is extremely important.

```text
0.0.0.0/0
```

means:

> Any IPv4 destination.

It is commonly called the **default route** or **catch-all route**.

For example:

```text
10.0.0.0/16 → Local
0.0.0.0/0   → Internet Gateway
```

If the destination is not covered by a more specific route, the default route is used.

For example, if an EC2 wants to reach:

```text
8.8.8.8
```

the route table checks:

```text
Is 8.8.8.8 inside 10.0.0.0/16?
No.

Is there a catch-all route?
Yes.

0.0.0.0/0 → Internet Gateway
```

Therefore the traffic is sent toward the Internet Gateway.

---

# 19. Why Do We Need 0.0.0.0/0 → Internet Gateway?

Creating an Internet Gateway alone does not tell the VPC how Internet-bound traffic should be routed.

The route table needs an explicit instruction:

```text
Destination: 0.0.0.0/0
Target: Internet Gateway
```

This means:

> For destinations outside the VPC that do not have a more specific route, send the traffic to the Internet Gateway.

Conceptually:

```text
EC2
 |
 v
Route Table
 |
 | 0.0.0.0/0 → IGW
 v
Internet Gateway
 |
 v
Internet
```

This separation gives AWS control over which subnets have Internet routes.

---

# 20. What Is a Gateway?

A gateway is a point through which traffic can move between networks.

For example, a home network might look like:

```text
Laptop
 |
 v
Home Router
 |
 v
Internet
```

The router/gateway connects the local network to another network.

---

# 21. What Is an Internet Gateway?

IGW means **Internet Gateway**.

An Internet Gateway is an AWS-managed virtual networking component that provides a connection point between a VPC and the Internet.

Think of it as a doorway:

```text
VPC
 |
 v
Internet Gateway
 |
 v
Internet
```

But the doorway alone is not enough.

The route table must tell traffic to use it:

```text
0.0.0.0/0 → Internet Gateway
```

So:

```text
Route Table = tells traffic where to go
Internet Gateway = provides the VPC's Internet connection point
```

---

# 22. What Is the Internet Gateway Physically?

An Internet Gateway is not a physical box that you can see or touch.

It is an AWS-managed virtual networking component.

AWS operates the underlying physical infrastructure, including data centers, servers, networking equipment, and physical links.

As an AWS user, you work with the logical networking layer.

---

# 23. What Makes a Subnet Public?

A subnet is not public merely because you gave it a CIDR or created it inside a VPC.

For a typical IPv4 public subnet, the important pieces include:

```text
Subnet
  |
  +-- Route table with:
  |      0.0.0.0/0 → Internet Gateway
  |
  +-- Resource with public IPv4
  |
  +-- Security rules allowing required traffic
```

The route to the Internet Gateway is a key part of making the subnet public.

---

# 24. What Is Auto-Assign Public IPv4?

When launching an EC2 instance, you may see:

```text
Enable auto-assign public IPv4 address
```

This tells AWS:

> Automatically give this EC2 instance a public IPv4 address.

For example:

```text
EC2
|
+-- Private IP: 10.0.0.10
|
+-- Public IP: 52.221.245.83
```

The private IP is used inside the VPC.

The public IP can be used to reach the EC2 over the Internet, provided routing and security rules allow it.

Important:

> Giving an EC2 a public IP does not by itself make the subnet public.

The route table and Internet Gateway are also important.

---

# 25. Why Does an EC2 Have an IP Like 52.221.245.83?

If you enabled auto-assign public IPv4, AWS automatically assigns a public IPv4 address.

For example:

```text
Private IP:
10.0.0.10

Public IP:
52.221.245.83
```

The public IP is not part of your VPC CIDR:

```text
VPC:
10.0.0.0/16

EC2 private IP:
10.0.0.10

EC2 public IP:
52.221.245.83
```

The VPC controls the private address space.

AWS provides the public address separately.

An auto-assigned public IPv4 address can change when an instance is stopped and started. An Elastic IP is used when a persistent public IPv4 address is required.

---

# 26. What Is a Port?

An IP address identifies the network destination.

A port identifies the service or application endpoint on that machine.

Think:

```text
IP address → Which machine?
Port       → Which service?
```

Example:

```text
10.0.0.10:22
```

Here:

```text
10.0.0.10 → IP address
22         → port
```

Common ports:

```text
22  → SSH
80  → HTTP
443 → HTTPS
```

---

# 27. Why Does Port 22 Mean SSH?

SSH normally uses TCP port 22.

So:

```text
TCP :22
```

usually means traffic intended for an SSH service.

For example:

```bash
ssh ubuntu@52.221.245.83
```

uses SSH to connect to the EC2 instance.

The connection normally reaches the SSH service listening on port 22.

Important:

> Port 22 does not itself perform SSH. It is the standard port number normally used by the SSH service.

---

# 28. Why Does Port 80 Mean HTTP?

HTTP normally uses port 80.

For example:

```text
TCP :80
```

normally means HTTP traffic.

If an EC2 is running a web server on port 80, a browser can access it through:

```text
http://<EC2-public-IP>
```

Again:

> Port 80 does not itself create a web server. It is the standard port where an HTTP web server commonly listens.

---

# 29. What Is TCP?

TCP stands for **Transmission Control Protocol**.

Simply:

> TCP is a protocol that helps two computers communicate reliably over a network.

TCP handles things such as:

```text
1. Establishing a connection
2. Sending data
3. Detecting missing data
4. Re-sending missing data
5. Keeping data in order
```

A useful mental model is:

```text
IP
↓
Where should the data go?

TCP
↓
How should the communication happen reliably?

Port
↓
Which service should receive it?
```

For example:

```text
EC2
 |
 | TCP :22
 v
SSH service
```

This means TCP communication is being sent to port 22, where the SSH service normally listens.

---

# 30. TCP vs. Port

Do not confuse these two concepts.

```text
TCP = communication protocol

Port = number identifying a service endpoint
```

For example:

```text
TCP :22
```

means:

```text
Protocol = TCP
Port     = 22
Service  = normally SSH
```

And:

```text
TCP :80
```

means:

```text
Protocol = TCP
Port     = 80
Service  = normally HTTP
```

---

# 31. What Is a Security Group?

A Security Group controls which network traffic is allowed to reach an EC2 instance.

Think of it as a security guard controlling the doors of the EC2.

For example:

```text
EC2
|
+-- Port 22 → SSH
|
+-- Port 80 → HTTP
```

You can configure rules such as:

```text
Protocol: TCP
Port: 22
Source: Your IP
```

This means:

> Allow TCP connections to port 22 from your IP address.

Another rule could be:

```text
Protocol: TCP
Port: 80
Source: 0.0.0.0/0
```

This means:

> Allow HTTP traffic from IPv4 addresses everywhere.

The exact source should be chosen according to the security requirements of the system.

---

# 32. What Does "Allow SSH Port 22 and HTTP Port 80" Mean?

It means configuring the Security Group to allow incoming traffic to those service ports.

For example:

```text
Protocol   Port   Purpose
TCP        22     SSH
TCP        80     HTTP
```

Traffic can then flow like:

```text
Your computer
 |
 | TCP :22
 v
Security Group
 |
 | allowed
 v
EC2
 |
 v
SSH service
```

For HTTP:

```text
Browser
 |
 | TCP :80
 v
Security Group
 |
 | allowed
 v
EC2
 |
 v
Web server
```

A Security Group does not automatically make the EC2 public.

Routing, public IP addressing, and the Internet Gateway also matter.

---

# 33. What Is DNS Resolution?

DNS stands for **Domain Name System**.

DNS resolution means:

> Converting a human-friendly domain name into an IP address.

For example:

```text
google.com
     ↓
DNS lookup
     ↓
IP address
```

Humans use:

```text
google.com
```

while network communication ultimately uses IP addresses.

Think of DNS as a phone book:

```text
Domain name       IP address

google.com   →    an IP address
github.com   →    an IP address
```

When you run:

```bash
ping google.com
```

your system first needs to resolve:

```text
google.com → IP address
```

Then it can attempt to communicate with that IP address.

---

# 34. DNS Resolution vs. Routing vs. Ping

These are different concepts.

### DNS resolution

```text
google.com → IP address
```

### Routing

```text
IP address → Where should traffic go?
```

### Ping

`ping` sends ICMP echo requests to test whether a destination responds.

So when you run:

```bash
ping google.com
```

several things can be involved:

```text
google.com
    |
    | DNS resolution
    v
IP address
    |
    | Routing
    v
Destination
    |
    | ICMP
    v
Response
```

A failed ping does not always mean DNS is broken. Ping can fail for other reasons, including routing or the destination not responding to ICMP.

---

# 35. What Happens When an EC2 Connects to the Internet?

Suppose:

```text
VPC:
10.0.0.0/16

Subnet:
10.0.0.0/24

EC2 private IP:
10.0.0.10

EC2 public IP:
52.221.245.83
```

The conceptual path is:

```text
EC2
10.0.0.10
   |
   v
Subnet
   |
   v
Route Table
   |
   | 0.0.0.0/0 → Internet Gateway
   v
Internet Gateway
   |
   v
Internet
```

The important pieces have different responsibilities:

```text
VPC
↓
Provides the larger private network

Subnet
↓
Provides a smaller network section

EC2
↓
Runs the workload

Private IP
↓
Identifies the EC2 inside the VPC

Public IP
↓
Provides Internet-facing addressing

Route Table
↓
Decides where traffic should go

Internet Gateway
↓
Provides the VPC's Internet connection point

Security Group
↓
Controls allowed traffic to the EC2

DNS
↓
Resolves names into IP addresses
```

---

# 36. Full Lab Example

A basic public EC2 lab may look like this:

```text
                         INTERNET
                            |
                            |
                    Internet Gateway
                            |
                            |
                    0.0.0.0/0 → IGW
                            |
                       Route Table
                            |
                            |
                    Public Subnet
                    10.0.0.0/24
                            |
                            |
                           EC2
                   Private: 10.0.0.10
                   Public:  52.221.245.83
                            |
                      Security Group
                       /           \
                    TCP:22       TCP:80
                      |             |
                     SSH           HTTP
```

The VPC contains the subnet:

```text
VPC
10.0.0.0/16
|
└── Public Subnet
    10.0.0.0/24
    |
    └── EC2
```

---

# 37. Why the Lab Needs an Internet Gateway

Without an Internet Gateway route:

```text
EC2
 |
 v
Route Table
 |
 X
Internet
```

The EC2 does not have a route telling it how to reach the Internet.

With:

```text
0.0.0.0/0 → Internet Gateway
```

the route becomes:

```text
EC2
 |
 v
Route Table
 |
 | 0.0.0.0/0 → IGW
 v
Internet Gateway
 |
 v
Internet
```

This is why the lab asks you to create and attach an Internet Gateway and add the default route.

---

# 38. Why Does the Route Table Need a Subnet Association?

A route table contains routing rules, but a subnet needs to know which route table it should use.

Conceptually:

```text
Route Table
|
+-- 10.0.0.0/16 → Local
+-- 0.0.0.0/0    → Internet Gateway
```

Then:

```text
Public Subnet
      |
      | associated with
      v
Route Table
```

Therefore, resources inside that subnet use those routing rules.

A route table can be associated with multiple subnets, while a subnet uses one route table at a time.

---

# 39. Why Doesn't Creating an Internet Gateway Automatically Give Internet Access?

Because different subnets may need different networking behavior.

For example:

```text
VPC
|
+-- Public Subnet
|     |
|     +-- Internet route
|
+-- Private Subnet
      |
      +-- No direct Internet Gateway route
```

This gives the architecture control over which resources have direct Internet routing.

---

# 40. AWS Tenancy

When creating a VPC, you may see:

```text
Tenancy: Default
```

Default tenancy means EC2 instances normally run on AWS's shared infrastructure rather than hardware dedicated exclusively to your account.

For most standard AWS workloads, `Default` is the normal choice.

---

# 41. Complete Mental Model

Keep this picture in your head:

```text
                         INTERNET
                            |
                            v
                    Internet Gateway
                            |
                            v
                     Route Table
                            |
                +-----------+-----------+
                |                       |
                v                       v
         Public Subnet            Private Subnet
         10.0.0.0/24              10.0.1.0/24
                |
                v
               EC2
          Private IP
          10.0.0.10
                |
          Public IP
        52.221.245.83
                |
          Security Group
           /          \
        TCP:22       TCP:80
          |             |
         SSH           HTTP
```

The responsibilities are:

```text
VPC
→ Defines the larger private address space.

Subnet
→ Divides the VPC into smaller address spaces.

IP
→ Identifies a network interface.

CIDR
→ Defines an IP address range.

Route Table
→ Decides where traffic should go.

Route
→ One routing instruction.

0.0.0.0/0
→ Any IPv4 destination.

Internet Gateway
→ Provides the VPC's connection point to the Internet.

Public IP
→ Provides an Internet-facing address for the EC2.

Port
→ Identifies a service endpoint.

TCP
→ Provides reliable transport communication.

Security Group
→ Controls allowed traffic to the EC2.

DNS
→ Converts domain names into IP addresses.
```

---

# 42. Quick Reference

| Concept          | Simple meaning                                                |
| ---------------- | ------------------------------------------------------------- |
| IP address       | Address used for network communication                        |
| IPv4             | 32-bit IP addressing system                                   |
| Private IP       | Address used inside private networks                          |
| Public IP        | Internet-facing IP address                                    |
| CIDR             | Defines an IP address range                                   |
| `/16`            | 16 fixed bits, 16 variable bits                               |
| `/24`            | 24 fixed bits, 8 variable bits                                |
| `/32`            | Exactly one IP address                                        |
| VPC              | Large virtual private network in AWS                          |
| Subnet           | Smaller network inside a VPC                                  |
| Route            | Instruction for where traffic goes                            |
| Route table      | Collection of routing instructions                            |
| `0.0.0.0/0`      | Any IPv4 destination                                          |
| Gateway          | Point used to move traffic between networks                   |
| Internet Gateway | AWS-managed connection point between VPC and Internet         |
| Port             | Identifies a service endpoint                                 |
| TCP              | Reliable transport protocol                                   |
| Port 22          | Standard SSH port                                             |
| Port 80          | Standard HTTP port                                            |
| Security Group   | Controls allowed traffic to EC2                               |
| DNS              | Converts domain names to IP addresses                         |
| Public subnet    | Typically has a route to an Internet Gateway                  |
| Private subnet   | Typically does not have a direct route to an Internet Gateway |

---

# 43. Questions and Answers From the Discussion

## Question 1: What does the CIDR block `10.0.0.0/16` mean?

It means that the CIDR range has:

```text
16 fixed bits
16 variable bits
```

Because IPv4 has 32 bits total:

```text
32 - 16 = 16
```

Therefore:

```text
2^16 = 65,536
```

IPv4 addresses are available in the range:

```text
10.0.0.0 → 10.0.255.255
```

---

## Question 2: How much of the IP is fixed in `/16`?

The first 16 bits are fixed.

The remaining 16 bits can vary.

Conceptually:

```text
10.0 | X.X
```

---

## Question 3: How many combinations does `10.0.0.0/16` support?

There are:

```text
2^16 = 65,536
```

possible IPv4 addresses in that CIDR range.

AWS reserves certain addresses inside each subnet for its own purposes, so the number of usable addresses for resources in an AWS subnet can be smaller than the total address count.

---

## Question 4: Why is it `2^16`?

Each bit can have two values:

```text
0 or 1
```

Therefore:

```text
1 bit  → 2 combinations
2 bits → 4 combinations
3 bits → 8 combinations
```

So:

```text
16 bits → 2^16 = 65,536
```

---

## Question 5: What does `10.0.0.0/24` mean?

It means:

```text
24 bits fixed
8 bits variable
```

Therefore:

```text
2^8 = 256 addresses
```

Range:

```text
10.0.0.0 → 10.0.0.255
```

---

## Question 6: What does `10.0.0.0/32` mean?

It means:

```text
32 bits fixed
0 bits variable
```

Therefore:

```text
2^0 = 1
```

It represents exactly one IP address.

For example:

```text
10.0.0.5/32
```

represents exactly:

```text
10.0.0.5
```

---

## Question 7: Does `/24` mean that 24 bits are allocated to the network and 8 bits remain?

Yes.

For:

```text
10.0.0.0/24
```

there are:

```text
24 fixed bits
8 remaining bits
```

Those remaining 8 bits provide:

```text
2^8 = 256
```

addresses.

---

## Question 8: What does "for the network" mean?

A CIDR prefix describes a range of IP addresses that share a common network portion.

For `/24`, the first 24 bits are common to the range and the last 8 bits can vary.

The easiest mental model is:

```text
/24 → 24 fixed, 8 variable
```

---

## Question 9: What is the difference between the IP range of a VPC and the IP range of a subnet?

The VPC defines the larger address space.

The subnet defines a smaller address space inside the VPC.

Example:

```text
VPC:
10.0.0.0/16

Subnet:
10.0.0.0/24
```

The subnet is a section of the VPC.

An EC2 then receives an individual private IP from the subnet.

For example:

```text
VPC
10.0.0.0/16
   |
   v
Subnet
10.0.0.0/24
   |
   v
EC2 private IP
10.0.0.10
```

---

## Question 10: Why can't an IPv4 octet exceed 255?

Each octet contains 8 bits.

An 8-bit value has:

```text
2^8 = 256
```

possible values:

```text
0 through 255
```

Therefore:

```text
256
```

is outside the valid range for an IPv4 octet.

---

## Question 11: Why use `10.0.0.0` instead of `192.168.1.1`?

`10.0.0.0` is not mandatory.

`192.168.1.1` is also a valid private IPv4 address.

AWS allows you to choose appropriate private CIDR ranges.

The lab uses:

```text
10.0.0.0/16
```

because it provides a convenient private address range for the VPC.

---

## Question 12: What should I keep in mind when designing a VPC and subnets?

Remember:

```text
1. Choose a suitable VPC CIDR.
2. Leave room for growth.
3. Keep subnets inside the VPC CIDR.
4. Do not overlap subnets.
5. Decide which subnets should be public or private.
6. Consider multiple Availability Zones.
7. Choose subnet sizes carefully.
8. Avoid overlapping CIDRs between networks that need to communicate.
```

---

## Question 13: What does "Enable auto-assign public IPv4 address" mean?

It means AWS should automatically assign a public IPv4 address to an EC2 instance when it is launched in that subnet.

The EC2 may then have:

```text
Private IP:
10.0.0.10

Public IP:
52.221.245.83
```

The private IP is used inside the VPC.

The public IP is used for Internet-facing communication.

---

## Question 14: What is an Internet Gateway?

An Internet Gateway, or IGW, is an AWS-managed virtual networking component that provides a connection point between a VPC and the Internet.

Conceptually:

```text
VPC
 |
 v
Internet Gateway
 |
 v
Internet
```

The route table must also contain an appropriate route, such as:

```text
0.0.0.0/0 → Internet Gateway
```

---

## Question 15: What is an Internet Gateway physically?

It is not a physical box that you manage.

It is an AWS-managed virtual networking component.

AWS manages the underlying physical infrastructure.

You interact with the logical networking component through AWS.

---

## Question 16: Why do we need the route `0.0.0.0/0 → Internet Gateway`?

Because creating an Internet Gateway does not automatically tell the subnet where Internet-bound traffic should go.

The route:

```text
0.0.0.0/0 → Internet Gateway
```

means:

> For IPv4 destinations that do not match a more specific route, send the traffic to the Internet Gateway.

The flow becomes:

```text
EC2
 |
 v
Route Table
 |
 | 0.0.0.0/0 → IGW
 v
Internet Gateway
 |
 v
Internet
```

---

## Question 17: What is a route table?

A route table is a collection of rules that tells network traffic where to go.

Example:

```text
Destination       Target
10.0.0.0/16       Local
0.0.0.0/0         Internet Gateway
```

Think of it as a map for network traffic.

---

## Question 18: What does `0.0.0.0/0` mean?

It means:

> Any IPv4 destination.

It is commonly used as the default or catch-all route.

---

## Question 19: What is a port?

A port identifies a service endpoint on a networked machine.

Think:

```text
IP address → Which machine?
Port       → Which service?
```

Examples:

```text
22  → SSH
80  → HTTP
443 → HTTPS
```

---

## Question 20: What does "allow SSH on port 22 and HTTP on port 80" mean?

It means configuring the Security Group to allow incoming traffic to those service ports.

For example:

```text
Protocol   Port   Purpose
TCP        22     SSH
TCP        80     HTTP
```

Port 22 is normally used by SSH.

Port 80 is normally used by HTTP web servers.

---

## Question 21: What is TCP?

TCP stands for **Transmission Control Protocol**.

TCP provides reliable transport communication between applications over a network.

It helps with:

```text
Connection
Reliable delivery
Ordering
Detecting missing data
Retransmission
```

A useful model is:

```text
IP   → Where?
TCP  → How should transport happen?
Port → Which service?
```

---

## Question 22: Can I SSH into EC2 using Windows Command Prompt?

Yes.

Modern Windows includes an OpenSSH client.

For example:

```cmd
ssh -i "my-new-key.pem" ubuntu@52.221.245.83
```

This can be run directly from Command Prompt.

---

## Question 23: Why did `chmod 400 my-new-key.pem` not work in Windows CMD?

`chmod` is normally a Linux/macOS command.

Windows Command Prompt does not normally provide `chmod`.

On Windows, `icacls` can be used to manage file permissions.

For example:

```cmd
icacls "my-new-key.pem"
```

and appropriate `icacls` commands can be used to restrict access to the private key.

---

## Question 24: Why didn't `cd desktop` work from `C:\Windows\System32`?

Because the current directory was:

```text
C:\Windows\System32
```

So:

```cmd
cd desktop
```

looked for:

```text
C:\Windows\System32\desktop
```

Your Desktop was instead:

```text
C:\Users\User\Desktop
```

So you can use:

```cmd
cd C:\Users\User\Desktop
```

---

## Question 25: Why did SSH report "Bad permissions" for my `.pem` file?

SSH requires private keys to be protected from other users.

The error indicated that another Windows account had access to:

```text
my-new-key.pem
```

SSH therefore refused to use the private key.

This is a local Windows file-permission problem, not necessarily an AWS networking problem.

---

## Question 26: Why did SSH then show `Permission denied (publickey)`?

The SSH client refused to load the private key because of its permissions:

```text
Private key
    ↓
Permissions too open
    ↓
SSH ignores the key
    ↓
AWS receives no valid private key
    ↓
Authentication fails
```

So `Permission denied (publickey)` in this situation is a consequence of the private-key permission problem.

---

## Question 27: What is DNS resolution?

DNS resolution means converting a domain name into an IP address.

For example:

```text
google.com
     ↓
DNS lookup
     ↓
IP address
```

DNS stands for **Domain Name System**.

Think of it as a phone book for domain names and IP addresses.

---

## Question 28: Why does the lab ask me to ping `google.com`?

The command:

```bash
ping google.com
```

can test several parts of connectivity.

The system first needs to resolve:

```text
google.com → IP address
```

Then it attempts to send ICMP packets toward that destination.

This can help verify DNS resolution and network connectivity, although a failed ping does not necessarily mean DNS is broken.

---

# 44. Recommended Learning Path Before the AWS Labs

Study these in this order:

```text
Phase 1: IP Fundamentals
    |
    +-- IPv4
    +-- Bits and octets
    +-- Private/Public IP
    |
    v
Phase 2: Address Ranges
    |
    +-- CIDR
    +-- /16
    +-- /24
    +-- /32
    +-- Network and host concepts
    |
    v
Phase 3: AWS Network Structure
    |
    +-- VPC
    +-- Subnet
    +-- Availability Zone
    |
    v
Phase 4: Traffic Movement
    |
    +-- Routing
    +-- Route
    +-- Route Table
    +-- Default route
    +-- Gateway
    +-- Internet Gateway
    |
    v
Phase 5: EC2 Networking
    |
    +-- Private IP
    +-- Public IP
    +-- Auto-assign public IPv4
    +-- Ports
    +-- TCP
    +-- Security Groups
    |
    v
Phase 6: Connectivity
    |
    +-- DNS
    +-- DNS resolution
    +-- Ping
    +-- SSH
    +-- HTTP
```

---

# 45. Final Mental Checklist

Before starting the VPC and EC2 labs, you should be able to answer these questions without looking them up:

```text
What is an IP address?
What is IPv4?
Why does an IPv4 octet stop at 255?
What does /16 mean?
What does /24 mean?
What does /32 mean?
Why is 2^8 equal to 256?
What is a private IP?
What is a public IP?
What is a VPC?
What is a subnet?
How does a subnet fit inside a VPC?
What is routing?
What is a route?
What is a route table?
What does 0.0.0.0/0 mean?
What is a gateway?
What is an Internet Gateway?
Why does a route table need a route to an Internet Gateway?
What makes a subnet public?
What is an EC2 private IP?
What is an EC2 public IP?
What is a port?
Why is port 22 used for SSH?
Why is port 80 used for HTTP?
What is TCP?
What is a Security Group?
What does a Security Group rule do?
What is DNS?
What is DNS resolution?
What does ping test?
```

---

# 46. One-Page Mental Model

The entire lab can be understood with this model:

```text
                         INTERNET
                            |
                            |
                    Internet Gateway
                            |
                            |
                 Route: 0.0.0.0/0 → IGW
                            |
                            v
                    +---------------+
                    |  Route Table  |
                    +---------------+
                            |
                            v
                    +---------------+
                    | Public Subnet |
                    | 10.0.0.0/24   |
                    +---------------+
                            |
                            v
                    +---------------+
                    |     EC2       |
                    |               |
                    | Private IP    |
                    | 10.0.0.10     |
                    |               |
                    | Public IP     |
                    | 52.221.245.83 |
                    +---------------+
                            |
                    +---------------+
                    | Security Group|
                    |               |
                    | TCP :22 → SSH |
                    | TCP :80 → HTTP|
                    +---------------+
```

And the hierarchy is:

```text
VPC
  ↓
Subnet
  ↓
EC2
  ↓
Private IP

EC2
  ↓
Public IP
  ↓
Internet

Traffic
  ↓
Route Table
  ↓
Internet Gateway
  ↓
Internet

Security Group
  ↓
Controls which traffic is allowed

DNS
  ↓
Converts domain names to IP addresses

TCP
  ↓
Provides reliable transport

Port
  ↓
Identifies the service
```

The central idea is:

> **A VPC defines the network space. A subnet divides it. An EC2 uses an IP from the subnet. A route table decides where traffic goes. An Internet Gateway provides the Internet connection point. A Security Group controls allowed traffic. TCP and ports identify how traffic reaches a service. DNS translates human-friendly names into IP addresses.**

```
```

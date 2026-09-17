# AWS Networking and Bastion Server — Beginner Notes

## 1. What is IPv4?

IPv4 means **Internet Protocol version 4**.

It is a system used to identify devices or network interfaces using a **32-bit address**.

Example:

```text
192.168.1.10
```

An IPv4 address contains four numbers called **octets**:

```text
192 . 168 . 1 . 10
 8     8    8    8  bits
```

Each octet can contain values from:

```text
0 to 255
```

Why?

```text
2^8 = 256
```

So each octet has 256 possible values.

Therefore:

```text
4 octets × 8 bits
= 32 bits
```

That is why IPv4 uses 32 bits.

---

# 2. What is IPv6?

IPv6 means **Internet Protocol version 6**.

IPv6 uses **128 bits** for an address.

Example:

```text
2001:0db8:85a3:0000:0000:8a2e:0370:7334
```

An IPv6 address contains eight hexadecimal groups.

Each group contains four hexadecimal digits.

One hexadecimal digit represents:

```text
4 bits
```

Therefore:

```text
8 groups × 4 hexadecimal digits × 4 bits
= 128 bits
```

So:

```text
IPv4 → 32 bits
IPv6 → 128 bits
```

IPv6 was designed with a much larger address space.

```text
IPv4:
2^32 ≈ 4.3 billion addresses

IPv6:
2^128 ≈ 3.4 × 10^38 addresses
```

The important mathematical idea is:

> More bits create exponentially more possible combinations.

128 bits is only four times as many bits as 32 bits, but the address space is enormously larger.

---

# 3. How can I know IPv4 is 32 bits from its notation?

Consider:

```text
10.0.0.1
```

There are four octets:

```text
10 | 0 | 0 | 1
```

Each octet represents 8 bits.

Therefore:

```text
8 + 8 + 8 + 8 = 32 bits
```

The reason each octet is 8 bits is:

```text
0–255
```

contains:

```text
256 values
```

and:

```text
256 = 2^8
```

Therefore, one octet represents 8 bits.

---

# 4. How can I intuitively understand the IPv6 128-bit size?

Consider:

```text
2001:0db8:85a3:0000:0000:8a2e:0370:7334
```

There are:

```text
8 groups
```

Each group contains:

```text
4 hexadecimal digits
```

Each hexadecimal digit represents 4 bits.

Therefore:

```text
8 × 4 × 4
= 128 bits
```

Another useful fact:

```text
1 hexadecimal digit = 4 bits
2 hexadecimal digits = 8 bits
```

That is why hexadecimal notation is convenient for representing binary addresses.

---

# 5. What does `/16` mean in a CIDR address?

Consider:

```text
10.0.0.0/16
```

IPv4 has 32 total bits.

The `/16` means:

```text
16 bits → network portion
16 bits → host portion
```

Visually:

```text
Network              Host
<------16------>     <------16------>
11111111.11111111.00000000.00000000
```

The number after `/` tells you how many bits belong to the network portion.

Examples:

```text
/8   → 8 network bits
/16  → 16 network bits
/24  → 24 network bits
/32  → 32 network bits
```

---

# 6. How many combinations can `10.0.0.0/16` create?

IPv4 has 32 bits.

A `/16` network leaves:

```text
32 - 16 = 16 host bits
```

Each bit has two possibilities:

```text
0 or 1
```

Therefore:

```text
2^16
= 65,536
```

So:

```text
10.0.0.0/16
```

contains:

```text
65,536 total IPv4 addresses
```

---

# 7. How do I intuitively understand the `65,536` calculation?

This is easier if you think in octets.

For:

```text
10.0.0.0/16
```

the first two octets are the network portion:

```text
10 . 0 . X . Y
```

The last two octets are available to vary.

Each octet has:

```text
256 combinations
```

Therefore:

```text
X → 256 choices
Y → 256 choices
```

For every value of `X`, there are 256 possible values of `Y`.

Therefore:

```text
256 × 256
= 65,536
```

For example:

```text
X = 0
    Y = 0 through 255
    → 256 combinations

X = 1
    Y = 0 through 255
    → 256 combinations

X = 2
    Y = 0 through 255
    → 256 combinations

...

X = 255
    Y = 0 through 255
    → 256 combinations
```

There are 256 groups:

```text
256 groups × 256 combinations
= 65,536
```

This is the same as:

```text
2^8 × 2^8
= 2^16
= 65,536
```

The key rule is:

> When independent positions can each have multiple choices, multiply their choices.

---

# 8. How many combinations does `10.0.1.0/24` have?

A `/24` leaves:

```text
32 - 24
= 8 host bits
```

Therefore:

```text
2^8
= 256
```

There are 256 total addresses.

The range is:

```text
10.0.1.0
through
10.0.1.255
```

In an AWS VPC subnet, AWS reserves five IP addresses, so the number available for resources is:

```text
256 - 5
= 251
```

Do not confuse this with general IPv4 subnet calculations, where the traditional network and broadcast reservations are different.

---

# 9. What about `10.0.1.0/16`?

A `/16` leaves:

```text
32 - 16
= 16 host bits
```

Therefore:

```text
2^16
= 65,536 addresses
```

However, there is an important detail.

```text
10.0.1.0/16
```

is not the canonical network address for that `/16`.

The actual `/16` network is:

```text
10.0.0.0/16
```

The address:

```text
10.0.1.0
```

is simply an address inside that network.

The range is:

```text
10.0.0.0
through
10.0.255.255
```

---

# 10. General CIDR formula

For IPv4:

```text
Number of addresses = 2^(32 - prefix length)
```

Examples:

```text
/16:
2^(32-16)
= 2^16
= 65,536

/24:
2^(32-24)
= 2^8
= 256

/32:
2^(32-32)
= 2^0
= 1
```

A useful mental model is:

```text
IPv4 address = 32 bits

/16
│
├── 16 fixed network bits
└── 16 variable host bits
```

---

# 11. What is the difference between a public and private route table?

A route table is a collection of routing rules.

For example:

```text
Destination       Target

10.0.0.0/16       local
0.0.0.0/0         Internet Gateway
```

A route table is not inherently called public or private by AWS.

The terms usually describe how the subnet uses the route table.

## Public subnet

A subnet is commonly considered public when its route table contains a route to an Internet Gateway.

Example:

```text
0.0.0.0/0 → Internet Gateway
```

Conceptually:

```text
Public EC2
    |
    v
Route Table
    |
    | 0.0.0.0/0
    v
Internet Gateway
    |
    v
Internet
```

## Private subnet

A private subnet normally does not have a direct route from the subnet to an Internet Gateway for its instances.

It may use a NAT Gateway for outbound Internet access.

```text
Private EC2
    |
    v
NAT Gateway
    |
    v
Internet Gateway
    |
    v
Internet
```

---

# 12. What is the purpose of `0.0.0.0/0 → my-IGW`?

The rule:

```text
0.0.0.0/0 → my-IGW
```

is the **default IPv4 route**.

`0.0.0.0/0` means:

> Any IPv4 destination.

It does not mean that the EC2 sends a request to an address called `0.0.0.0`.

Instead, it means:

> If no more specific route matches the destination, use the Internet Gateway.

For example, suppose an EC2 wants to communicate with:

```text
8.8.8.8
```

The route table checks the destination.

If there is no more specific route for `8.8.8.8`, it uses:

```text
0.0.0.0/0 → Internet Gateway
```

The path becomes:

```text
EC2
 ↓
Route Table
 ↓
0.0.0.0/0
 ↓
Internet Gateway
 ↓
Internet
 ↓
8.8.8.8
```

---

# 13. Analogy for a route table

Think of a route table as a road instruction board.

Suppose you are inside a city.

The board says:

```text
Local destinations → Local roads

Everything else → Highway
```

You do not travel to a place called "everything else."

Instead, the rule tells you what road to use when the destination does not match a more specific rule.

That is what:

```text
0.0.0.0/0
```

does.

It is the default route.

---

# 14. Why would an EC2 want to reach `8.8.8.8`?

An EC2 instance does not inherently need to communicate with `8.8.8.8`.

`8.8.8.8` is Google's public DNS server and is commonly used as a connectivity example.

An EC2 might need Internet access for:

```text
apt update
Downloading packages
GitHub
External APIs
Container registries
Software repositories
Other Internet services
```

You can also deliberately test Internet connectivity with:

```bash
ping 8.8.8.8
```

---

# 15. Is `ping google.com` the same as `ping 8.8.8.8`?

Not exactly.

When you run:

```bash
ping google.com
```

your machine first needs to resolve:

```text
google.com
      ↓
IP address
```

This is called **DNS resolution**.

Then it sends traffic to the resolved IP address.

When you run:

```bash
ping 8.8.8.8
```

you already provided the IP address.

Therefore, DNS resolution is not needed.

Conceptually:

```text
ping google.com

google.com
    ↓
DNS resolution
    ↓
IP address
    ↓
Network communication
```

Whereas:

```text
ping 8.8.8.8

8.8.8.8
    ↓
Network communication
```

Therefore:

```text
ping 8.8.8.8
```

can help test Internet connectivity without involving DNS.

---

# 16. When I ping `google.com`, does the request go outside the VPC?

After DNS resolution, suppose Google resolves to an IP address outside your VPC.

The route table examines that destination IP.

If the destination does not match a more specific VPC route, the default route is used:

```text
0.0.0.0/0 → Internet Gateway
```

So the important idea is:

> Routing is based on the destination IP address.

It is not exactly correct to say:

> "The IP is not available inside the VPC."

A better explanation is:

> The destination IP is outside the VPC's local network routes, so the default route handles the traffic.

---

# 17. What happens when I SSH into EC2?

SSH is **Secure Shell**.

It is commonly used to remotely access a Linux server.

SSH normally uses:

```text
TCP port 22
```

When you SSH from your computer to a public EC2 instance:

```text
Your Computer
      |
      | SSH
      | TCP 22
      v
   Internet
      |
      v
Internet Gateway
      |
      v
EC2 Public IP
      |
      v
EC2 Instance
```

This is different from EC2 making an outbound request.

### Outbound

```text
EC2 → Internet
```

### Inbound

```text
Your Computer → EC2
```

---

# 18. What does "Allow SSH and all outbound traffic" mean?

This usually refers to **Security Group rules**.

A Security Group acts as a virtual firewall for an EC2 instance.

There are two major directions:

```text
Inbound
Outbound
```

## Inbound

Inbound means:

> Traffic coming into the EC2 instance.

For SSH:

```text
Protocol: TCP
Port: 22
Source: allowed IP/network
```

This allows an SSH connection to the server.

## Outbound

Outbound means:

> Traffic leaving the EC2 instance.

If the rule says:

```text
All traffic
Destination: 0.0.0.0/0
```

it means the EC2 is allowed to send IPv4 traffic to any IPv4 destination.

However, the Security Group does not create an Internet connection.

The route table and network infrastructure must also provide a valid path.

---

# 19. What is `0.0.0.0/0` in a Security Group?

In an IPv4 Security Group rule:

```text
0.0.0.0/0
```

means:

> Any IPv4 address.

For example:

```text
Destination: 0.0.0.0/0
```

means:

```text
EC2 → any IPv4 destination
```

Similarly:

```text
::/0
```

means:

> Any IPv6 address.

So:

```text
0.0.0.0/0 → all IPv4 addresses
::/0      → all IPv6 addresses
```

---

# 20. How can Security Group rules be made more restrictive?

Instead of:

```text
0.0.0.0/0
```

you can specify a particular destination.

For example:

```text
8.8.8.8/32
```

means exactly one IPv4 address:

```text
8.8.8.8
```

Why?

Because `/32` leaves:

```text
32 - 32 = 0
```

variable bits.

Therefore:

```text
2^0 = 1 address
```

Another example:

```text
10.0.2.0/24
```

allows the entire:

```text
10.0.2.0
through
10.0.2.255
```

network.

You can also restrict:

```text
Protocol
Port
Destination
```

For example:

```text
Protocol: TCP
Port: 443
Destination: 10.0.2.50/32
```

Conceptually:

> Allow HTTPS traffic only to `10.0.2.50`.

This follows the principle of **least privilege**.

Allow only the traffic that is actually required.

---

# 21. What about `::/0`?

`::/0` is the IPv6 equivalent of:

```text
0.0.0.0/0
```

Comparison:

```text
0.0.0.0/0 → all IPv4 addresses

::/0      → all IPv6 addresses
```

If your AWS VPC does not use IPv6, you normally do not need to design IPv6 rules for this particular lab.

---

# 22. What is a packet?

A **packet** is a small unit of data sent across a network.

Conceptually, a packet contains information such as:

```text
Source IP
Destination IP
Protocol information
Data
```

For example:

```text
Your Computer
     |
     | Packet
     | Source: your IP
     | Destination: EC2 IP
     v
Internet
```

The network uses the destination information to determine where the packet should go.

---

# 23. What is a router?

A router connects networks and decides where packets should be forwarded.

Conceptually:

```text
Network A
    |
    v
 Router
    |
    +----> Network B
    |
    +----> Network C
```

A router examines the packet's destination and chooses an appropriate route.

An AWS route table provides the routing rules used within the VPC networking architecture.

---

# 24. What is a host?

A **host** is a device or network interface that participates in network communication.

Examples include:

```text
Laptop
Desktop
EC2 instance
Server
Phone
```

In CIDR calculations, "host bits" refer to the part of an IP address that can vary within the network.

For:

```text
10.0.0.0/16
```

there are:

```text
16 network bits
16 host bits
```

The host bits provide:

```text
2^16 = 65,536
```

possible addresses.

---

# 25. What is an AWS VPC?

VPC means:

**Virtual Private Cloud**

It is a logically isolated network environment inside AWS.

For example:

```text
VPC
10.0.0.0/16
```

can contain multiple subnets.

Example:

```text
VPC: 10.0.0.0/16
│
├── Public Subnet
│   10.0.1.0/24
│
└── Private Subnet
    10.0.2.0/24
```

The `/16` VPC provides the larger address space.

The `/24` subnets divide that space into smaller networks.

---

# 26. AWS Lab: Deploying a Bastion Server in a Public Subnet

The lab creates the following components:

```text
VPC
my-vpc
10.0.0.0/16

        |
        v

Public Subnet
public-subnet
10.0.1.0/24

        |
        v

Route Table
public-route-table

        |
        | 0.0.0.0/0 → my-IGW
        v

Internet Gateway
my-IGW

        |
        v

EC2
ec2-instance-1
```

The lab also creates a Security Group and an SSH key pair.

---

# 27. What is a bastion server?

A **bastion server** is a controlled entry point into a private network.

A typical architecture looks like:

```text
Your Computer
      |
      | SSH
      v
┌─────────────────┐
│ Bastion Server  │
│ Public Subnet   │
│ Public IP       │
└────────┬────────┘
         |
         | SSH
         v
┌─────────────────┐
│ Private Server   │
│ Private Subnet   │
│ No Public IP    │
└─────────────────┘
```

The idea is that you do not directly expose the private server to the Internet.

Instead:

```text
Internet
   |
   v
Bastion
   |
   v
Private Server
```

The bastion provides the controlled entry point.

---

# 28. Where is the bastion server in this lab?

In this particular lab:

```text
ec2-instance-1
```

is being used as the bastion server.

It is placed inside:

```text
Public Subnet
10.0.1.0/24
```

It receives a public IP address.

You connect to it using SSH.

The architecture is:

```text
Your Computer
      |
      | SSH
      v
Internet
      |
      v
Internet Gateway
      |
      v
Public Subnet
      |
      v
┌────────────────────┐
│ ec2-instance-1     │
│                    │
│ Bastion Server     │
│ Public IP          │
└────────────────────┘
```

---

# 29. Does this lab have a private server behind the bastion?

No.

This is an important detail.

The lab demonstrates the **bastion server itself**, but it does not create the complete bastion architecture.

There is no second private EC2 instance in the described lab.

The current lab is:

```text
Your Computer
      |
      | SSH
      v
Bastion EC2
Public Subnet
```

A complete bastion lab would look like:

```text
Your Computer
      |
      | SSH
      v
Bastion EC2
Public Subnet
      |
      | SSH using private IP
      v
Private EC2
Private Subnet
```

So the current lab teaches the public entry point.

A later lab could extend it into the complete jump-host architecture.

---

# 30. What is the relationship between Public Subnet and Bastion Server?

A bastion server is normally placed in a public subnet because it needs to be reachable from the administrator's network.

For direct Internet connectivity, the relevant pieces are:

```text
Public Subnet
     |
     v
Route Table
     |
     | 0.0.0.0/0
     v
Internet Gateway
```

The EC2 also needs appropriate addressing and Security Group rules.

Therefore, simply naming a subnet "public" does not make it public.

The networking configuration determines its behavior.

---

# 31. AWS Lab Security Group

The lab uses:

```text
Security Group:
security-group-1
```

The inbound SSH rule allows:

```text
Protocol: TCP
Port: 22
Source: 0.0.0.0/0
```

This means:

> Any IPv4 source is allowed to attempt an SSH connection to port 22.

This is broad.

For a real production environment, SSH access should normally be restricted to trusted sources where possible.

For example:

```text
YOUR_PUBLIC_IP/32
```

means:

> Only this one public IPv4 address.

The lab uses `0.0.0.0/0` for simplicity and learning.

---

# 32. AWS Lab outbound Security Group rule

The lab allows:

```text
Outbound:
All traffic
Destination:
0.0.0.0/0
```

This means the EC2 can initiate IPv4 traffic toward any IPv4 destination, subject to the rest of the network configuration.

A more restrictive design might allow only required destinations.

For example:

```text
TCP
443
10.0.2.50/32
```

would permit HTTPS traffic to one specific IPv4 address.

However, you should not blindly replace `0.0.0.0/0`.

First determine what the server actually needs to communicate with.

---

# 33. How does the bastion EC2 get Internet access?

The simplified path is:

```text
Bastion EC2
     |
     v
Public Subnet
     |
     v
Route Table
     |
     | 0.0.0.0/0
     v
Internet Gateway
     |
     v
Internet
```

For inbound SSH:

```text
Your Computer
     |
     v
Internet
     |
     v
Internet Gateway
     |
     v
Public EC2
```

The two directions should be kept conceptually separate.

```text
Inbound:
Your Computer → EC2

Outbound:
EC2 → Internet
```

---

# 34. What is the purpose of `aws configure`?

`aws configure` is used to configure the AWS CLI with credentials and default settings.

It can configure things such as:

```text
AWS Access Key ID
AWS Secret Access Key
Default Region
Output Format
```

For example:

```bash
aws configure
```

The AWS CLI can then use these settings when communicating with AWS services.

For example:

```bash
aws s3 ls
```

The CLI needs appropriate AWS credentials and permissions to perform the operation.

---

# 35. What is a `.sh` file?

A `.sh` file is commonly a **shell script**.

Example:

```text
vpc.sh
```

It contains commands that a shell can execute.

For example:

```bash
#!/bin/bash

echo "Creating VPC"
aws ec2 create-vpc ...
```

Instead of manually typing each command, you can execute the script.

---

# 36. What is Bash scripting?

**Bash scripting** means writing commands in a file so Bash can execute them automatically.

For example:

```bash
#!/bin/bash

echo "Hello"
mkdir test
cd test
touch example.txt
```

Bash can execute these commands sequentially.

This is useful in DevOps, MLOps, and cloud environments because infrastructure often requires many repetitive commands.

---

# 37. What does `#!/bin/bash` mean?

This line:

```bash
#!/bin/bash
```

is called a **shebang**.

It tells the operating system which interpreter should execute the script.

Here:

```text
#! → interpreter declaration
/bin/bash → Bash interpreter
```

So:

```bash
#!/bin/bash
```

means:

> Execute this script using Bash.

---

# 38. What does `chmod +x` mean?

`chmod` means:

```text
change mode
```

It changes file permissions on Unix/Linux systems.

This:

```bash
chmod +x script.sh
```

adds the executable permission.

Then you can run:

```bash
./script.sh
```

Without executable permission, the shell may not allow the file to be executed directly.

---

# 39. What does `chmod 400` mean?

This command:

```bash
chmod 400 new-key-pair.pem
```

changes the file permissions.

The number:

```text
400
```

can be understood as:

```text
Owner   Group   Others
  4       0       0
```

The value `4` means:

```text
read
```

So:

```text
400
```

means:

```text
Owner  → read
Group  → no permissions
Others → no permissions
```

This is commonly used for private SSH keys.

Conceptually:

```text
Owner   → R
Group   → -
Others  → -
```

The goal is to prevent other users from reading the private key.

---

# 40. Why didn't `chmod` work in PowerShell?

You initially ran:

```powershell
PS C:\Users\User\Desktop> chmod 400 "new-key-pair.pem"
```

PowerShell returned:

```text
chmod : The term 'chmod' is not recognized
```

The reason is that `chmod` is a Unix/Linux command.

Normal Windows PowerShell does not provide `chmod`.

Therefore:

```text
PowerShell
   |
   └── chmod → not available by default
```

Whereas:

```text
Linux / WSL / Git Bash
   |
   └── chmod → available
```

---

# 41. How can `chmod` be used on Windows?

You need a Unix-like environment such as:

```text
WSL
Git Bash
Linux VM
Linux server
```

For example, inside WSL:

```bash
chmod 400 new-key-pair.pem
```

However, your environment was not using the usual WSL mount path.

---

# 42. Why didn't `/mnt/c/Users/User/Desktop` work?

You entered:

```bash
cd /mnt/c/Users/User/Desktop
```

and received:

```text
No such file or directory
```

Your shell showed:

```text
Akash-desktop-ryzen7:/mnt/host/c/Windows/system32#
```

This indicates that your environment exposes the Windows `C:` drive through:

```text
/mnt/host/c/
```

rather than:

```text
/mnt/c/
```

Therefore, the appropriate path in that environment is:

```bash
cd /mnt/host/c/Users/User/Desktop
```

You can check the directory with:

```bash
ls /mnt/host/c/Users/User/Desktop
```

Then:

```bash
chmod 400 new-key-pair.pem
```

---

# 43. How do Windows and the Linux shell map paths?

In your environment:

```text
Windows                         Linux shell

C:\                             /mnt/host/c/

C:\Users\User\                  /mnt/host/c/Users/User/

C:\Users\User\Desktop\          /mnt/host/c/Users/User/Desktop/
```

Therefore:

```bash
cd /mnt/host/c/Users/User/Desktop
```

takes you to the Windows Desktop.

Then:

```bash
ls
```

should show the files on your Windows Desktop.

---

# 44. What if I want to stay in PowerShell?

You do not necessarily need `chmod`.

Windows provides its own file-permission system.

You can first try SSH directly:

```powershell
ssh -i ".\new-key-pair.pem" ubuntu@YOUR_EC2_PUBLIC_IP
```

If Windows OpenSSH complains about private-key permissions, Windows permissions can be modified using:

```powershell
icacls ".\new-key-pair.pem" /inheritance:r
```

and:

```powershell
icacls ".\new-key-pair.pem" /grant:r "$($env:USERNAME):(R)"
```

Then retry SSH.

---

# 45. Complete mental model of the lab

The entire lab can be understood as several layers.

```text
                 YOUR COMPUTER
                      |
                      | SSH
                      | TCP 22
                      v
                   INTERNET
                      |
                      v
              INTERNET GATEWAY
                   my-IGW
                      |
                      v
              PUBLIC ROUTE TABLE
                      |
              0.0.0.0/0 → IGW
                      |
                      v
              PUBLIC SUBNET
               10.0.1.0/24
                      |
                      v
              ┌────────────────┐
              │ ec2-instance-1 │
              │                │
              │ Bastion Server │
              │                │
              │ Public IP      │
              └────────────────┘
                      |
                      |
               Security Group
                      |
             TCP 22 inbound
                      |
             All outbound
```

The VPC surrounding this architecture is:

```text
VPC
10.0.0.0/16
```

The public subnet is a smaller network inside the VPC:

```text
VPC
10.0.0.0/16
      |
      +---- Public Subnet
            10.0.1.0/24
```

---

# 46. The most important concepts to remember

## IP address

Identifies a network interface.

```text
192.168.1.10
```

## CIDR

Defines a network and how many bits are fixed.

```text
10.0.0.0/16
```

## Network bits

The fixed portion of the address.

```text
/16 → 16 network bits
```

## Host bits

The variable portion.

```text
/16 → 16 host bits
```

## Route table

Decides where packets should go.

```text
Destination → Target
```

## `0.0.0.0/0`

Matches any IPv4 destination.

```text
All IPv4 addresses
```

## `::/0`

Matches any IPv6 destination.

```text
All IPv6 addresses
```

## Internet Gateway

Provides the VPC's Internet connectivity path when routing and addressing are configured appropriately.

## Security Group

Acts as a stateful virtual firewall for resources such as EC2.

## SSH

A secure protocol for remotely accessing servers.

```text
TCP 22
```

## Bastion Server

A controlled public entry point used to reach private resources.

## `chmod 400`

On Linux/Unix:

```text
Owner → read
Group → none
Others → none
```

It is commonly used to protect private SSH keys.

---

# 47. One final picture

```text
                     INTERNET
                         |
                         |
                  Your Computer
                         |
                         | SSH / TCP 22
                         |
                         v
                ┌─────────────────┐
                │ Internet        │
                │ Gateway         │
                │ my-IGW          │
                └────────┬────────┘
                         |
                         |
                Route Table
                public-route-table
                         |
                   0.0.0.0/0
                         |
                         v
                ┌─────────────────┐
                │ Public Subnet   │
                │ 10.0.1.0/24     │
                │                 │
                │ ┌─────────────┐ │
                │ │ EC2         │ │
                │ │ Bastion     │ │
                │ │ Server      │ │
                │ └─────────────┘ │
                └─────────────────┘
                         |
                         |
                    VPC
                 10.0.0.0/16
```

The central idea is:

```text
VPC
 ↓
Subnet
 ↓
Route Table
 ↓
Internet Gateway
 ↓
Internet

Security Group
 ↓
Controls allowed traffic

EC2
 ↓
Server

Bastion
 ↓
Controlled entry point
```

Once these relationships are clear, AWS networking labs become much easier to understand because each AWS component has a specific role.

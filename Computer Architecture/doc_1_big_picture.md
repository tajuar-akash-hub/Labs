Think of **computer architecture** as:

> **How a computer is organized internally so it can store data, process instructions, and communicate with other components.**


---

# 1. The Big Picture

A computer can be simplified into these major parts:

```text
                    COMPUTER
                       |
        +--------------+--------------+
        |              |              |
       CPU            RAM          Storage
        |              |              |
   Processing      Temporary      Long-term
                   memory          memory
        |
   +----+----+
   |         |
Registers    ALU
   |
Control Unit
```

And there are other important components:

```text
CPU
RAM
Storage
GPU
Motherboard
NIC
Input/Output devices
```

The most important thing to understand first is:

> **CPU processes instructions, RAM temporarily holds data/instructions, and storage permanently holds data.**

---

# 2. What Is a CPU?

CPU stands for:

**Central Processing Unit**

It is the main processing unit of a computer.

For example, when you write:

```python
x = 10 + 20
```

eventually the CPU has to perform operations corresponding to this computation.

A simplified CPU looks like:

```text
                 CPU
                  |
        +---------+---------+
        |                   |
       ALU             Control Unit
        |
   Calculations
        |
    Registers
```

---

# 3. ALU

ALU stands for:

**Arithmetic Logic Unit**

It performs operations such as:

```text
10 + 20
10 - 5
5 × 4
10 > 5
A AND B
A OR B
```

So:

> **ALU = part of the CPU that performs arithmetic and logical operations.**

---

# 4. Control Unit

The **Control Unit (CU)** coordinates what the CPU should do.

For example:

```text
Get instruction
      ↓
Understand instruction
      ↓
Get required data
      ↓
Perform operation
      ↓
Store result
```

You can think of it as the **traffic controller inside the CPU**.

---

# 5. Registers

Registers are very small, very fast storage locations **inside the CPU**.

For example:

```text
CPU
 |
 +-- Register
 +-- Register
 +-- Register
 +-- Register
```

Suppose the CPU needs to calculate:

```text
10 + 20
```

It might conceptually do:

```text
Register 1 ← 10
Register 2 ← 20

ALU:
Register 1 + Register 2

Register 3 ← 30
```

Registers are much faster to access than RAM.

---

# 6. RAM

RAM stands for:

**Random Access Memory**

RAM is the computer's **working memory**.

Suppose you run:

```python
python app.py
```

The program and the data it needs are loaded from storage into RAM.

Conceptually:

```text
SSD
 |
 | Load program
 ↓
RAM
 |
 | CPU accesses it
 ↓
CPU
```

RAM is much larger than registers but slower.

---

# 7. Storage

Storage means things like:

* SSD
* HDD
* NVMe SSD

Storage keeps information even after the computer is turned off.

For example:

```text
SSD
 |
 +-- Windows
 +-- Python
 +-- Your projects
 +-- Docker images
 +-- Documents
```

The important distinction is:

| Component | Purpose              | Keeps data after shutdown? |
| --------- | -------------------- | -------------------------- |
| Register  | CPU's immediate data | No                         |
| RAM       | Working memory       | No                         |
| SSD/HDD   | Long-term storage    | Yes                        |

---

# 8. The Memory Hierarchy

One of the most important concepts in computer architecture is:

> **The closer memory is to the CPU, the faster and usually smaller it is.**

A simplified hierarchy:

```text
             FASTEST
                ↑
          +-----------+
          | Registers |
          +-----------+
                |
          +-----------+
          |   Cache   |
          +-----------+
                |
          +-----------+
          |    RAM    |
          +-----------+
                |
          +-----------+
          |    SSD    |
          +-----------+
                |
          +-----------+
          |    HDD    |
          +-----------+
                ↓
             SLOWEST
```

Generally:

```text
Registers > Cache > RAM > SSD > HDD
```

in access speed.

But the trade-off is that faster memory tends to be **smaller and more expensive per byte**.

---

# 9. CPU Cache

You will hear about **L1, L2, and L3 cache**.

They are small, fast memory areas associated with the CPU.

```text
CPU
 |
 +-- L1 Cache
 |
 +-- L2 Cache
 |
 +-- L3 Cache
 |
 +-- Registers
```

A simplified idea:

```text
CPU
 ↓
Check registers
 ↓
Check L1
 ↓
Check L2
 ↓
Check L3
 ↓
Check RAM
 ↓
Check storage
```

The exact behavior is more complicated, but this gives you the basic intuition.

---

# 10. What Is a CPU Core?

Modern CPUs have multiple **cores**.

For example:

```text
CPU
 |
 +-- Core 1
 +-- Core 2
 +-- Core 3
 +-- Core 4
 +-- Core 5
 +-- Core 6
 +-- Core 7
 +-- Core 8
```

A core is essentially an independent processing unit capable of executing instructions.

So an **8-core CPU** can work on multiple streams of instructions concurrently.

This is why you can run things like:

```text
Browser
Docker
VS Code
Python
Database
Kubernetes
```

at the same time.

---

# 11. What Is a Thread?

A thread is a sequence of instructions that can be executed by a CPU core.

For example:

```text
Core 1
 ├── Thread A
 └── Thread B
```

Technologies such as SMT/Hyper-Threading allow one physical core to maintain multiple hardware threads.

So you might see:

```text
8 cores
16 threads
```

This does **not** mean you have 16 physical cores.

It means:

```text
Physical cores = 8
Logical/hardware threads = 16
```

---

# 12. Instruction

A CPU doesn't directly understand Python, JavaScript, or C++.

Ultimately, software must be translated into **machine instructions** that the CPU's instruction set supports.

Conceptually:

```text
Python
   ↓
Interpreter/compiler/runtime
   ↓
Machine instructions
   ↓
CPU
```

A CPU might execute instructions conceptually like:

```text
LOAD
ADD
STORE
COMPARE
JUMP
```

---

# 13. Instruction Set Architecture — ISA

This is a very important term.

**ISA = Instruction Set Architecture**

It defines the instructions and programmer-visible behavior that a CPU architecture supports.

Examples include:

* **x86-64**
* **ARM64 / AArch64**
* **RISC-V**

For example:

```text
Intel/AMD CPUs
       ↓
    x86-64

Apple Silicon
       ↓
     ARM64

Many phones
       ↓
     ARM64
```

This is why software sometimes has different versions:

```text
program-x86_64
program-arm64
```

They target different CPU architectures.

---

# 14. What Does 32-bit vs 64-bit Mean?

This is commonly misunderstood.

A 64-bit CPU does **not** mean:

> "Each RAM cell stores 64 bits."

That's incorrect.

Instead, **64-bit** broadly refers to the CPU's architecture and the size of important processor operations/registers/addressing capabilities.

For example:

```text
32-bit register

[xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx]
       32 bits
```

versus:

```text
64-bit register

[xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx]
                         64 bits
```

A 64-bit CPU can work with 64-bit values directly in its registers and supports a much larger address space than traditional 32-bit systems.

And importantly:

> **RAM does not need to be "64-bit RAM" just because the CPU is 64-bit.**

---

# 15. Bits and Bytes

You need this before going deeper.

```text
1 bit = 0 or 1

8 bits = 1 byte
```

For example:

```text
10110101
```

is 8 bits = 1 byte.

Common units:

```text
1 byte       = 8 bits
1 KB         ≈ 1,000 bytes
1 MB         ≈ 1,000 KB
1 GB         ≈ 1,000 MB
1 TB         ≈ 1,000 GB
```

In computing, binary-based definitions are also commonly used, where:

```text
1 KiB = 1024 bytes
1 MiB = 1024 KiB
1 GiB = 1024 MiB
```

---

# 16. How CPU + RAM Work Together

Imagine you run:

```python
result = 10 + 20
```

A simplified version is:

```text
             SSD
              |
       Load program
              ↓
             RAM
              |
       CPU fetches instructions
              ↓
             CPU
              |
       Registers hold values
              ↓
             ALU
              |
           10 + 20
              ↓
             30
              |
           Register
              ↓
             RAM
```

The actual hardware process is much more sophisticated, but this is the correct mental model for a beginner.

---

# 17. Fetch → Decode → Execute

One of the most fundamental CPU concepts is the **instruction cycle**.

```text
       FETCH
         ↓
       DECODE
         ↓
      EXECUTE
         ↓
       REPEAT
```

### Fetch

CPU gets the next instruction.

### Decode

CPU determines what the instruction means.

### Execute

CPU performs the operation.

For example:

```text
Instruction:
ADD R1, R2
```

Conceptually:

```text
Fetch instruction
       ↓
Understand "ADD"
       ↓
Read R1 and R2
       ↓
ALU performs addition
       ↓
Store result
```

The CPU performs this process extremely rapidly.

---

# 18. Motherboard

The motherboard connects the major components.

```text
             Motherboard
                  |
      +-----------+-----------+
      |           |           |
     CPU         RAM        Storage
      |
     GPU
      |
     NIC
      |
    USB/I/O
```

It provides communication pathways and interfaces between components.

---

# 19. Bus

A **bus** is a communication pathway between components.

Simplified:

```text
CPU  ←──── Bus ────→  RAM
 |
 |
 +──── Bus ────────→  I/O
```

Historically, you will encounter concepts such as:

* Data bus
* Address bus
* Control bus

At a beginner level, remember:

> **A bus provides a way for components to communicate.**

Modern computers use more sophisticated interconnects rather than one simple shared bus for everything, but the concept remains useful.

---

# 20. GPU

GPU stands for:

**Graphics Processing Unit**

Originally designed primarily for graphics, GPUs are extremely good at performing many similar operations in parallel.

For example:

```text
CPU

Core → Task
Core → Task
Core → Task
Core → Task
```

versus a GPU with a very large number of simpler parallel processing units.

This makes GPUs useful for:

* Graphics
* Deep learning
* Matrix operations
* Scientific computing
* Large-scale parallel workloads

That's why frameworks such as PyTorch can use:

```python
model.to("cuda")
```

to execute suitable operations on an NVIDIA GPU.

---

# 21. NIC

NIC stands for:

**Network Interface Card/Controller**

It allows a computer to communicate over a network.

For example:

```text
Computer
   |
  NIC
   |
Ethernet/Wi-Fi
   |
 Router
   |
 Internet
```

This becomes especially important when you learn:

* Docker networking
* Kubernetes networking
* TCP/IP
* AWS VPC
* Network namespaces

---

# 22. Input and Output

Computers need to communicate with the outside world.

Examples:

```text
Input:
Keyboard
Mouse
Microphone
Network

Output:
Monitor
Speaker
Network
Storage
```

This is usually called **I/O — Input/Output**.

---

# 23. Hardware vs Software

This distinction is fundamental.

### Hardware

Physical components:

```text
CPU
RAM
SSD
GPU
NIC
Keyboard
Monitor
```

### Software

Instructions/programs:

```text
Windows
Linux
Python
Docker
Kubernetes
Nginx
PostgreSQL
```

The relationship is:

```text
Software
    ↓
Operating System
    ↓
Hardware
```

---

# 24. Where Does the Operating System Fit?

The OS sits between applications and hardware.

```text
+-----------------------+
| Applications          |
| Python / Docker / etc |
+-----------------------+
            ↓
+-----------------------+
| Operating System      |
| Linux / Windows       |
+-----------------------+
            ↓
+-----------------------+
| Hardware              |
| CPU / RAM / Disk / NIC|
+-----------------------+
```

For example, your Python program doesn't normally tell the SSD:

> "Move these exact electrical signals."

Instead, it asks the OS to perform operations.

The OS manages resources such as:

* CPU
* Memory
* Processes
* Files
* Networking
* Devices

This is why **Linux knowledge becomes very important for MLOps**.

---

# 25. Process

When you execute:

```bash
python app.py
```

Linux creates a **process**.

Conceptually:

```text
Python program
      ↓
    Process
      ↓
+-----+-----+
|           |
CPU        RAM
```

A process has things such as:

* Its own virtual address space
* Code
* Data
* Stack
* Heap
* Open files
* Threads

You don't need to memorize these yet.

---

# 26. Virtual Memory

This is another important concept for your future Linux/Docker/Kubernetes learning.

Programs don't normally work directly with physical RAM addresses.

Instead:

```text
Application
     ↓
Virtual Memory Address
     ↓
Operating System
     ↓
Physical RAM
```

For example:

```text
Process A
Virtual memory
0x0000...
0x1000...
0x2000...

        ↓

Physical RAM
Different physical locations
```

This gives each process an isolated address space.

This concept eventually leads to:

* Pages
* Page tables
* Memory mapping
* Swap
* Memory protection
* Containers
* Linux namespaces

---

# 27. Architecture vs Microarchitecture

These two terms are easy to confuse.

### Architecture

The programmer-visible design.

For example:

```text
x86-64
ARM64
RISC-V
```

### Microarchitecture

How a particular CPU implements that architecture.

For example, two CPUs may both support:

```text
x86-64
```

but internally use very different designs.

So:

```text
ISA / Architecture
        ↓
Microarchitecture
        ↓
Physical CPU
```

---

# 28. RISC vs CISC

You will eventually encounter this.

Two broad historical approaches are:

```text
RISC
Reduced Instruction Set Computer

CISC
Complex Instruction Set Computer
```

A simplified comparison:

| RISC                                   | CISC                            |
| -------------------------------------- | ------------------------------- |
| Simpler instructions                   | More complex instructions       |
| Often fixed/simple instruction formats | More varied instruction formats |
| ARM, RISC-V                            | x86                             |
| Common in mobile/embedded              | Common in PCs/servers           |

Modern CPUs are more complicated than this simple distinction suggests, so don't treat it as a strict "simple vs complex CPU" rule.

---

# 29. The Most Important Mental Model

If you remember only one diagram, remember this:

```text
                    COMPUTER
                       |
        +--------------+--------------+
        |              |              |
       CPU            RAM           Storage
        |              |              |
   +----+----+         |         SSD / HDD
   |         |         |
Registers    ALU       |
   |                   |
   +--------+----------+
            |
       Processing
```

And around them:

```text
                 +-------------+
                 |     CPU     |
                 |             |
                 | Registers   |
                 | ALU         |
                 | Control     |
                 | Cache       |
                 +------+------+
                        |
                       RAM
                        |
                 +------+------+
                 |             |
               Storage        I/O
                              |
                       +------+------+
                       |             |
                      NIC           GPU
```

---
## What Is a CPU Core?

A **CPU core** is an individual processing unit inside a CPU.

Think of the CPU as a company and each core as a worker who can execute instructions.

For example, an 8-core CPU can be viewed simply as:

```text
              CPU
               |
    +----------+----------+
    |          |          |
  Core 1     Core 2     Core 3
    |          |          |
    +----------+----------+
    |          |          |
  Core 4     Core 5     Core 6
    |          |          |
    +----------+----------+
    |          |
  Core 7     Core 8
```

Each core can execute instructions independently.

### Single-core CPU

A single-core CPU has one processing core:

```text
CPU
 |
Core 1
 |
Executes instructions
```

### Multi-core CPU

A multi-core CPU has multiple processing cores:

```text
CPU
 |
 +-- Core 1
 +-- Core 2
 +-- Core 3
 +-- Core 4
```

This allows the CPU to work on multiple tasks **concurrently**.

For example:

```text
Core 1 → Python program
Core 2 → Browser
Core 3 → Docker
Core 4 → Database
```

The operating system schedules work across the available cores.

### Core vs CPU

These terms are often confused:

```text
CPU = The whole processor
Core = A processing unit inside the CPU
```

For example:

> **AMD Ryzen 7 7700 = 1 CPU with 8 physical cores.**

So when someone says **“8-core CPU”**, they mean:

```text
1 CPU
 ├── Core 1
 ├── Core 2
 ├── Core 3
 ├── Core 4
 ├── Core 5
 ├── Core 6
 ├── Core 7
 └── Core 8
```

One important point:

> **More cores do not automatically mean the computer is faster at everything.**

Performance also depends on clock speed, CPU architecture, cache, memory, workload, and other factors.

### Core vs Thread

A **core** is physical processing hardware.

A **hardware thread** is a logical execution context provided by a core.

For example:

```text
8 cores / 16 threads
```

means:

```text
CPU
 |
 +-- Core 1 → Thread 1 + Thread 2
 +-- Core 2 → Thread 3 + Thread 4
 +-- Core 3 → Thread 5 + Thread 6
 ...
 +-- Core 8 → Thread 15 + Thread 16
```

So:

**8 cores ≠ 16 physical cores.**

It means **8 physical cores capable of supporting 16 hardware threads**.




# The 10 concepts to make absolutely solid first

## 1. Process

A **process** is a program that is currently running.

For example:

```text
You run:
python app.py

        ↓

Operating System

        ↓

Creates a process

        ↓

Python application is running
```

A process gets its own **virtual memory space** and contains things like:

* Code
* Data
* Heap
* Stack
* Threads
* Open files
* Network sockets

Example in MLOps:

```text
FastAPI application
        ↓
FastAPI process
        ↓
Loads ML model
        ↓
Accepts requests
        ↓
Runs inference
```

**Remember:**

> Process = a running program.

---

# 2. Thread

A **thread** is an execution path inside a process.

A process can contain one or multiple threads.

```text
Process
│
├── Thread 1
├── Thread 2
├── Thread 3
└── Thread 4
```

Think:

```text
Process = restaurant
Thread  = worker inside the restaurant
```

The process provides the environment and resources. Threads perform the actual execution.

**Remember:**

> Process = container of execution resources
> Thread = execution path inside the process

---

# 3. Worker

**Worker** means something that performs a unit of work.

The exact meaning depends on the software.

For example, in a web server:

```text
Client
  │
  ├── Request 1
  ├── Request 2
  └── Request 3
          │
          ↓
     Web Server
     ┌────────┐
     │Worker 1│
     │Worker 2│
     │Worker 3│
     └────────┘
```

A worker may be:

* A process
* A thread
* A task executor
* A background job consumer
* Sometimes a container/pod, depending on the system

For example:

```text
4 FastAPI workers
        ↓
4 server processes
        ↓
Each may load the ML model
```

This is important because:

```text
4 workers
×
2 GB model
≈
8 GB model memory
```

plus Python/runtime/framework memory.

**Remember:**

> Worker = an execution unit responsible for doing work.

---

# 4. CPU Core

A **CPU core** is a physical processing unit inside a CPU.

For example:

```text
CPU
├── Core 1
├── Core 2
├── Core 3
└── Core 4
```

Each core can execute instructions.

So if you have:

```text
8 CPU cores
```

you have roughly:

```text
8 physical processing units
```

With SMT/Hyper-Threading, the operating system may see more **logical processors**:

```text
8 physical cores
        ↓
16 logical processors
```

That does **not** mean you have 16 physical cores.

**Remember:**

> Core = physical CPU execution unit.

---

# 5. RAM

**RAM (Random Access Memory)** is the computer's main working memory.

When a program runs:

```text
SSD
 │
 │ load program/model
 ↓
RAM
 │
 ↓
CPU
```

For example:

```text
ML model on disk
       ↓
Load model
       ↓
RAM
       ↓
CPU executes inference
```

RAM is much faster than SSD but is volatile.

When the machine shuts down, normal RAM contents disappear.

**Remember:**

> RAM = temporary working memory used by running programs.

---

# 6. Virtual Memory

This is one of the **most important concepts for Linux and containers**.

Programs generally don't directly use physical RAM addresses.

Instead:

```text
Application
     ↓
Virtual Address
     ↓
MMU + Page Tables
     ↓
Physical RAM
```

Each process gets its own virtual address space.

For example:

```text
Process A
Virtual address 0x1000
        ↓
Physical frame A


Process B
Virtual address 0x1000
        ↓
Physical frame B
```

Both processes can have the same virtual address, but they map to different physical memory.

Virtual memory provides:

* Process isolation
* Memory protection
* Flexible memory management
* Ability to use more memory through mechanisms such as swap

**Remember:**

> Virtual memory gives each process its own view of memory.

---

# 7. Kernel

The **kernel is the core part of the operating system**.

It manages hardware and provides services to applications.

```text
Applications
     │
     ↓
System Calls
     │
     ↓
Linux Kernel
     │
 ┌───┼────┬──────┐
 ↓   ↓    ↓      ↓
CPU RAM Network Storage
```

The kernel manages things like:

* Processes
* CPU scheduling
* Memory
* Filesystems
* Networking
* Devices
* Security
* Sockets
* Containers

This is why Linux knowledge is so important for Docker and Kubernetes.

**Remember:**

> Kernel = the privileged core of the operating system that manages resources and hardware.

---

# 8. System Call

Applications cannot freely access hardware or kernel-managed resources.

They request services from the kernel through **system calls**.

For example, your Python program wants to read a file:

```text
Python
  ↓
Python runtime
  ↓
read() system call
  ↓
Linux kernel
  ↓
Filesystem
  ↓
Storage
```

Networking works similarly:

```text
Python
  ↓
socket()
  ↓
Linux kernel
  ↓
Network stack
  ↓
NIC
  ↓
Network
```

Common system-call-related operations include:

```text
open()
read()
write()
close()
socket()
connect()
accept()
send()
recv()
```

**Remember:**

> System call = controlled entry point from an application into the kernel.

---

# 9. Socket

A **socket** is an operating-system abstraction that applications use for communication.

For network communication:

```text
Application
     ↓
Socket
     ↓
TCP/UDP
     ↓
IP
     ↓
NIC
     ↓
Network
```

For example, a FastAPI application might listen on:

```text
0.0.0.0:8000
```

Here:

```text
0.0.0.0 = listening network address
8000    = port
```

A simplified request:

```text
Client
  ↓
IP + Port
  ↓
Server Socket
  ↓
FastAPI
```

Sockets are extremely important for:

* FastAPI
* TCP
* HTTP
* Docker networking
* Kubernetes Services
* Databases
* Microservices

**Remember:**

> Socket = OS interface/end-point used by applications for communication.

---

# 10. CPU vs GPU / VRAM

This is especially important for ML engineers.

### CPU

CPU is designed for general-purpose computation.

```text
CPU
├── Core
├── Core
├── Core
└── Core
```

It is good at:

* General application logic
* Branching
* OS operations
* Networking
* Sequential/irregular workloads
* Data preprocessing

### GPU

GPU contains many execution units designed for highly parallel computation.

```text
GPU
├── Many execution units
├── Many execution units
├── Many execution units
└── ...
```

This makes GPUs very effective for operations such as:

```text
Matrix multiplication
Tensor operations
Neural network inference
Neural network training
```

### VRAM

VRAM is the GPU's memory.

```text
CPU
 │
 │ system RAM
 ↓
RAM
 │
 │ PCIe / interconnect
 ↓
GPU
 │
 ↓
VRAM
```

An ML model running on GPU may look like:

```text
Model
  ↓
VRAM
  ↓
GPU computation
  ↓
Prediction
```

If VRAM is insufficient:

```text
CUDA/GPU memory allocation
        ↓
Not enough VRAM
        ↓
GPU OOM
```

This is different from system RAM OOM.

**Remember:**

> CPU = general-purpose processor
> GPU = highly parallel processor
> RAM = main system memory
> VRAM = GPU memory

---

# Then learn these 10

These concepts build on the first 10.

---

## 11. TCP

**TCP = Transmission Control Protocol.**

It provides reliable, ordered communication between applications.

```text
Application A
     ↓
    TCP
     ↓
    IP
     ↓
 Network
     ↓
    IP
     ↓
    TCP
     ↓
Application B
```

TCP provides things such as:

* Reliable delivery
* Ordering
* Retransmission
* Flow control
* Congestion control

HTTP commonly runs over TCP in HTTP/1.1 and HTTP/2.

**Remember:**

> TCP gives applications a reliable, ordered byte stream.

---

# 12. Kubernetes

Kubernetes manages containerized applications.

Without Kubernetes:

```text
You
 ↓
Start container
 ↓
Monitor it
 ↓
Restart if it crashes
 ↓
Scale it
 ↓
Connect it to other containers
```

With Kubernetes:

```text
Kubernetes
     │
 ┌───┼─────────┐
 ↓   ↓         ↓
Deploy Scale  Restart
     │
     ↓
Networking
     │
     ↓
Service discovery
```

It manages:

* Containers
* Pods
* Scheduling
* Scaling
* Networking
* Service discovery
* Health checks
* Restarts
* Resource limits

**Remember:**

> Kubernetes is a system for managing containerized workloads across machines.

---

# 13. Container

A container is an isolated environment for running a process and its dependencies.

Important point:

> A Linux container is **not a small virtual machine**.

Conceptually:

```text
Physical Machine
       ↓
Linux Kernel
       ↓
Container Runtime
       ↓
┌─────────────┬─────────────┐
│ Container A │ Container B │
│   Process   │   Process   │
└─────────────┴─────────────┘
```

Containers share the host kernel.

Linux uses mechanisms such as:

```text
Namespaces → isolation
cgroups    → resource control
```

This becomes very important when learning Docker.

**Remember:**

> Container = isolated process environment using the host kernel.

---

# 14. I/O

**I/O = Input/Output.**

It means moving data into or out of a system.

Examples:

```text
Disk → RAM
RAM → Disk
Database → Application
Application → Database
Network → Application
Application → Network
```

For example:

```text
FastAPI
   ↓
Database query
   ↓
Wait for database
```

The CPU may not be doing much during the wait.

That is an **I/O-bound workload**.

**Remember:**

> I/O = communication with external resources such as storage, databases, and devices.

---

# 15. Throughput

**Throughput = how much work is completed per unit of time.**

For an API:

```text
100 requests / second
```

means:

```text
Throughput = 100 requests/sec
```

For ML training:

```text
10,000 samples / minute
```

could describe throughput.

Higher throughput generally means the system can process more work over time.

**Remember:**

> Throughput = how much work the system completes over time.

---

# 16. Latency

**Latency = how long something takes.**

For an API:

```text
Request
  ↓
Model inference
  ↓
Response

100 ms
```

The request latency is approximately 100 ms.

You may see:

```text
P50 latency = 80 ms
P95 latency = 150 ms
P99 latency = 300 ms
```

This tells you how quickly individual requests are completed.

### Throughput vs latency

```text
Latency
= How long does ONE request take?


Throughput
= How many requests can I process per second?
```

They are related but not the same.

---

# 17. Overhead

**Overhead = additional cost required to perform useful work.**

Suppose your model computation takes:

```text
10 ms
```

But the complete request takes:

```text
Preprocessing       5 ms
Data transfer       8 ms
Model inference    10 ms
Serialization       4 ms
Network              8 ms
-------------------------
Total               35 ms
```

The useful model computation is only 10 ms.

The remaining time is overhead or other surrounding work.

In MLOps, overhead can come from:

* Serialization
* Deserialization
* Networking
* Process management
* Context switching
* CPU/GPU data transfer
* Framework/runtime operations

**Remember:**

> Overhead = extra resource usage or time around the actual useful computation.

---

# 18. OOM

**OOM = Out Of Memory.**

Example:

```text
Container memory limit = 2 GB

Application needs = 3 GB

        ↓

Not enough memory

        ↓

OOM
```

In Kubernetes, a container that exceeds its memory limit can be terminated and shown as:

```text
OOMKilled
```

There are also GPU OOM situations:

```text
VRAM = 8 GB
Model + tensors = 10 GB

        ↓

GPU OOM
```

**Remember:**

> OOM = the system cannot provide enough required memory.

---

# 19. Swapping

When RAM is under pressure, Linux can move some memory contents to **swap**, which is backed by storage.

```text
RAM
 │
 │ memory pressure
 ↓
Swap
 │
 ↓
SSD/HDD
```

Storage is much slower than RAM.

Therefore, heavy swapping can make a system extremely slow.

Example:

```text
RAM almost full
       ↓
Memory pressure
       ↓
Pages moved to swap
       ↓
Application needs those pages again
       ↓
Read from storage
       ↓
Slow
```

**Remember:**

> Swapping = using storage as backing for memory pages when RAM is under pressure.

---

# 20. Data Transfer

**Data transfer = moving data from one place to another.**

Examples:

```text
SSD → RAM
RAM → CPU
RAM → GPU
GPU → RAM
Container → Container
Server → Client
```

For ML, this is particularly important:

```text
CPU
 │
 │ Data transfer
 ↓
GPU
 │
 ↓
VRAM
```

Suppose:

```text
GPU computation = 5 ms
CPU → GPU transfer = 20 ms
GPU → CPU transfer = 10 ms
```

Then your GPU is extremely fast, but the overall operation may still be slow.

This is why **CPU/GPU data-transfer overhead** matters in ML systems.

---

# The complete picture

These concepts become much easier when you connect them:

```text
                  APPLICATION
                       │
                       ↓
                    Process
                       │
                  ┌────┴────┐
                  ↓         ↓
               Thread     Thread
                  │
                  ↓
                Worker
                  │
                  ↓
              CPU Core
                  │
                  ↓
             RAM / Cache
                  │
                  ↓
             Virtual Memory
                  │
                  ↓
                Kernel
                  │
             System Calls
                  │
          ┌───────┼────────┐
          ↓       ↓        ↓
        Disk    Socket    GPU
                    │       │
                    ↓       ↓
                  TCP     VRAM
                    │
                    ↓
                  Network
```

And when Docker/Kubernetes are added:

```text
Application
     ↓
Process
     ↓
Container
     ↓
Linux Kernel
     ↓
Docker
     ↓
Kubernetes
     ↓
Pods
     ↓
Services
     ↓
Network
```

## The learning priority I'd use for your MLOps path

### Tier 1 — Make these very solid

```text
Process
Thread
Worker
CPU Core
RAM
Virtual Memory
Kernel
System Call
Socket
CPU vs GPU / VRAM
```

### Tier 2 — Understand clearly

```text
TCP
Container
Kubernetes
I/O
Latency
Throughput
```

### Tier 3 — Understand for troubleshooting

```text
Overhead
OOM
Swapping
Data Transfer
```

Once these are solid, a statement like:

> "Our Kubernetes inference service has high latency because each pod has too many workers, causing CPU contention and memory pressure, while CPU-to-GPU data transfer adds additional overhead."



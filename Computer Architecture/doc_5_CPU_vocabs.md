
# 1. Thread

A **thread** is an execution path inside a process.

Think of a **process as a restaurant** and threads as **workers inside the restaurant**.

```text
Process = Restaurant

        ┌──────────────────────┐
        │      Restaurant      │
        │                      │
        │  Thread 1 → Worker A │
        │  Thread 2 → Worker B │
        │  Thread 3 → Worker C │
        │                      │
        └──────────────────────┘
```

Each thread performs a sequence of instructions.

For example, suppose your FastAPI application receives three requests:

```text
Request A
Request B
Request C
```

The application could have multiple threads handling work.

### Important distinction

A **process** provides an environment/resources.

A **thread** performs execution within that process.

```text
Process
│
├── Memory
├── Files
├── Resources
│
├── Thread 1
├── Thread 2
└── Thread 3
```

---

# 2. Workload

A **workload** means the actual work a computer is being asked to perform.

For an ML server, the workload might be:

```text
Receive image
     ↓
Resize image
     ↓
Normalize image
     ↓
Run model
     ↓
Generate prediction
     ↓
Return response
```

That entire activity is part of the application's workload.

Different workloads stress different hardware.

### CPU-heavy workload

```text
Complex calculations
Data preprocessing
Compression
Large amounts of computation
```

### I/O-heavy workload

```text
Read files
Write files
Wait for database
Wait for network
```

### GPU-heavy workload

```text
Matrix multiplication
Tensor operations
Deep learning inference
Deep learning training
```

So when someone says:

> "It depends on the workload."

They mean:

> "The best solution depends on what the application is actually doing."

---

# 3. Thread per Worker

This phrase can be confusing.

A **worker** is a unit responsible for processing tasks or requests.

For example:

```text
Server
│
├── Worker 1
├── Worker 2
├── Worker 3
└── Worker 4
```

Each worker might have one or multiple threads.

For example:

```text
Worker 1
├── Thread 1
├── Thread 2
└── Thread 3

Worker 2
├── Thread 4
├── Thread 5
└── Thread 6
```

So:

> **Thread per worker** means each worker has a certain number of threads available to perform work.

If you configure:

```text
8 workers
4 threads per worker
```

you potentially have:

```text
8 × 4 = 32 threads
```

available for application work.

This does **not** mean 32 CPU cores are required. The OS schedules those threads onto available CPU resources.

---

# 4. What is a Worker?

A **worker** is a process or execution unit that performs assigned tasks.

The exact meaning depends on the software.

For example, a web server may have:

```text
Master
│
├── Worker 1
├── Worker 2
├── Worker 3
└── Worker 4
```

Each worker handles incoming requests.

Think:

```text
Manager
   ↓
Workers
   ↓
Tasks
```

---

# 5. What is an ML Worker?

An **ML worker** is a worker responsible for performing ML-related work.

For example:

```text
Request
   ↓
ML Worker
   ↓
Load model
   ↓
Preprocess input
   ↓
Run inference
   ↓
Return prediction
```

Suppose your model is:

```text
BERT
```

and your API has:

```text
4 workers
```

If each worker loads its own copy of BERT:

```text
Worker 1 → BERT
Worker 2 → BERT
Worker 3 → BERT
Worker 4 → BERT
```

Then memory consumption can become significant.

This is why **number of ML workers is an important MLOps consideration**.

---

# 6. Python Runtime

The **Python runtime** is the software environment that executes Python programs.

When you run:

```bash
python app.py
```

Python needs to:

```text
Read Python code
      ↓
Interpret/execute it
      ↓
Manage Python objects
      ↓
Manage memory
      ↓
Interact with the operating system
```

The runtime includes the Python interpreter and supporting runtime machinery.

For example:

```text
Your FastAPI code
       ↓
Python runtime
       ↓
Operating system
```

It is therefore more than just your `.py` file.

---

# 7. Runtime Overhead

**Overhead** means additional resources required to perform something beyond the actual useful work.

For example:

```text
ML model = 2 GB
```

doesn't mean your application needs exactly 2 GB RAM.

You may also need memory for:

```text
Python runtime
Framework
Libraries
Request data
Intermediate tensors
Buffers
OS resources
```

That additional consumption is **runtime overhead**.

Think:

```text
Useful work
     +
Supporting cost
     =
Total resource usage
```

---

# 8. Overhead

More generally, **overhead is the extra cost of performing an operation**.

Suppose you need to send data from CPU RAM to GPU VRAM.

The useful work is:

```text
GPU processing
```

But before that, you may need:

```text
CPU memory
   ↓
Data transfer
   ↓
GPU memory
   ↓
Processing
```

The transfer takes time.

That transfer time is an example of **overhead**.

---

# 9. Throughput

**Throughput** means:

> How much work a system can complete per unit of time.

For an ML API:

```text
100 requests/second
```

means:

```text
Throughput = 100 requests/sec
```

For model training, it could be:

```text
10,000 samples/sec
```

### Analogy

Imagine a factory.

```text
Factory A → 100 cars/hour
Factory B → 500 cars/hour
```

Factory B has higher throughput.

---

# 10. Inference Latency

**Inference latency** is how long it takes to produce a prediction for a request.

Suppose:

```text
Request arrives
      ↓
Model processes it
      ↓
Response returned
```

If this takes:

```text
80 ms
```

then inference latency is approximately 80 ms, depending on exactly what portion of the request path you measure.

### Example

```text
User sends image
       ↓
20 ms preprocessing
       ↓
50 ms model inference
       ↓
10 ms postprocessing
       ↓
Response

Total = 80 ms
```

Latency asks:

> **How long did one request take?**

Throughput asks:

> **How many requests can we process per second?**

---

# 11. Throughput vs Latency

This distinction is extremely important for MLOps interviews.

| Concept    | Question                                     |
| ---------- | -------------------------------------------- |
| Latency    | How long does one request take?              |
| Throughput | How many requests can we process per second? |

Example:

```text
Server A
Latency = 20 ms
Throughput = 50 req/sec

Server B
Latency = 100 ms
Throughput = 500 req/sec
```

Depending on your application, either system could be preferable.

---

# 12. Branching / Control-Heavy Workload

A **branch** means choosing between different execution paths.

For example:

```python
if age > 18:
    allow()
else:
    reject()
```

The CPU must determine which path to execute.

A **control-heavy workload** contains lots of:

```text
if
else
switch
loops
conditional decisions
irregular execution paths
```

Example:

```text
if A:
    do X
elif B:
    do Y
else:
    do Z
```

This can be less suitable for GPUs than highly regular parallel mathematical operations.

---

# 13. Specialized Execution

A processor can contain hardware designed for particular types of operations.

For example:

```text
CPU
├── General-purpose execution
├── Integer operations
├── Floating-point operations
└── Vector operations

GPU
└── Highly parallel numerical operations
```

**Specialized execution** means using hardware that is particularly suited to the operation.

For ML:

```text
Matrix operations
      ↓
GPU
      ↓
Highly parallel execution
```

This is one reason GPUs are useful for deep learning.

---

# 14. Data Transfer

**Data transfer** means moving data from one place to another.

In ML, an important example is:

```text
CPU RAM
   ↓
Data transfer
   ↓
GPU VRAM
```

Suppose your image is in CPU memory:

```text
Image
 ↓
RAM
```

but your model is running on the GPU:

```text
Model
 ↓
VRAM
```

The image must be transferred to the GPU.

That movement takes time and can become an **overhead**.

---

# 15. I/O Bottleneck

**I/O = Input/Output.**

It includes things such as:

```text
Disk reads
Disk writes
Network communication
Database operations
File operations
```

An **I/O bottleneck** occurs when the application is mostly waiting for I/O.

Example:

```text
ML application
      ↓
Need dataset
      ↓
Read 100 GB from slow storage
      ↓
CPU/GPU waits
```

Your GPU could be extremely powerful, but if data arrives too slowly:

```text
GPU
 ↓
waiting...
 ↓
waiting...
 ↓
waiting...
```

GPU utilization may remain low.

---

# 16. Swapping

Normally:

```text
Process
   ↓
RAM
```

When RAM becomes heavily pressured, Linux can move some memory contents to swap space.

Conceptually:

```text
RAM
 ↓
Memory pressure
 ↓
Swap
 ↓
Disk
```

The problem is that SSD/storage is generally much slower than RAM.

So excessive swapping can make a system very slow.

---

# 17. Memory Reclaim

When Linux needs more memory, it can try to **reclaim memory**.

For example, it may free memory associated with caches that can be reconstructed later.

Conceptually:

```text
RAM pressure
     ↓
Linux tries to reclaim memory
     ↓
Free/reusable memory
```

This is different from immediately assuming that all memory shown as "used" is unavailable.

Linux uses RAM for useful caches too.

---

# 18. OOM

**OOM = Out Of Memory.**

It means the system or a particular resource-controlled environment cannot satisfy a memory demand.

Example:

```text
Container memory limit = 2 GB

Application needs:
3 GB
```

The container exceeds its memory limit.

This can result in:

```text
OOM
 ↓
Process killed
```

In Kubernetes you may see:

```text
OOMKilled
```

This is an extremely important MLOps troubleshooting concept.

---

# 19. Physical Frame A and Physical Frame B

This relates to virtual memory.

Suppose:

```text
Process A:
Virtual address 0x1000
```

and:

```text
Process B:
Virtual address 0x1000
```

They can map to different physical memory locations.

For example:

```text
Process A
0x1000
  ↓
Physical Frame A


Process B
0x1000
  ↓
Physical Frame B
```

A **physical frame** is a fixed-size block of physical memory, typically corresponding to a virtual-memory page.

The important idea is:

> Virtual addresses are translated into physical memory locations.

---

# 20. Eventually OOM

"Eventually OOM" means that after exhausting available memory-management options, the system reaches a point where it cannot satisfy memory demands.

Conceptually:

```text
Application requests memory
        ↓
RAM available?
    ┌───┴───┐
   Yes      No
    │        │
 Allocate   Reclaim
             ↓
          Swap if available
             ↓
       Still insufficient
             ↓
             OOM
```

For containers:

```text
Container exceeds memory limit
            ↓
          OOMKill
```

---

# 21. Kernel

The **kernel is the core part of the operating system**.

Linux itself is based around the Linux kernel.

It manages and provides controlled access to:

```text
CPU
Memory
Processes
Networking
Filesystems
Devices
```

Think of it as the **resource manager between applications and hardware**.

```text
Applications
     ↓
Linux Kernel
     ↓
Hardware
```

---

# 22. Host Kernel

The **host kernel** is the kernel belonging to the machine that is running something else.

For Docker:

```text
Physical Machine
       ↓
Host Linux
       ↓
Host Linux Kernel
       ↓
Containers
```

Containers generally share the host kernel.

This is one of the fundamental differences between containers and traditional VMs.

---

# 23. Kubernetes

**Kubernetes is a system for managing containerized applications across machines.**

It can handle things such as:

```text
Deploying containers
Scaling applications
Restarting failed containers
Service discovery
Networking
Load distribution
Rolling updates
Resource management
```

For example:

```text
Kubernetes Cluster
│
├── Node 1
│   ├── Pod
│   └── Pod
│
├── Node 2
│   ├── Pod
│   └── Pod
│
└── Node 3
    └── Pod
```

Kubernetes decides where workloads should run and manages their desired state.

For your MLOps path:

```text
Docker
  ↓
Container
  ↓
Kubernetes
  ↓
ML model deployment
```

---

# 24. Hypervisor

A **hypervisor** is software that manages virtual machines.

Conceptually:

```text
Physical Hardware
       ↓
Hypervisor
       ↓
┌──────────────┐
│ VM 1         │
│ Guest Linux  │
└──────────────┘

┌──────────────┐
│ VM 2         │
│ Guest Linux  │
└──────────────┘
```

Each VM can have its own operating system.

### VM

```text
Hardware
 ↓
Hypervisor
 ↓
Guest OS
 ↓
Application
```

### Container

```text
Hardware
 ↓
Host Kernel
 ↓
Container
 ↓
Application
```

This distinction becomes important when you work with AWS EC2, Kubernetes nodes, and virtualization.

---

# 25. TCP

**TCP = Transmission Control Protocol.**

TCP is a transport-layer protocol that provides a reliable, ordered byte stream between endpoints.

Suppose:

```text
Client
  ↓
TCP
  ↓
Server
```

TCP handles things such as:

```text
Connection establishment
Reliable delivery
Ordering
Retransmission
Flow control
Congestion control
```

For example, when you connect to:

```text
FastAPI server
10.0.0.10:8000
```

you might be using:

```text
TCP
+
IP
+
Port 8000
```

---

# 26. Socket

A **socket is the interface applications use to communicate through the networking stack.**

Conceptually:

```text
FastAPI
   ↓
Socket API
   ↓
TCP
   ↓
IP
   ↓
NIC
```

For example:

```text
10.0.0.10:8000
```

can represent a network endpoint.

The application doesn't manually construct Ethernet frames. It uses the socket interface and the kernel networking stack handles the lower-level work.

---

# 27. FastAPI Process

Suppose you execute:

```bash
uvicorn main:app
```

Your operating system creates a process for the running server.

Conceptually:

```text
Linux
  ↓
Process
  ↓
Python runtime
  ↓
FastAPI application
```

That running process contains the application code and its execution environment.

---

# 28. Application Thread

Inside that process, execution occurs through one or more threads.

For example:

```text
FastAPI Process
│
├── Thread 1
├── Thread 2
└── Thread 3
```

Those threads execute application work.

A request might be handled through:

```text
Network
   ↓
NIC
   ↓
Linux kernel
   ↓
Socket
   ↓
Application
   ↓
Thread
   ↓
FastAPI
```

This is a simplified model, but it is an excellent mental model for interviews.

---

# 29. VRAM

**VRAM = Video Random Access Memory**, commonly referring to memory dedicated to a GPU.

For an ML workload:

```text
CPU
 ↓
RAM

GPU
 ↓
VRAM
```

A deep-learning model may be loaded into VRAM:

```text
BERT model
    ↓
GPU VRAM
    ↓
GPU computation
```

VRAM stores things such as:

```text
Model parameters
Input tensors
Intermediate activations
Other GPU data
```

If the GPU runs out of VRAM:

```text
VRAM full
   ↓
Cannot allocate required memory
   ↓
CUDA/GPU out-of-memory error
```

This is different from normal system RAM OOM.

---

# 30. The Complete MLOps Picture

Now connect all of the terms you asked about.

Suppose you deploy a **FastAPI ML inference service on Kubernetes with a GPU**.

A request arrives:

```text
                    USER
                      │
                      ↓
                  NETWORK
                      │
                      ↓
                     NIC
                      │
                      ↓
                Linux Kernel
                      │
                   TCP/IP
                      │
                   Socket
                      │
                      ↓
              FastAPI Process
                      │
              ┌───────┴───────┐
              │               │
           Worker          Worker
              │               │
           Thread           Thread
              │               │
              └───────┬───────┘
                      ↓
                 ML Model
                      │
                 CPU / GPU
                      │
                  GPU VRAM
                      │
                      ↓
                  Prediction
                      │
                      ↓
                   Response
```

And underneath Kubernetes:

```text
Kubernetes
    ↓
Container
    ↓
Host Linux Kernel
    ↓
CPU / RAM / GPU
```

---

# 31. Extra vocabs 

> **"What resource is limiting my application's performance?"**

Think of your application as a car. If the car is slow, you need to know whether the problem is the engine, fuel, road, transmission, or something else.

---

#  CPU-bound

**CPU-bound** means the application spends most of its time doing CPU computation.

In simple words:

> **The CPU is the thing slowing you down.**

Example:

```text
ML application
     ↓
Heavy preprocessing
     ↓
Lots of calculations
     ↓
CPU → 100%
```

For example, suppose your ML pipeline does:

```text
Large image
   ↓
Resize
   ↓
Transform
   ↓
Feature extraction
   ↓
CPU calculations
```

If the CPU is constantly busy while other resources are mostly waiting, the workload may be CPU-bound.

### How might you notice?

```text
CPU utilization → very high
GPU utilization → low
Disk utilization → low
Network usage   → low
```

### Possible solutions

Depending on the cause:

```text
Better algorithm
More CPU cores
More workers
CPU optimization
Vectorization
Better preprocessing
Horizontal scaling
```

---

#  Memory-bound

**Memory-bound** means the application is limited primarily by memory access or memory capacity rather than raw CPU computation.

There are two related situations you should distinguish.

### Situation A: Not enough RAM

```text
Application
    ↓
Needs more memory
    ↓
RAM nearly full
    ↓
Memory pressure
    ↓
Performance drops
```

### Situation B: CPU is waiting for memory

The CPU can perform calculations extremely quickly, but it may have to wait for data from RAM.

```text
CPU
 ↓
"Give me data"
 ↓
Cache miss
 ↓
RAM
 ↓
Wait
```

This is also a form of memory-related bottleneck.

### MLOps example

Your model server has:

```text
RAM = 16 GB
```

But:

```text
Model          = 8 GB
Python/runtime = 2 GB
Workers        = 6 GB
Requests       = 3 GB
```

Total demand can exceed available RAM.

---

#  GPU-bound

**GPU-bound** means the GPU is the main resource limiting performance.

In simple words:

> **The GPU is working as hard as it can, and more GPU capacity could improve performance.**

Example:

```text
Request
   ↓
GPU
   ↓
Heavy matrix calculations
   ↓
GPU utilization → 100%
```

For deep learning:

```text
Input
  ↓
Transformer
  ↓
Matrix operations
  ↓
GPU
```

If the GPU is consistently saturated, the workload may be GPU-bound.

### Example

```text
GPU utilization = 98%
CPU utilization = 30%
```

You might investigate:

* larger/faster GPU
* batching
* model optimization
* quantization
* parallel inference
* multiple GPUs

---

#  I/O-bound

**I/O-bound** means the application spends much of its time waiting for input/output operations.

I/O includes:

```text
Disk
SSD
Database
File system
Network
External services
```

Example:

```text
ML application
      ↓
Need dataset
      ↓
Read from storage
      ↓
WAIT...
      ↓
Data arrives
      ↓
Process data
```

The CPU might only be using 20%.

Why?

Because the CPU isn't doing work. It's **waiting**.

### Example

Imagine your model needs 10,000 images.

```text
SSD → images → CPU → model
```

If the SSD is slow:

```text
CPU → waiting
GPU → waiting
```

The entire ML pipeline becomes slow.

---

#  Network-bound

**Network-bound** means network communication is the main limitation.

Example:

```text
Application
    ↓
Request to external API
    ↓
Network
    ↓
WAIT...
    ↓
Response arrives
```

Suppose your application calls another service:

```text
FastAPI
   ↓
Embedding Service
   ↓
Network
   ↓
Embedding returned
```

If the network round trip takes 500 ms, your FastAPI application may spend much of its time waiting.

### Example

```text
CPU = 10%
RAM = 30%
GPU = 20%
Network request = 500 ms
```

The problem may be network-bound.

---

#  Too Much Overhead

**Overhead** means extra cost required to perform the useful work.

Imagine:

```text
Useful computation = 10 ms
Extra operations   = 90 ms
```

Your application takes:

```text
100 ms
```

The 90 ms is overhead.

### MLOps example

You have a model that needs:

```text
10 ms → inference
```

But:

```text
20 ms → preprocessing
15 ms → serialization
25 ms → network
10 ms → data transfer
```

Total:

```text
80 ms
```

The model itself isn't necessarily the bottleneck.

The surrounding operations are.

---

#  CPU/GPU Data-Transfer Overhead

This is particularly important for ML.

Suppose your input starts in CPU RAM:

```text
CPU
 │
 └── RAM
      │
      ↓
    Image
```

But your model runs on the GPU:

```text
GPU
 │
 └── VRAM
```

The image needs to move:

```text
RAM
 ↓
CPU/GPU data transfer
 ↓
VRAM
 ↓
GPU
```

That transfer takes time.

Then the output may need to come back:

```text
VRAM
 ↓
Data transfer
 ↓
RAM
 ↓
CPU
```

### Example

Suppose:

```text
Data preparation = 5 ms
CPU → GPU transfer = 20 ms
GPU inference = 10 ms
GPU → CPU transfer = 15 ms
```

Total:

```text
50 ms
```

But actual GPU computation is only:

```text
10 ms
```

So the application is spending a lot of time around the GPU rather than inside the GPU.

That's **CPU/GPU data-transfer overhead**.

---

#  Too Many Workers

A worker is an execution unit that handles tasks or requests.

Suppose:

```text
CPU = 4 cores
```

and you run:

```text
20 CPU-heavy workers
```

You now have many workers competing for only four physical cores.

```text
             4 CPU cores
                 │
        ┌────────┼────────┐
        ↓        ↓        ↓
     Worker   Worker   Worker
        ...
       20 workers
```

Linux has to schedule them.

This can cause:

```text
Context switching
CPU contention
Scheduling overhead
Higher latency
```

### Important

"More workers = more performance" is **not always true**.

You need the right number of workers for the workload and available resources.

---

#  Are Workers Consuming Too Much Memory?

Each worker may consume memory.

Suppose:

```text
ML model = 2 GB
```

and you have:

```text
4 workers
```

If every worker loads its own model:

```text
Worker 1 → 2 GB
Worker 2 → 2 GB
Worker 3 → 2 GB
Worker 4 → 2 GB
```

That's approximately:

```text
8 GB
```

just for those model copies.

Then you still need:

```text
Python runtime
Libraries
Requests
Intermediate tensors
Other application memory
```

So you might suddenly have:

```text
RAM usage → 95%
```

and eventually:

```text
OOM
```

This is why worker configuration is especially important for ML services.

---

#  CPU-Throttled Container

This one is **very important for Kubernetes interviews**.

Suppose your container has a CPU limit:

```text
CPU limit = 1 CPU
```

Your application wants:

```text
2 CPUs
```

But Kubernetes/container resource controls prevent it from continuously consuming more than its allowed CPU allocation.

Conceptually:

```text
Application wants
      ↓
    2 CPUs
      ↓
Container limit
      ↓
    1 CPU
```

The application can experience **CPU throttling**.

In simple words:

> The container wants more CPU time, but its configured CPU limit restricts how much CPU time it can use.

### Result

```text
CPU throttling
      ↓
Less CPU execution
      ↓
Higher latency
      ↓
Slower application
```

This is very different from simply saying:

> "The node doesn't have enough CPU."

The node may have plenty of CPU, but **your container's limit may be restricting it**.

---

#  Container Hitting Memory Limits

Suppose Kubernetes gives your container:

```text
Memory limit = 2 GB
```

Your application tries to use:

```text
3 GB
```

Conceptually:

```text
Container
Memory limit = 2 GB
       │
       ↓
Application needs 3 GB
       │
       ↓
Limit exceeded
       │
       ↓
OOMKilled
```

You may see something like:

```text
OOMKilled
```

in Kubernetes.

This is one of the most common production ML problems because models can consume substantial memory.

---

#  CPU-bound vs GPU-bound vs I/O-bound

This is the comparison you should memorize:

| Type          | Main bottleneck           | Example                    |
| ------------- | ------------------------- | -------------------------- |
| CPU-bound     | CPU computation           | Image preprocessing        |
| Memory-bound  | Memory capacity/access    | Huge model/data            |
| GPU-bound     | GPU computation           | Transformer inference      |
| I/O-bound     | Storage/database/file I/O | Loading datasets           |
| Network-bound | Network communication     | Calling another ML service |

---

#  A Real MLOps Example

Suppose you have:

```text
FastAPI
   ↓
BERT model
   ↓
Kubernetes
   ↓
GPU
```

A request comes in.

Your pipeline:

```text
HTTP request
     ↓
FastAPI
     ↓
Preprocessing
     ↓
CPU → GPU transfer
     ↓
GPU inference
     ↓
GPU → CPU transfer
     ↓
Postprocessing
     ↓
HTTP response
```

Now imagine the API takes **500 ms**.

You investigate:

```text
CPU utilization = 25%
GPU utilization = 30%
RAM utilization = 50%
Network = normal
Disk = normal
```

You should **not** immediately conclude:

> "We need a bigger GPU."

Instead, investigate where the 500 ms is going.

Maybe:

```text
Preprocessing       200 ms
CPU → GPU transfer   80 ms
GPU inference        50 ms
GPU → CPU transfer   70 ms
Postprocessing       50 ms
Network              50 ms
                    -----
Total               500 ms
```

The model itself only takes:

```text
50 ms
```

The problem is everything around it.

---

#  The Mental Model to Use in Interviews

When an interviewer says:

> "Your ML application is slow. What would you check?"

Think:

```text
                    APPLICATION SLOW
                           │
          ┌────────────────┼────────────────┐
          ↓                ↓                ↓
         CPU              Memory           GPU
          │                │                │
      CPU-bound       Memory-bound      GPU-bound
          │                │                │
          └────────────────┼────────────────┘
                           ↓
                          I/O
                           │
                      I/O-bound
                           │
                           ↓
                        Network
                           │
                     Network-bound
                           │
                           ↓
                        Overhead
                           │
                  Data transfer
                  Serialization
                  Scheduling
                           │
                           ↓
                      Containers
                           │
                 ┌─────────┴─────────┐
                 ↓                   ↓
           CPU throttling       Memory limit
                                     ↓
                                   OOM
```

The key question is:

> **"What resource is the application waiting for or running out of?"**

That one question connects almost everything you've been learning.

### One-line definitions to memorize

```text
CPU-bound
→ CPU is the main bottleneck.

Memory-bound
→ Memory capacity/access is the main bottleneck.

GPU-bound
→ GPU computation is the main bottleneck.

I/O-bound
→ Application spends much time waiting for storage/database/file I/O.

Network-bound
→ Network communication is the main bottleneck.

Overhead
→ Extra cost required around the useful work.

Data-transfer overhead
→ Time/cost spent moving data between components.

Too many workers
→ More execution units competing for limited resources.

Worker memory usage
→ Memory consumed by each worker, including model/runtime/data.

CPU throttling
→ Container is restricted from using as much CPU as it wants.

Memory limit
→ Maximum memory allowed to a container; exceeding it can lead to OOM/OOMKilled.
```

These are exactly the vocabulary you should use when **debugging ML systems in production**, rather than only knowing theoretical computer architecture.




# 32. The Interview Mental Model

When an interviewer asks:

> "Why is my ML API slow?"

Don't immediately answer:

> "Use a faster GPU."

Think through the entire system:

```text
                    API SLOW
                       │
       ┌───────────────┼────────────────┐
       ↓               ↓                ↓
      CPU             RAM              GPU
       │               │                │
    Workers         Memory            VRAM
    Threads         Pressure          Utilization
    Scheduling      Swapping          Data Transfer
       │               │                │
       └───────────────┼────────────────┘
                       ↓
                    Network
                       │
                    I/O
                       │
                    Storage
                       │
                    Database
```

Then ask:

```text
Is it CPU-bound?
Is it memory-bound?
Is it GPU-bound?
Is it I/O-bound?
Is it network-bound?
Is there too much overhead?
Is there CPU/GPU data-transfer overhead?
Are there too many workers?
Are workers consuming too much memory?
Are containers being CPU-throttled?
Are containers hitting memory limits?
```

That is the kind of thinking that makes these concepts **useful for MLOps**, rather than just memorized definitions.




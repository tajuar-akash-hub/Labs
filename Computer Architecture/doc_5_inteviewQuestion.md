## 1. CPU, Core, Thread

### Q1. What is the difference between a CPU, core, and thread?

**Good interview answer:**

> A CPU is the processor, a core is an individual physical execution unit inside the CPU, and a thread is an execution flow that can be scheduled onto a CPU core. A multi-core CPU can execute multiple threads concurrently.

---

### Q2. If a machine has 8 cores and 16 threads, does it have 16 CPUs?

**Expected answer:**

> It has 8 physical CPU cores and 16 logical processors, usually because of SMT/Hyper-Threading. The 16 logical processors do not provide the same performance as 16 physical cores.

---

### Q3. If my ML inference server has 8 CPU cores, can I safely run 8 worker processes?

**Critical point:** **Not necessarily.**

You need to consider:

```text
CPU cores
+
number of workers
+
threads per worker
+
workload
+
memory
+
I/O
```

For example:

```text
8 cores
8 workers
4 threads each

Potentially:
8 × 4 = 32 runnable threads
```

That can cause contention depending on the workload.

---

# 2. CPU vs GPU

### Q4. Why are GPUs commonly used for deep learning?

**Expected answer:**

> Deep learning involves a large number of mathematical operations that can be performed in parallel. GPUs contain many parallel processing units and are optimized for high-throughput numerical computation, making them well suited for tensor and matrix operations.

---

### Q5. If a GPU is faster than a CPU, why don't we use GPUs for everything?

Because GPU computation has costs and constraints.

```text
CPU
→ general-purpose
→ low-latency diverse workloads
→ operating-system tasks
→ branching/control-heavy workloads

GPU
→ highly parallel workloads
→ high throughput
→ ML/tensor computation
→ requires data transfer and specialized execution
```

A simple API server may not benefit from GPU acceleration.

---

### Q6. Why can GPU utilization be low even when an ML application is slow?

This is a very good MLOps troubleshooting question.

Possible causes:

```text
CPU bottleneck
     ↓
Data preprocessing too slow
     ↓
GPU waits

OR

Small batches
     ↓
GPU cannot stay busy

OR

CPU ↔ GPU data transfer
     ↓
Overhead

OR

I/O bottleneck
     ↓
GPU waits for data
```

So:

> **Low GPU utilization does not necessarily mean the GPU is the problem.**

---

# 3. Memory

### Q7. Why is RAM important for an ML inference server?

Because the server needs memory for things such as:

```text
Model
+
Python runtime
+
Libraries
+
Input data
+
Intermediate tensors
+
Multiple requests
+
Multiple workers
```

If memory becomes insufficient:

```text
RAM pressure
   ↓
Swapping / reclaim
   ↓
Latency increases
   ↓
Possible OOM
   ↓
Process/container killed
```

---

### Q8. Why does running multiple ML workers increase memory usage?

Suppose:

```text
Model = 2 GB
```

and you run:

```text
4 workers
```

If every worker has its own model copy, you could approach:

```text
2 GB × 4 = 8 GB
```

plus the runtime and other memory.

This is a common production consideration.

---

### Q9. Why doesn't "the model is only 2 GB" mean the server only needs 2 GB RAM?

Because the model isn't the only thing consuming memory.

For example:

```text
Model             2 GB
Python            0.5 GB
Framework         1 GB
Runtime overhead  0.5 GB
Requests          1 GB
Other processes   1 GB
-----------------------
Total             ~6 GB
```

The exact values depend on the workload.

---

# 4. Virtual Memory

### Q10. What is virtual memory, and why does Linux use it?

**Good answer:**

> Virtual memory gives each process its own virtual address space. Linux and the CPU's memory-management hardware translate virtual addresses to physical memory. This provides isolation, protection, and flexible memory management.

This is one of the most important architecture questions for Linux/MLOps.

---

### Q11. Two processes both use address `0x1000`. Can they access the same memory?

**Not necessarily.**

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

Virtual addresses are process-specific.

---

### Q12. What happens when a process runs out of memory?

A good answer should mention:

```text
Memory allocation request
        ↓
Linux memory management
        ↓
Available memory?
   ┌────┴────┐
   │         │
  Yes        No
   │         │
Allocate   Reclaim / swap /
           eventually OOM
```

In containers, you should also understand **cgroup memory limits**.

---

# 5. Cache

### Q13. Why does CPU cache matter for ML workloads?

Because CPUs repeatedly access data.

If frequently accessed data is already in cache:

```text
CPU → Cache → Data
```

If not:

```text
CPU → L1 miss
    → L2 miss
    → L3 miss
    → RAM
```

RAM access is much slower than cache access.

For ML, memory access patterns can significantly affect CPU preprocessing and inference performance.

---

### Q14. What is a cache miss?

> A cache miss occurs when the CPU requests data that isn't available in the relevant cache level, requiring it to retrieve the data from a lower level of the memory hierarchy.

---

# 6. CPU Scheduling and MLOps

### Q15. Your Kubernetes node has 4 CPU cores, but you run 20 containers. How is that possible?

Because containers are not physical CPUs.

The Linux scheduler can time-share CPU resources among many runnable processes/threads.

```text
4 CPU cores
     ↓
Linux scheduler
     ↓
Many runnable processes
     ↓
Time sharing
```

But 20 CPU-intensive workloads competing for 4 cores can cause contention.

---

### Q16. What happens if a container requests 1 CPU but the node has only 0.5 CPU available?

In Kubernetes, this becomes a scheduling/resource-management issue depending on **requests, limits, allocatable capacity, and actual usage**.

The important interview concept is:

> Kubernetes CPU resources are ultimately backed by the host's CPU scheduling mechanisms.

---

# 7. Containers

### Q17. Does Docker create a virtual CPU for every container?

**No.**

Containers generally share the host kernel and host CPU resources.

```text
Physical CPU
     ↓
Linux Kernel
     ↓
┌────────────┬────────────┬────────────┐
│ Container A│ Container B│ Container C│
│ Process    │ Process    │ Process    │
└────────────┴────────────┴────────────┘
```

Linux controls resource usage using mechanisms such as **cgroups**.

---

### Q18. What is the difference between a VM and a container from a CPU architecture perspective?

```text
VM:

Hardware
   ↓
Hypervisor
   ↓
Virtual CPU
   ↓
Guest OS
   ↓
Application
```

Container:

```text
Hardware
   ↓
Host Linux Kernel
   ↓
Container process
```

A VM virtualizes hardware resources more completely.

A container isolates processes while sharing the host kernel.

---

# 8. System Calls

### Q19. Why can't a normal ML application directly access hardware?

Because applications normally run in user mode.

They request privileged operations from the kernel through system calls.

```text
ML Application
      ↓
User Mode
      ↓
System Call
      ↓
Kernel
      ↓
Hardware / Driver
```

This is important when understanding Linux and device access.

---

### Q20. When a Python application reads a file, does Python directly control the SSD?

**No.**

A simplified path is:

```text
Python
  ↓
Python runtime
  ↓
OS system call
  ↓
Linux kernel
  ↓
Filesystem
  ↓
Storage driver
  ↓
Storage device
```

This is a very useful mental model for MLOps.

---

# 9. Networking + Architecture

### Q21. What happens inside a Linux machine when your FastAPI server receives an HTTP request?

This is an excellent MLOps interview question.

A simplified path:

```text
Network
   ↓
NIC
   ↓
Linux kernel
   ↓
Network stack
   ↓
TCP
   ↓
Socket
   ↓
FastAPI process
   ↓
Application thread
```

The NIC and CPU cooperate, while the Linux kernel manages the networking stack.

---

### Q22. What is a socket?

> A socket is an operating-system abstraction that applications use to communicate through a network or locally.

For a TCP service:

```text
IP + Port + Protocol
```

might identify an endpoint.

Example:

```text
10.0.1.20:8000
```

---

# 10. Performance Troubleshooting

These are the questions that become **very relevant to an actual MLOps Engineer**.

### Q23. Your ML inference API suddenly has high latency. CPU is at 100%. What would you investigate?

Don't immediately increase CPU.

Investigate:

```text
CPU utilization
CPU throttling
Number of workers
Thread count
Request concurrency
Model computation
Data preprocessing
Memory pressure
Cache behavior
I/O
```

Then profile the application.

---

### Q24. CPU is at 20%, RAM is at 95%, and API latency is extremely high. What might be happening?

Potentially:

```text
High memory pressure
      ↓
Memory reclaim
      ↓
Possibly swapping
      ↓
Slow memory/storage operations
      ↓
High latency
```

You would investigate memory usage, swap, OOM events, container limits, and application behavior.

---

### Q25. CPU is only 30%, but your application is slow. Does that mean you have plenty of CPU capacity?

**No.**

30% overall CPU utilization can hide a bottleneck.

For example:

```text
8 cores

Core 1 → 100%
Core 2 → 100%
Core 3 → 10%
Core 4 → 10%
...
```

Overall utilization could look moderate while a single-threaded workload is bottlenecked.

You need to inspect **per-core utilization** and workload characteristics.

---

# 11. A Very Important ML Question

### Q26. Why can increasing batch size improve GPU throughput but increase inference latency?

Because larger batches allow the GPU to process more data efficiently.

```text
Batch = 1
→ low latency
→ potentially poor GPU utilization

Batch = 32
→ better GPU utilization
→ higher throughput
→ potentially higher waiting time
```

This creates a production trade-off:

```text
Batch size
    ↓
Throughput vs Latency
```

This is directly relevant to model serving.

---

# 12. CPU vs GPU Memory

### Q27. What is the difference between RAM and GPU VRAM?

```text
CPU
 ↓
RAM

GPU
 ↓
VRAM
```

The CPU primarily uses system RAM, while the GPU primarily uses its own device memory.

For an ML model:

```text
Model
 ↓
CPU RAM
```

versus:

```text
Model
 ↓
GPU VRAM
```

When data moves between CPU memory and GPU memory, transfer overhead can matter.

---

# 13. The Most Critical Scenario Questions

If you're preparing specifically for an **MLOps Engineer interview**, I would prioritize these:

### Scenario 1

> Your Kubernetes ML inference pod is using 100% CPU and latency is increasing. How would you investigate?

Think:

```text
CPU usage
↓
Per-core usage
↓
CPU limits/throttling
↓
Worker/thread count
↓
Concurrency
↓
Model inference
↓
Profiling
```

---

### Scenario 2

> Your ML container keeps getting OOMKilled. What could be causing it?

Think:

```text
Model size
+
Multiple workers
+
Request concurrency
+
Memory leak
+
Intermediate tensors
+
Container memory limit
```

---

### Scenario 3

> GPU utilization is only 30%, but inference latency is high. What would you investigate?

Think:

```text
CPU preprocessing
GPU data transfer
Batch size
I/O
GPU synchronization
Model architecture
Concurrency
CPU bottleneck
```

---

### Scenario 4

> A server has 16 CPU cores, but your application uses only one core. Why?

Possible reason:

```text
Single-threaded workload
       OR
Python/GIL limitations for CPU-bound Python threads
       OR
Application/framework configuration
       OR
Only one worker
```

Then ask:

> How would you improve it?

Potential approaches:

```text
Multiple processes
+
appropriate worker configuration
+
native parallel libraries
+
horizontal scaling
```

The correct solution depends on the workload.

---

# 14. The 15 Questions I Would Memorize

For your current MLOps learning path, focus hardest on these:

| Priority  | Question                                          |
| --------- | ------------------------------------------------- |
| Very High | CPU vs Core vs Thread                             |
| Very High | Process vs Thread                                 |
| Very High | What is virtual memory?                           |
| Very High | User mode vs Kernel mode                          |
| Very High | What is a system call?                            |
| Very High | What is a context switch?                         |
| Very High | How does Linux schedule processes?                |
| Very High | What is a socket?                                 |
| Very High | How does a network packet reach an application?   |
| High      | RAM vs Cache                                      |
| High      | CPU vs GPU                                        |
| High      | Why can GPU utilization be low?                   |
| High      | Why does an ML worker consume significant memory? |
| High      | VM vs Container                                   |
| High      | CPU/memory troubleshooting in Kubernetes          |

### The ultimate mental model

For an MLOps interview, you should be able to explain this without memorizing:

```text
                    HARDWARE
                       │
             ┌─────────┴─────────┐
             │                   │
            CPU                 GPU
             │                   │
          Cores              GPU Cores
             │                   │
          Threads              VRAM
             │
        Linux Kernel
             │
    ┌────────┼─────────┐
    │        │         │
 Process   Memory   Networking
    │        │         │
 Thread   Virtual    Socket
           Memory      │
                      TCP/IP
                        │
                       NIC
                        │
                     Network
                        │
                    Container
                        │
                       Pod
                        │
                    Kubernetes
                        │
                   ML Inference
```



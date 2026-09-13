# CPU Terminology for Beginners


The key mental model is:

```text
                         CPU
                          │
              ┌───────────┴───────────┐
              │                       │
          CPU Cores              Shared resources
              │
        ┌─────┴─────┐
        │           │
   Execution    Registers
     Units
        │
   ┌────┼────┐
   │    │    │
  ALU  FPU  Load/Store
```

## 1. CPU — Central Processing Unit

**Textbook definition:**
The CPU is the primary processor that executes instructions of a computer program.

In simple terms:

> The CPU is the component that fetches, interprets, and executes instructions.

### Analogy

Think of a CPU as a factory.

* Instructions = work orders
* CPU = factory
* Registers = worker's hands
* Execution units = machines that perform different jobs
* Cache = materials kept nearby
* RAM = warehouse

---

## 2. CPU Core

A **core** is an individual processing unit within a CPU that can independently execute instructions.

For example:

```text
CPU
│
├── Core 1
├── Core 2
├── Core 3
└── Core 4
```

A 4-core CPU has four physical processing cores.

### Analogy

CPU = factory
Core = worker inside the factory

```text
Factory
│
├── Worker 1
├── Worker 2
├── Worker 3
└── Worker 4
```

More cores allow the computer to execute more independent work concurrently.

---

## 3. Thread

A **thread** is a sequence of instructions that can be scheduled for execution.

There are two related meanings:

* **Software thread:** a unit of execution created by a program.
* **Hardware thread:** a logical execution context supported by a CPU core.

For example:

```text
4 cores / 8 hardware threads
```

can conceptually look like:

```text
Core 1 → Thread A + Thread B
Core 2 → Thread C + Thread D
Core 3 → Thread E + Thread F
Core 4 → Thread G + Thread H
```

### Analogy

Core = worker
Thread = work queue the worker can keep track of.

---

## 4. Clock Speed

**Clock speed** is the frequency at which a processor's clock operates.

It is usually measured in:

```text
Hz
MHz
GHz
```

For example:

```text
4.5 GHz
```

means approximately 4.5 billion clock cycles per second.

Important:

> A clock cycle is a timing interval. It does not necessarily mean "one instruction."

A single instruction can require multiple cycles, and modern CPUs can execute multiple instructions during overlapping stages.

### Analogy

Imagine a factory bell:

```text
Bell → Work → Bell → Work → Bell → Work
```

The faster the bell rings, the more frequently the factory gets timing opportunities.

But a faster bell does not automatically mean the factory does more useful work. The machines and workflow also matter.

---

## 5. Clock Cycle

A **clock cycle** is one period of the CPU's clock signal.

```text
Clock:
_|‾|_|‾|_|‾|_|‾|_
   ↑   ↑   ↑
 cycles
```

The CPU uses this clock as a timing reference to coordinate operations.

---

## 6. Instruction

An **instruction** is a machine-level operation that tells the CPU what to do.

Examples conceptually include:

```text
ADD
LOAD
STORE
COMPARE
JUMP
```

For example:

```text
ADD R1, R2
```

means approximately:

> Add the values in registers R1 and R2.

---

## 7. Instruction Set

An **instruction set** is the collection of machine instructions supported by a processor architecture.

For example:

```text
ADD
SUB
LOAD
STORE
JUMP
COMPARE
...
```

Think of it as the CPU's **vocabulary**.

---

## 8. ISA — Instruction Set Architecture

This is one of the most important terms.

**ISA** defines the interface between software and the processor.

It specifies things such as:

* available instructions
* registers visible to software
* data types
* addressing modes
* memory behavior
* instruction encoding

Common ISAs include:

```text
x86-64
ARM64
RISC-V
```

### Analogy

ISA = **language understood by the CPU**

For example:

```text
English → language
x86-64 → instruction language
ARM64 → instruction language
```

---

## 9. Execution Unit

An **execution unit** is a part of a CPU core that performs specific operations.

A modern CPU core can contain several types of execution units.

Conceptually:

```text
CPU Core
│
├── Integer ALU
├── Floating-Point Unit
├── Load/Store Unit
├── Branch Unit
└── Vector/SIMD Units
```

### Analogy

Think of a factory worker with several specialized machines:

```text
Worker
│
├── Addition machine
├── Decimal-calculation machine
├── Loading machine
└── Branch-decision machine
```

Different execution units perform different kinds of work.

---

## 10. ALU — Arithmetic Logic Unit

The **ALU** performs arithmetic and logical operations on integer or logical data.

Examples:

```text
10 + 20
50 - 10
5 > 3
A AND B
A OR B
```

### Analogy

ALU = **calculator + logic machine**

```text
10 + 20
   ↓
 ALU
   ↓
  30
```

The ALU is an execution unit.

---

## 11. FPU — Floating-Point Unit

An **FPU** performs floating-point arithmetic.

For example:

```text
3.14 + 2.71
1.5 × 4.2
```

Modern CPUs typically have specialized hardware for floating-point operations.

### Analogy

ALU = integer calculator
FPU = decimal/scientific calculator

---

## 12. SIMD / Vector Unit

SIMD means:

**Single Instruction, Multiple Data**

It allows one instruction to operate on multiple data elements simultaneously.

For example, conceptually:

```text
Normal:

1 + 10
2 + 20
3 + 30
4 + 40

Four operations
```

With vector/SIMD processing:

```text
[1, 2, 3, 4]
+
[10,20,30,40]
       ↓
[11,22,33,44]
```

This is useful for:

* multimedia
* image processing
* scientific computing
* numerical workloads
* some ML operations

---

## 13. Register

A **register** is a small, high-speed storage location inside the CPU used to hold values, addresses, and other information needed during instruction execution.

Example:

```text
R1 = 10
R2 = 20

ADD R1, R2

R1 = 30
```

Registers are extremely fast but very limited in number and capacity.

### Analogy

Register = **something in the worker's hand**

The worker can access it immediately.

---

## 14. General-Purpose Register

A **general-purpose register (GPR)** is a register that can be used for many types of general computation.

For example, an architecture might provide registers such as:

```text
RAX
RBX
RCX
RDX
```

in x86-64.

The exact names depend on the ISA.

---

## 15. Program Counter / Instruction Pointer

The **program counter (PC)** keeps track of the address of the next instruction to be fetched.

On x86, it is commonly called the **instruction pointer (RIP)**.

Conceptually:

```text
Instruction 1
Instruction 2
Instruction 3  ← PC
Instruction 4
Instruction 5
```

After execution:

```text
Instruction 1
Instruction 2
Instruction 3
Instruction 4  ← PC
Instruction 5
```

### Analogy

PC = **bookmark in a book**

It tells the CPU where to continue reading.

---

## 16. Stack Pointer

The **stack pointer (SP)** points to the current location of the program's stack.

The stack is used for things such as:

* function calls
* local variables
* saved state

### Analogy

Stack = pile of plates.

```text
Plate 3
Plate 2
Plate 1
-------
```

The stack pointer tells you where the top of the stack currently is.

---

## 17. Flags / Status Register

CPUs maintain status information about operations.

For example, after:

```text
5 - 5
```

the result is zero.

A CPU may set a **zero flag** to indicate that.

Other flags can represent things such as:

* zero
* carry
* overflow
* negative/sign

These flags can influence conditional branches.

---

## 18. Control Unit

The **control unit** coordinates CPU operations.

It helps determine:

```text
What instruction is this?
What data does it need?
Which operation should happen?
Where should the result go?
```

### Analogy

Control unit = **factory manager**

It coordinates the workers and machines.

---

## 19. Datapath

The **datapath** is the collection of hardware components and connections through which data moves and gets processed.

It includes things such as:

```text
Registers
ALUs
FPUs
Multiplexers
Internal data paths
```

### Analogy

Datapath = **factory's production line**

The control unit decides what should happen.

The datapath is where the actual data processing happens.

---

## 20. Fetch–Decode–Execute Cycle

This is a fundamental CPU concept.

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

Get the instruction from memory/cache.

### Decode

Determine what the instruction means.

### Execute

Perform the required operation.

For example:

```text
ADD R1, R2
```

Conceptually:

```text
Fetch ADD instruction
       ↓
Decode "ADD"
       ↓
Read R1 and R2
       ↓
ALU adds them
       ↓
Store result
```

Modern processors overlap many instructions using pipelines, so this simple diagram is a teaching model rather than a literal description of every CPU cycle.

---

## 21. Instruction Decoder

The **instruction decoder** interprets the binary machine instruction and determines what operation it represents.

For example:

```text
Binary instruction
       ↓
 Instruction Decoder
       ↓
"Perform ADD"
       ↓
Appropriate execution unit
```

### Analogy

Decoder = **translator**

It translates the machine instruction into control information for the CPU.

---

## 22. Cache

A **cache** is a small, fast memory used to keep frequently or recently needed data and instructions close to the CPU.

Typical CPU caches:

```text
L1
L2
L3
```

Generally:

```text
L1 → fastest, smallest
L2 → larger, slower
L3 → larger, slower still
```

### Analogy

```text
Register → in your hand
L1       → on your desk
L2       → nearby shelf
L3       → nearby room
RAM      → warehouse
SSD      → storage building
```

The farther away the information is, the longer it generally takes to access.

---

## 23. Cache Line

A CPU cache doesn't usually move data one individual byte at a time.

It transfers data in blocks called **cache lines**.

A common cache-line size is:

```text
64 bytes
```

although the exact size depends on the architecture.

### Analogy

Instead of bringing one book from a shelf, you bring an entire small box of related books because you expect to need them.

---

## 24. Cache Hit

A **cache hit** occurs when the CPU looks for data and finds it in the cache.

```text
CPU
 ↓
Cache
 ↓
Found
```

Fast.

---

## 25. Cache Miss

A **cache miss** occurs when the requested data isn't present in the relevant cache.

```text
CPU
 ↓
Cache
 ↓
Not found
 ↓
Lower-level cache / RAM
```

This takes longer.

---

## 26. Memory Controller

The **memory controller** manages communication between the CPU and system memory such as RAM.

Conceptually:

```text
CPU
 |
Memory Controller
 |
RAM
```

Modern processors commonly integrate the memory controller into the CPU package.

---

## 27. RAM — Main Memory

RAM is the computer's primary working memory.

Programs and data currently being used are stored there.

```text
SSD
 ↓
RAM
 ↓
CPU Cache
 ↓
Registers
 ↓
Execution Units
```

This is a simplified representation of the path data may travel.

---

## 28. Bus / Interconnect

An **interconnect** provides communication between components.

Historically, computers used various shared buses. Modern CPUs use sophisticated interconnects and point-to-point links.

Conceptually:

```text
CPU ←→ RAM
CPU ←→ GPU
CPU ←→ I/O
```

### Analogy

Interconnect = **roads connecting different parts of a city**.

---

## 29. Pipeline

A CPU pipeline divides instruction processing into stages so multiple instructions can be in different stages simultaneously.

Instead of:

```text
Instruction 1
Fetch → Decode → Execute

Instruction 2
Fetch → Decode → Execute
```

a pipeline can overlap them:

```text
             Cycle
             1   2   3   4
Instruction 1 F   D   E
Instruction 2     F   D   E
Instruction 3         F   D   E
```

### Analogy

A car factory has multiple stations:

```text
Station 1 → Station 2 → Station 3
Painting  → Engine    → Testing
```

While one car is being tested, another can be having its engine installed.

---

## 30. Branch Prediction

Programs frequently contain decisions:

```c
if (x > 10) {
    ...
}
```

The CPU may need to determine which instruction path will execute next.

A **branch predictor** predicts the likely path.

```text
if condition
     |
     +---- likely path
     |
     +---- unlikely path
```

The CPU can start preparing the predicted path before it knows the final result.

If it predicts incorrectly, the CPU has to discard some speculative work.

---

## 31. Speculative Execution

**Speculative execution** means executing instructions based on a prediction before the CPU knows with certainty that those instructions are needed.

Example:

```text
if (condition):
      A
else:
      B
```

CPU predicts:

```text
condition → TRUE
```

and starts processing `A`.

If the prediction is correct, time is saved.

If wrong, the speculative work is discarded and the correct path is processed.

---

## 32. Out-of-Order Execution

Modern CPUs do not necessarily execute instructions strictly in the order they appear in the program.

They can execute independent instructions earlier when their required resources are available, while still preserving the program's correct architectural behavior.

Example:

```text
Instruction 1 → waiting for data
Instruction 2 → ready
Instruction 3 → ready
```

The CPU may execute internally:

```text
Instruction 2
Instruction 3
Instruction 1
```

### Analogy

A worker has three tasks:

```text
Task A → waiting for delivery
Task B → ready
Task C → ready
```

The worker doesn't sit doing nothing. They do B and C first.

---

## 33. Superscalar CPU

A **superscalar processor** can issue and execute multiple instructions in the same clock cycle when the instructions and available hardware allow it.

Conceptually:

```text
Clock cycle
    |
    +── Instruction A → ALU
    +── Instruction B → Load/Store
    +── Instruction C → FPU
```

This is one reason:

> 4 GHz does not mean "4 billion instructions per second."

Modern CPUs can process multiple instructions per cycle, while some instructions require multiple cycles.

---

## 34. IPC — Instructions Per Cycle

**IPC** measures how many instructions a processor completes or retires per clock cycle under a particular workload and measurement definition.

A simplified performance relationship is:

```text
Performance ≈ Clock Speed × IPC
```

This is only a rough model because real performance depends on many other factors.

That's why:

```text
CPU A → 4.0 GHz
CPU B → 4.5 GHz
```

doesn't necessarily mean CPU B is faster.

CPU A might have substantially better architecture and IPC.

---

## 35. ISA vs Microarchitecture

This distinction is extremely important.

### ISA

What the CPU **promises to software**.

```text
x86-64
ARM64
RISC-V
```

### Microarchitecture

How the CPU **internally implements that ISA**.

For example:

```text
ISA
 ↓
x86-64
 ↓
Different CPU implementations
```

Two processors can support the same ISA while having very different internal designs.

### Analogy

ISA = rules of a language
Microarchitecture = how different people physically produce/process that language

---

## 36. Physical Core vs Logical Processor

Suppose your computer says:

```text
8 cores
16 logical processors
```

It means:

```text
Physical cores = 8
Logical processors = 16
```

Technologies such as SMT allow a physical core to expose multiple hardware threads.

Intel commonly calls its implementation **Hyper-Threading**.

---

## 37. SMT — Simultaneous Multithreading

SMT allows one physical CPU core to maintain multiple hardware threads and use otherwise idle execution resources more effectively.

Conceptually:

```text
Physical Core
     |
 +---+---+
 |       |
Thread A Thread B
```

Important:

> Two hardware threads on one core are **not equivalent to two physical cores**.

---

## 38. CPU Socket

A **CPU socket** is the physical interface on a motherboard where a processor is installed.

For a normal desktop:

```text
Motherboard
     |
   Socket
     |
    CPU
```

A server can have multiple CPU sockets:

```text
Server
 |
 +── CPU 1
 |
 +── CPU 2
```

This is called a **multi-socket system**.

---

## 39. CPU Package

The **CPU package** is the physical packaged component installed into the motherboard socket.

It can contain:

* CPU cores
* cache
* memory controllers
* I/O controllers
* other components

The exact organization depends on the processor.

---

## 40. Die

A **die** is a piece of semiconductor material containing integrated circuitry.

A CPU package can contain one or multiple dies.

Conceptually:

```text
CPU Package
 |
 +-- Die
 |    ├── CPU cores
 |    └── Cache
 |
 +-- Other die(s)
```

Modern CPUs can use multiple chiplets/dies.

---

## 41. Chiplet

A **chiplet** is a smaller semiconductor die that forms part of a larger processor.

Instead of manufacturing everything as one huge die:

```text
Traditional idea:

+-----------------------+
| Everything on one die |
+-----------------------+
```

A chiplet-based design might look like:

```text
CPU Package
 |
 +── Compute Chiplet
 +── Compute Chiplet
 +── I/O Die
```

This approach is common in modern high-performance processors.

---

## 42. Integrated GPU

Some CPUs contain graphics hardware on the same processor package or silicon design.

This is commonly called an **integrated GPU (iGPU)**.

```text
Processor
 |
 +── CPU cores
 +── GPU
 +── Cache
 +── Memory controller
```

A discrete GPU is a separate graphics processor.

---

## 43. TDP

**TDP = Thermal Design Power**

It is a thermal/power design specification used by manufacturers to describe the cooling and power characteristics a system should be designed around.

Do not interpret TDP as:

> "This CPU always consumes exactly X watts."

Actual power consumption can vary substantially depending on workload and processor configuration.

---

## 44. Instruction Latency

**Latency** is the time or number of cycles before an operation's result becomes available.

For example:

```text
Operation
   ↓
Several cycles
   ↓
Result available
```

---

## 45. Instruction Throughput

**Throughput** describes how frequently operations can be completed once a pipeline is running.

Latency and throughput are different.

### Analogy

A factory:

```text
Latency = time for one product to finish
Throughput = products produced per hour
```

A factory can have relatively high latency for an individual product but high overall throughput.

---

## 46. Interrupt

An **interrupt** is a mechanism that causes the CPU to temporarily redirect execution to handle an event that requires attention.

For example:

```text
CPU is executing program
        ↓
Network packet arrives
        ↓
Interrupt/event
        ↓
CPU handles event
        ↓
CPU continues
```

Operating systems rely heavily on interrupts.

---

## 47. Exception

An **exception** is a synchronous event caused by the execution of an instruction.

For example:

```text
Program performs invalid operation
          ↓
CPU detects problem
          ↓
Exception
          ↓
Operating system handles it
```

Interrupts and exceptions are related but not identical.

---

## 48. Privilege Levels

Modern CPUs provide different privilege levels so that ordinary applications cannot freely perform privileged operations.

Simplified:

```text
User Mode
   ↓
Applications

Kernel Mode
   ↓
Operating System
```

For example, a normal application cannot directly control hardware however it wants.

It requests services from the operating system.

This becomes extremely important for:

* Linux
* system calls
* containers
* security
* virtualization

---

## 49. System Call

A **system call** is a controlled interface through which a user-space program requests a service from the operating system kernel.

For example:

```text
Python program
      ↓
System call
      ↓
Linux kernel
      ↓
Hardware
```

Examples include operations related to:

```text
files
processes
memory
networking
```

This is one of the bridges between **CPU architecture and Linux**.

---

## 50. Virtualization

CPU virtualization allows a physical machine to support virtual machines efficiently.

Conceptually:

```text
Physical CPU
      ↓
Hypervisor
      ↓
+-------------+-------------+
| Virtual CPU | Virtual CPU |
|     VM 1    |     VM 2    |
+-------------+-------------+
```

Modern CPUs provide hardware virtualization features to support this.

---

# The Complete Beginner Mental Model

If you want to understand all these terms together, keep this picture in your head:

```text
                         CPU
                          │
              ┌───────────┴───────────┐
              │                       │
            Core                    Core
              │                       │
       ┌──────┼────────┐       ┌──────┼────────┐
       │      │        │       │      │        │
   Registers ALU      FPU   Registers ALU      FPU
       │      │        │       │      │        │
       └──────┴────────┘       └──────┴────────┘
              │                       │
           L1 Cache                L1 Cache
              │                       │
           L2 Cache                L2 Cache
              │                       │
              └──────────┬────────────┘
                         │
                      L3 Cache
                         │
                  Memory Controller
                         │
                        RAM
                         │
                       Storage
```

And around the CPU:

```text
                         CPU
                          │
          ┌───────────────┼───────────────┐
          │               │               │
         RAM             GPU             I/O
                                          │
                              ┌───────────┼───────────┐
                              │           │           │
                             NIC         USB       Storage
```

# The Terms to Memorize First

Don't try to memorize all 50 terms immediately. For a Linux → Docker → Kubernetes → MLOps path, learn these first:

```text
1. CPU
2. Core
3. Thread
4. Clock
5. Clock cycle
6. Instruction
7. ISA
8. Register
9. ALU
10. Execution Unit
11. Control Unit
12. Program Counter
13. Cache
14. L1 / L2 / L3
15. RAM
16. Fetch
17. Decode
18. Execute
19. Pipeline
20. Branch Prediction
21. Out-of-Order Execution
22. Virtual Memory
23. Process
24. System Call
25. User Mode
26. Kernel Mode
27. Interrupt
28. CPU Socket
29. CPU Package
30. Microarchitecture
```

The most important hierarchy to understand is:

```text
CPU
 └── Core
      ├── Registers
      ├── Execution Units
      │    ├── ALU
      │    ├── FPU
      │    ├── Load/Store Unit
      │    └── SIMD/Vector Unit
      │
      ├── L1 Cache
      └── L2 Cache

Multiple cores
      ↓
     CPU
      ↓
    L3 Cache
      ↓
     RAM
      ↓
   Storage
```


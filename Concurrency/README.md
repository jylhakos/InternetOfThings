# Concurrency

## Table of Contents

1. [Overview](#overview)
2. [Folder Structure](#folder-structure)
3. [Vibe Coding for IoT with Concurrency](#vibe-coding-for-iot-with-concurrency)
   - [What Is Vibe Coding](#what-is-vibe-coding)
   - [Rapid Prototyping](#rapid-prototyping)
   - [Challenges in IoT Concurrency](#challenges-in-iot-concurrency)
   - [Prompt Sequence Strategy](#prompt-sequence-strategy)
   - [Concurrency Primitives Illustrated](#concurrency-primitives-illustrated)
   - [AI Agents for Concurrent Code](#ai-agents-for-concurrent-code)
4. [Language Summaries](#language-summaries)
   - [C++](#c)
   - [Go](#go)
   - [Java](#java)
   - [JavaScript and TypeScript](#javascript-and-typescript)
   - [Python](#python)
5. [References](#references)

---

## Overview

Concurrency refers to the ability of a program to manage multiple tasks at once. Concurrent execution alternates doing a little of each task until all tasks are completed.

In IoT systems, concurrency is not optional — a device must simultaneously read sensors, process data, trigger actuators, and transmit telemetry, all under real-time, resource, and safety constraints. Unlike desktop applications, IoT software runs on resource-constrained hardware where timing deadlines are hard, memory is limited, and energy consumption matters. The Linux scheduler provides preemptive multitasking on Linux-based boards such as the Raspberry Pi, and each language in this repository exposes its own abstraction over the underlying OS threading model.

---

## Folder Structure

```
◈ Concurrency/
├── ▸ C++/
│   ├── ▸ examples/
│   │   ├── ▸ 01_threads/          ▪ main.cpp  ▪ CMakeLists.txt
│   │   ├── ▸ 02_mutex/            ▪ main.cpp  ▪ CMakeLists.txt
│   │   ├── ▸ 03_atomic/           ▪ main.cpp  ▪ CMakeLists.txt
│   │   ├── ▸ 04_async_future/     ▪ main.cpp  ▪ CMakeLists.txt
│   │   ├── ▸ 05_condition_variable/ ▪ main.cpp  ▪ CMakeLists.txt
│   │   └── ▸ 06_iot_sensor_hub/   ▪ main.cpp  ▪ CMakeLists.txt
│   ├── ▪ CMakeLists.txt
│   └── ▪ README.md
├── ▸ Go/
│   ├── ▸ channels/                ▪ main.go  ▪ go.mod
│   ├── ▸ goroutines/              ▪ main.go  ▪ go.mod
│   ├── ▸ synchronized/            ▪ main.go  ▪ go.mod
│   └── ▪ README.md
├── ▸ Java/
│   └── ▪ README.md
├── ▸ Javascript/
│   ├── ▸ src/
│   │   └── ▪ race-condition.ts
│   ├── ▪ package.json
│   ├── ▪ tsconfig.json
│   └── ▪ README.md
├── ▸ Python/
│   ├── ▸ asyncio/                 ▪ FastAPI async web application
│   ├── ▸ Celery/                  ▪ Distributed task queue
│   ├── ▸ Redis Queue/             ▪ Redis-backed worker queue
│   └── ▪ README.md
└── ▪ README.md
```

---

## Vibe Coding for IoT with Concurrency

### What Is Vibe Coding

Vibe Coding is a development style where you describe a feature in natural language and an AI model generates the implementation. The term captures the idea of guiding AI through intent and constraints rather than typing every line by hand.

For IoT concurrency, Vibe Coding works best as a collaboration model: use AI as an assistant for boilerplate and scaffolding, but retain control over architectural decisions, particularly regarding task orchestration, interrupt handling, and memory management. AI cannot inspect your circuit board, your RTOS configuration, or your linker script — those decisions remain the developer's responsibility.

### Rapid Prototyping

AI agents can instantly create boilerplate code for LED toggling, peripheral initialization, sensor polling loops, and timer callback structures, allowing developers to focus on high-level system architecture. For simple, well-understood routines such as PWM setup, I2C read loops, or GPIO toggling, AI-generated code often works without modification. This dramatically shortens the feedback loop in early prototyping cycles.

### Challenges in IoT Concurrency

IoT software development operates under real-time, resource, and safety constraints that most general-purpose AI training data does not cover:

- **Hardware-specific details** — most AI models are trained on general-purpose code and lack access to your specific MCU, RTOS, or linker configuration. Generated code may compile but violate timing deadlines or misuse hardware peripherals.
- **Energy-sensitive devices** — AI-generated code may introduce unnecessary busy-waiting or redundant wake cycles, significantly shortening battery life.
- **Timing deadlines** — concurrent systems have strict scheduling requirements. A missed deadline in a sensor-fusion pipeline or a network-transmission window is not just a performance issue; it can be a safety failure.
- **Subtle regressions** — relying solely on "vibes" for complex, parallelized tasks such as asynchronous data processing from multiple sensors can lead to race conditions and code that is extremely difficult to debug on hardware without a debugger.

### Prompt Sequence Strategy

Concurrency is error-prone. Use an incremental **Prompt Sequence** to build the algorithm rather than asking for the entire system at once.

**Step 1 — The Skeleton.** Ask for the basic structure first, before adding complexity.

> "Scaffold a TypeScript class for a sliding window rate limiter."

**Step 2 — Describe behavior and constraints.** Instead of listing every variable, describe the runtime behavior and the environmental constraints the code must satisfy.

> "This runs on a Raspberry Pi Zero 2W with 512 MB RAM. The sensor fires at 10 Hz and the network publish interval is 1 second. The buffer must not allocate on the heap after initialization."

**Step 3 — Direct the AI toward thread safety.** Explicitly ask the model to reason about concurrent access. Do not assume it will do so automatically.

> "Update this code to be thread-safe. I'm worried about multiple requests hitting the same window at the exact same millisecond."

**Step 4 — Target the concurrency boundary first.** Ask for the concurrency handling between sensor acquisition and network transmission before adding business logic.

> "Add a producer-consumer queue between the sensor thread and the network thread. The producer must never block the sensor loop."

If a prompt is too loose, the AI will make assumptions — often leading to insecure, non-functional, or non-deterministic concurrent code. Use structured, constraints-based prompts rather than vague, open-ended requests to ensure reliability.

### Concurrency Primitives Illustrated

The three most important low-level concurrency primitives appear across all languages in this repository. Below are minimal C++ illustrations.

**Threads** — the unit of concurrent execution.

```cpp
#include <iostream>
#include <thread>
using namespace std;

void func(int x) {
    cout << "Inside thread " << x << endl;
}

int main() {
    thread th(&func, 100);
    th.join();
    cout << "Outside thread" << endl;
    return 0;
}
```

**Mutex (Mutual Exclusion)** — ensures only one thread executes a critical section at a time.

```cpp
#include <mutex>

int accum = 0;
mutex accum_mutex;

void square(int x) {
    int temp = x * x;
    accum_mutex.lock();
    accum += temp;      // protected: only one thread at a time
    accum_mutex.unlock();
}
```

**Atomic** — lock-free thread-safe operations for simple scalars, using hardware-level CPU instructions (e.g., `LDREX`/`STREX` on ARM Cortex-A).

```cpp
#include <atomic>

atomic<int> accum(0);

void square(int x) {
    accum += x * x;    // no mutex needed; hardware guarantees atomicity
}
```

### AI Agents for Concurrent Code

AI agents are specifically designed to handle complex development tasks, including generating multithreaded and concurrent code across a local repository. Three tools are particularly relevant for IoT concurrency work:

| Agent | Description |
|---|---|
| **Windsurf Editor** | An AI-powered IDE featuring "Flow" (agentic behavior) that understands and anticipates coding needs in C++. Handles large-scale project navigation and generates multiline suggestions for complex concurrent functions. |
| **Claude Code** | A terminal-based agent from Anthropic that analyzes entire codebases to help build, debug, and refactor features. High-performing for large projects (1M+ lines) using models such as Claude 3.5 Sonnet. |
| **Cursor** | A popular agentic IDE that integrates with VS Code. Uses agentic capabilities to navigate large codebases and is recommended for complex C++ projects requiring multi-file edits. |

While these agents can produce functional concurrent code, C++ concurrency remains challenging due to risks like race conditions, priority inversion, and high-performance requirements. Always validate AI-generated concurrent code with thread sanitizers (`-fsanitize=thread`) and hardware-in-the-loop testing.

---

## Language Summaries

### C++

> See [C++/README.md](C++/README.md) for the full reference.

The C++ folder covers concurrency on Linux and Raspberry Pi using the C++17 standard library. `std::thread` maps directly to POSIX `pthread_create`, giving low-latency, low-overhead threads suited to edge devices. Six progressive examples are provided:

| Example | Topic |
|---|---|
| `01_threads` | Spawning and joining `std::thread` instances; thread lifecycle basics |
| `02_mutex` | `std::mutex` and `std::lock_guard` for safe shared-state access |
| `03_atomic` | `std::atomic<T>` for lock-free counters, flags, and status indicators |
| `04_async_future` | `std::async` and `std::future` for non-blocking asynchronous tasks |
| `05_condition_variable` | `std::condition_variable` for producer-consumer event signaling |
| `06_iot_sensor_hub` | Full IoT sensor hub combining all primitives: temperature, humidity, and GPS threads feeding a processor, a network publisher using `std::async`, a lock-free stats monitor, and a concurrent finite state machine (FSM) |

All examples are built with CMake and link with `-pthread`. The IoT sensor hub (`06_iot_sensor_hub`) can be compiled with `-fsanitize=thread` to detect data races during development.

---

### Go

> See [Go/README.md](Go/README.md) for the full reference.

The Go folder demonstrates Go's built-in concurrency model, which differs fundamentally from thread-per-task models. Three sub-packages are provided:

| Package | Topic |
|---|---|
| `goroutines/` | Goroutines — lightweight cooperatively scheduled functions launched with the `go` keyword. The Go scheduler (part of the Go runtime, running in user space) context-switches goroutines across OS threads (M) on logical processors (P). |
| `synchronized/` | `sync.WaitGroup` for coordinating goroutine completion without channels. Goroutines share the same address space, so shared memory must be synchronized. |
| `channels/` | Channels — typed pipes through which goroutines send and receive values. The `<-` operator specifies direction. A send on an unbuffered channel blocks until a receiver is ready, providing implicit synchronization. |

Go's concurrency model is particularly well suited to IoT gateway software (MQTT brokers, HTTP APIs, device coordinators) where thousands of concurrent connections must be managed with minimal memory overhead.

---

### Java

> See [Java/README.md](Java/README.md) for the full reference.

The Java folder covers Java concurrency concepts for IoT applications running on JVM-capable hardware (e.g., Raspberry Pi with Java SE Embedded). Key topics include:

- **Thread lifecycle** — five states: New, Runnable, Running, Waiting/Blocked, Dead/Terminated.
- **Creating threads** — by extending `Thread` (override `run()`) or implementing `Runnable` (preferred, allows extending another class).
- **Thread safety** — protecting shared data so multiple threads can access it without data corruption or inconsistent state.
- **Race conditions** — when the final state of shared data depends on unpredictable thread scheduling order.
- **Deadlocks** — two or more threads permanently blocked, each waiting for a resource held by the other.
- **`java.util.concurrent`** — the foundation of modern Java concurrency, providing thread pools (`ExecutorService`), concurrent collections, high-level locks, and synchronization primitives.

---

### JavaScript and TypeScript

> See [Javascript/README.md](Javascript/README.md) for the full reference.

The Javascript folder covers concurrency in both JavaScript and TypeScript. TypeScript adds static typing and compile-time safety on top of the same underlying JavaScript execution model.

JavaScript uses a single-threaded **run-to-completion** event loop. Each task (job) runs entirely to completion before the next one starts, meaning JavaScript functions cannot be preempted by other JavaScript code. Concurrency is achieved cooperatively through:

- **Promises** — represent the eventual success or failure of an asynchronous operation. `Promise.all` runs tasks in parallel; `Promise.allSettled` handles mixed outcomes.
- **Async/Await** — syntactic sugar over Promises that makes asynchronous code read like synchronous code.
- **Web Workers / Node.js Worker Threads** — true parallel execution in separate threads, each with its own heap. Workers communicate by message passing rather than shared memory.

The `src/race-condition.ts` example demonstrates a classic race condition using Node.js `worker_threads`. Five simulated cash machines concurrently read and write a shared account balance stored in a file. Because the read-modify-write sequence is not atomic, concurrent interleaving corrupts the balance — illustrating why shared mutable state requires explicit synchronization even in a high-level runtime.

For IoT edge applications (Node.js on Raspberry Pi, Johnny-Five, MQTT clients), the event loop model is well suited to I/O-heavy workloads but inadequate for CPU-bound sensor processing, which requires Worker Threads or native addons.

---

### Python

> See [Python/README.md](Python/README.md) for the full reference.

The Python folder covers three concurrency models and their IoT applications:

| Model | Module | Best For |
|---|---|---|
| **Threading** | `threading` | I/O-bound tasks (network requests, file operations). The CPython GIL limits true parallelism — only one thread executes Python bytecode at a time — but threads yield the GIL during I/O, enabling concurrent I/O. |
| **Multiprocessing** | `multiprocessing` | CPU-bound tasks (signal processing, image analysis). Each process has its own memory space and interpreter, bypassing the GIL for true multi-core parallelism. |
| **Async I/O** | `asyncio` | High-concurrency I/O workloads (web servers, MQTT clients, database connections). Uses an event loop and coroutines (`async`/`await`) for cooperative multitasking in a single thread. |

Three production-grade sub-projects are provided:

- **`asyncio/`** — A FastAPI web application demonstrating async request handling. FastAPI uses Uvicorn (an ASGI server) to manage an `asyncio` event loop. Async route handlers yield control during I/O (e.g., database queries), allowing other requests to proceed without blocking.
- **`Celery/`** — A distributed task queue using Celery with a Python API and a LangChain Node.js service. Celery workers process background tasks asynchronously, enabling IoT ingestion pipelines to offload heavy processing away from the request path.
- **`Redis Queue/`** — A Redis-backed worker queue for task dispatch and result retrieval. Includes an OpenAI-compatible API, prompt templates, and integration tests demonstrating concurrent task submission and consumption patterns.

---

## References

- [C++ Thread support library — cppreference.com](https://en.cppreference.com/w/cpp/thread)
- [Go Concurrency Patterns — The Go Blog](https://go.dev/blog/pipelines)
- [Lesson: Concurrency — Oracle Java Tutorials](https://docs.oracle.com/javase/tutorial/essential/concurrency/index.html)
- [JavaScript Execution Model — MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Execution_model)
- [Concurrent Execution — Python 3 Documentation](https://docs.python.org/3/library/concurrency.html)
- [Node.js Worker Threads](https://nodejs.org/api/worker_threads.html)


# Concurrency in C++ for IoT on Linux / Raspberry Pi

## Table of Contents

1. [Overview](#overview)
2. [Why C++ for IoT](#why-c-for-iot)
3. [Core Concurrency Primitives](#core-concurrency-primitives)
   - [std::thread — Native Threading](#stdthread--native-threading)
   - [std::mutex and std::lock_guard — Synchronization](#stdmutex-and-stdlock_guard--synchronization)
   - [std::atomic — Lock-Free Operations](#stdatomic--lock-free-operations)
   - [std::async and std::future — Asynchronous Programming](#stdasync-and-stdfuture--asynchronous-programming)
   - [std::condition_variable — Event-Driven Synchronization](#stdcondition_variable--event-driven-synchronization)
4. [Concurrency on Raspberry Pi — POSIX Threads](#concurrency-on-raspberry-pi--posix-threads)
5. [Concurrent State Machine (FSM) for IoT](#concurrent-state-machine-fsm-for-iot)
6. [AI Agents for C++ Concurrency Development](#ai-agents-for-c-concurrency-development)
7. [Development Environment Setup on Linux with VS Code](#development-environment-setup-on-linux-with-vs-code)
   - [Step 1 — Install GCC/G++ with C++17 Support](#step-1--install-gccg-with-c17-support)
   - [Step 2 — Install CMake](#step-2--install-cmake)
   - [Step 3 — Install Git](#step-3--install-git)
   - [Step 4 — Install VS Code](#step-4--install-vs-code)
   - [Step 5 — Install VS Code Extensions](#step-5--install-vs-code-extensions)
   - [Step 6 — Configure IntelliSense (c_cpp_properties.json)](#step-6--configure-intellisense-c_cpp_propertiesjson)
   - [Step 7 — Configure Build Tasks (tasks.json)](#step-7--configure-build-tasks-tasksjson)
   - [Step 8 — Configure Launch/Debug (launch.json)](#step-8--configure-launchdebug-launchjson)
   - [Step 9 — (Optional) Install MQTT Library — Eclipse Paho](#step-9--optional-install-mqtt-library--eclipse-paho)
8. [Building the Examples](#building-the-examples)
9. [Running on Raspberry Pi — Step-by-Step](#running-on-raspberry-pi--step-by-step)
   - [Step 1 — Prepare the Raspberry Pi](#step-1--prepare-the-raspberry-pi)
   - [Step 2 — Install Build Tools on the Pi](#step-2--install-build-tools-on-the-pi)
   - [Step 3 — Transfer and Build on the Pi](#step-3--transfer-and-build-on-the-pi)
   - [Step 4 — Run the Program](#step-4--run-the-program)
   - [Step 5 — (Optional) Remote Development via VS Code SSH](#step-5--optional-remote-development-via-vs-code-ssh)
10. [Examples Overview](#examples-overview)
11. [Key Takeaways](#key-takeaways)

---

## Overview

Concurrency in C++ for IoT is the ability to manage multiple tasks simultaneously — reading sensors, processing data, and communicating over network protocols — on a single device. On Linux-based IoT hardware such as the Raspberry Pi, C++11/14/17/20 standard library threading primitives (`std::thread`, `std::mutex`, `std::atomic`, `std::async`, `std::future`, `std::condition_variable`) map directly to POSIX threads, providing low-latency, low-overhead execution suited to the resource constraints of edge devices.

IoT devices must handle multiple inputs (GPS, temperature sensors, I2C/SPI peripherals) and outputs (actuators, cloud connectivity, MQTT brokers) at the same time. C++ concurrency primitives make this tractable without requiring an RTOS — the Linux scheduler provides preemptive multitasking, and the C++ standard library provides the portable abstractions.

---

## Why C++ for IoT

C++ is the language of choice for embedded and IoT development for several reasons:

- **Low-level memory access** — direct pointer manipulation, stack allocation, and placement new allow fine-grained memory control.
- **Predictable performance** — compiled, statically typed code with no garbage collector pauses and minimal runtime overhead.
- **Zero-cost abstractions** — standard library containers and algorithms produce the same machine code as hand-written C equivalents when optimized.
- **Portable hardware abstraction** — `std::thread` compiles to `pthreads` on Linux, to Win32 threads on Windows, and to FreeRTOS tasks on microcontrollers with the appropriate port.
- **Mature ecosystem** — HAL drivers, MQTT clients (Eclipse Paho), protocol buffers, and sensor libraries all expose C or C++ APIs.
- **C++17/20 features** — structured bindings, `std::optional`, `std::variant`, parallel algorithms, and coroutines reduce boilerplate in data-pipeline code.

---

## Core Concurrency Primitives

### std::thread — Native Threading

`std::thread` spawns an OS-level thread. On Linux/Raspberry Pi this compiles to a `pthread_create` call. Threads run a callable (function, lambda, or functor) concurrently with the spawning thread.

```cpp
#include <iostream>
#include <thread>

void sensor_read(int sensor_id) {
    std::cout << "Reading sensor " << sensor_id << " on thread\n";
}

int main() {
    std::thread t(sensor_read, 1);   // spawn thread
    t.join();                         // wait for completion
    std::cout << "Main thread continues\n";
    return 0;
}
```

Compile with:

```bash
g++ -std=c++17 main.cpp -pthread -o sensor_read
```

The `-pthread` flag links `libpthread` and enables thread-safe errno on glibc. On modern GCC the flag also implies `-lpthread`.

Key rules:
- Every `std::thread` object must be either `join()`ed or `detach()`ed before it is destroyed, or `std::terminate` is called.
- Prefer `join()` over `detach()` — detached threads make lifetime management harder on resource-constrained devices.
- Use RAII wrappers (C++20 `std::jthread`) when available — they join automatically on destruction.

---

### std::mutex and std::lock_guard — Synchronization

A mutex (mutual exclusion) ensures only one thread at a time executes a protected code block. On Raspberry Pi this maps to a `pthread_mutex_t`. `std::lock_guard` acquires the mutex on construction and releases it on destruction (RAII), preventing deadlocks caused by forgotten `unlock()` calls.

```cpp
#include <mutex>

int sensor_accumulator = 0;
std::mutex accumulator_mutex;

void record_reading(int value) {
    std::lock_guard<std::mutex> lock(accumulator_mutex);  // acquired
    sensor_accumulator += value;
    // lock released automatically when lock goes out of scope
}
```

Use `std::unique_lock` instead of `std::lock_guard` when you need to:
- Transfer lock ownership.
- Pair with a `std::condition_variable` (required).
- Unlock and re-lock mid-scope.

Locking guidelines for IoT:
- Keep critical sections as short as possible — do not call I/O or sleep inside a lock.
- Never acquire two mutexes in different orders across threads (deadlock prevention).
- Prefer `std::scoped_lock` (C++17) to lock multiple mutexes simultaneously.

---

### std::atomic — Lock-Free Operations

`std::atomic<T>` provides thread-safe read-modify-write operations without a mutex, using hardware-level atomic CPU instructions (e.g., `LDREX`/`STREX` on ARM Cortex-A). This is faster than mutex locking for simple counters, flags, and state indicators.

```cpp
#include <atomic>

std::atomic<bool>     g_running{true};         // stop flag
std::atomic<uint64_t> g_readings_count{0};     // lock-free counter
std::atomic<int>      g_error_code{0};         // last error flag

void sensor_thread() {
    while (g_running.load()) {
        // ... read sensor ...
        ++g_readings_count;    // atomic increment, no mutex needed
    }
}

// From another thread or signal handler:
// g_running.store(false);
```

Use `std::atomic` for:
- Global stop/run flags.
- Simple counters and statistics.
- Single-value status indicators.

Do not use `std::atomic` as a replacement for a mutex when protecting a multi-field data structure — the fields are not updated atomically relative to each other.

---

### std::async and std::future — Asynchronous Programming

`std::async` launches a callable asynchronously and returns a `std::future<T>` that holds the result. The calling thread can continue doing other work and retrieve the result with `future.get()` when needed. This prevents the main loop from blocking on slow I/O operations such as cloud uploads or MQTT publishes.

```cpp
#include <future>
#include <string>
#include <chrono>
using namespace std::chrono_literals;

std::string upload_to_cloud(const std::string& payload) {
    std::this_thread::sleep_for(300ms);   // simulate network latency
    return "ACK: " + payload;
}

int main() {
    // Launch asynchronously — does not block
    std::future<std::string> fut = std::async(
        std::launch::async,
        upload_to_cloud,
        "temperature=24.5"
    );

    // Main thread continues reading sensors here...

    // Retrieve result when needed (blocks until upload_to_cloud returns)
    std::string response = fut.get();
    std::cout << response << "\n";
    return 0;
}
```

`std::launch::async` forces a new thread. Without it the implementation may defer execution (`std::launch::deferred`).

---

### std::condition_variable — Event-Driven Synchronization

`std::condition_variable` allows threads to sleep efficiently until a specific condition becomes true. This avoids busy-waiting (spinning in a loop consuming CPU cycles) and is the correct mechanism for producer-consumer pipelines — for example, waking a network thread only when new sensor data is available in a shared queue.

```cpp
#include <mutex>
#include <condition_variable>
#include <queue>

std::queue<int>            data_queue;
std::mutex                 queue_mutex;
std::condition_variable    data_ready_cv;

// Producer (sensor thread)
void sensor_thread() {
    while (true) {
        int reading = read_sensor();
        {
            std::lock_guard<std::mutex> lock(queue_mutex);
            data_queue.push(reading);
        }
        data_ready_cv.notify_one();   // wake one waiting consumer
    }
}

// Consumer (processing thread)
void processing_thread() {
    while (true) {
        std::unique_lock<std::mutex> lock(queue_mutex);
        data_ready_cv.wait(lock, [] { return !data_queue.empty(); });
        int value = data_queue.front();
        data_queue.pop();
        lock.unlock();
        process(value);
    }
}
```

The lambda predicate passed to `wait()` guards against spurious wakeups — the thread re-checks the condition before proceeding.

---

## Concurrency on Raspberry Pi — POSIX Threads

The Raspberry Pi runs a full Linux kernel. C++ threading primitives compile to POSIX thread (pthread) calls:

| C++ Primitive              | POSIX Equivalent             | Kernel Mechanism         |
|----------------------------|------------------------------|--------------------------|
| `std::thread`              | `pthread_create`             | `clone()` syscall        |
| `std::mutex`               | `pthread_mutex_t`            | futex                    |
| `std::condition_variable`  | `pthread_cond_t`             | futex                    |
| `std::atomic`              | GCC built-in atomics         | ARM `LDREX`/`STREX`      |
| `std::async`               | `pthread_create` + result    | Thread pool / new thread |

The Raspberry Pi 4 has a quad-core ARM Cortex-A72 running at 1.8 GHz. `std::thread::hardware_concurrency()` returns `4`, meaning four threads can execute in true parallel. Earlier models:

| Model         | Cores | Max true parallelism |
|---------------|-------|----------------------|
| Pi Zero (W)   | 1     | 1 (concurrency only) |
| Pi 2B         | 4     | 4                    |
| Pi 3B/3B+     | 4     | 4                    |
| Pi 4B         | 4     | 4                    |
| Pi 5          | 4     | 4                    |

On single-core devices (Pi Zero), threads still provide concurrency through time-slicing, which is useful for decoupling I/O-bound tasks even without parallelism.

Real-time considerations: For hard real-time requirements, use `SCHED_FIFO` or `SCHED_RR` scheduling policies via `pthread_setschedparam()`. The standard `std::thread` API does not expose scheduling parameters directly; use native handles:

```cpp
std::thread t(my_critical_task);
sched_param sch{};
sch.sched_priority = 80;
pthread_setschedparam(t.native_handle(), SCHED_FIFO, &sch);
```

---

## Concurrent State Machine (FSM) for IoT

A Finite State Machine models a device that exists in one of several defined states and transitions between them based on events. IoT devices naturally follow state transitions: INIT -> READING -> PROCESSING -> TRANSMITTING -> READING (loop), with an ERROR state reachable from any state.

In a concurrent C++ program, a thread-safe FSM protects the current state variable with a mutex, allowing multiple threads to query or trigger transitions safely.

```
 +-------+     startup      +---------+     data ready     +------------+
 | INIT  | --------------> | READING | -----------------> | PROCESSING |
 +-------+                  +---------+                    +------------+
                                 ^                               |
                                 |         batch ready           v
                                 +------------------------  +---------------+
                                                           | TRANSMITTING  |
                                                           +---------------+
                                    ERROR
      Any state  -----------------------------------------> +-------+
                                                            | ERROR |
                                                            +-------+
```

A thread-safe FSM implementation:

```cpp
class DeviceStateMachine {
public:
    DeviceState get() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return state_;
    }

    bool transition(DeviceState expected, DeviceState next) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (state_ == expected) {
            state_ = next;
            return true;
        }
        return false;   // transition rejected — already in different state
    }

private:
    mutable std::mutex mutex_;
    DeviceState state_ = DeviceState::INIT;
};
```

Each thread calls `transition()` with the state it expects to be in and the state it wants to move to. Rejected transitions are handled gracefully, preventing inconsistent state changes from racing threads.

---

## AI Agents for C++ Concurrency Development

AI coding agents can generate, refactor, and debug concurrent C++ code for IoT by interpreting structured natural language prompts. Effective prompts include explicit constraints relevant to the target hardware.

Example prompt structure:

```
Role:    Act as an embedded systems expert targeting C++17 for Linux/ARM (Raspberry Pi).
Context: IoT sensor hub with temperature, humidity, and GPS sensors. Data is published
         to an MQTT broker every 2 seconds. Constraints: minimal memory footprint,
         thread-safe queue for sensor data, non-blocking network IO, no exceptions.
Task:    Generate a multithreaded C++ program using std::thread, std::mutex,
         std::atomic, std::condition_variable, and std::async. Include a thread-safe
         queue, a lock-free stop flag, and a simple FSM for device state.
```

Recommended AI coding agents for C++ concurrency work:

**GitHub Copilot** — integrated into VS Code, generates inline suggestions for `std::thread` boilerplate, mutex guards, and async patterns. Understands IoT context when the project contains relevant header includes and comments.

**Cursor** — agentic IDE built on VS Code. Uses multi-step planning to navigate large codebases and refactor concurrent code across multiple files. Recommended for complex multi-threaded projects.

**Claude Code** — terminal-based agent from Anthropic that can analyze entire repositories, trace data races, and refactor synchronization patterns. High performance on large projects using Claude 3.5 Sonnet / Claude 4 Sonnet.

**Windsurf Editor** — AI-powered IDE featuring "Flow" agentic behavior. Understands and anticipates coding needs for C++ concurrency, generates multiline suggestions for complex synchronized data structures.

Key points when using AI agents for C++ concurrency:
- Always specify the C++ standard (`-std=c++17` or `-std=c++20`).
- State the target hardware and OS (Linux ARM, Raspberry Pi, single-core vs. multi-core).
- Ask the agent to reason about thread lifetimes and whether every thread is joined.
- Request explicit handling of data races and spurious wakeups.
- AI agents produce functional starting code but C++ concurrency bugs (race conditions, deadlocks, use-after-free from detached threads) require human review and testing tools like ThreadSanitizer (`-fsanitize=thread`).

---

## Development Environment Setup on Linux with VS Code

### Step 1 — Install GCC/G++ with C++17 Support

Ubuntu/Debian (and Raspberry Pi OS):

```bash
sudo apt update
sudo apt install -y build-essential gcc g++ gdb
```

Verify the compiler version (GCC 7+ supports C++17; GCC 9+ has full C++17 library support):

```bash
g++ --version
# g++ (Ubuntu 11.4.0) 11.4.0
```

To install a specific version alongside the system default:

```bash
sudo apt install -y gcc-12 g++-12
sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-12 12
```

### Step 2 — Install CMake

CMake is the recommended build system for cross-platform C++ projects:

```bash
sudo apt install -y cmake
cmake --version
# cmake version 3.22.1
```

For a newer CMake on older Debian/Ubuntu systems:

```bash
# Install via pip (requires Python 3)
pip3 install --upgrade cmake
cmake --version
```

Or download the official installer from `cmake.org/download`.

### Step 3 — Install Git

```bash
sudo apt install -y git
git --version
```

### Step 4 — Install VS Code

On Ubuntu/Debian (x86_64):

```bash
# Add Microsoft signing key and repository
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | \
    gpg --dearmor | sudo tee /usr/share/keyrings/packages.microsoft.gpg > /dev/null

echo "deb [arch=amd64 signed-by=/usr/share/keyrings/packages.microsoft.gpg] \
    https://packages.microsoft.com/repos/code stable main" | \
    sudo tee /etc/apt/sources.list.d/vscode.list

sudo apt update
sudo apt install -y code
```

On Raspberry Pi OS (ARM64):

```bash
# VS Code is available in the official Raspberry Pi OS repository since Bullseye
sudo apt update
sudo apt install -y code
```

Alternatively, download the `.deb` package directly from `code.visualstudio.com/download` and install with:

```bash
sudo dpkg -i code_*.deb
sudo apt install -f   # resolve any missing dependencies
```

### Step 5 — Install VS Code Extensions

Open VS Code and install the following extensions from the Extensions view (`Ctrl+Shift+X`) or via the command line:

```bash
# C/C++ language support (IntelliSense, debugging, code navigation)
code --install-extension ms-vscode.cpptools

# CMake language support and syntax highlighting
code --install-extension twxs.cmake

# CMake Tools — configure, build, and debug CMake projects from within VS Code
code --install-extension ms-vscode.cmake-tools

# GitHub Copilot (AI code completion — requires GitHub account)
code --install-extension github.copilot

# Remote — SSH (connect to and develop on Raspberry Pi from your desktop)
code --install-extension ms-vscode-remote.remote-ssh
```

### Step 6 — Configure IntelliSense (c_cpp_properties.json)

Create `.vscode/c_cpp_properties.json` in your project root:

```json
{
    "configurations": [
        {
            "name": "Linux",
            "includePath": [
                "${workspaceFolder}/**"
            ],
            "defines": [],
            "compilerPath": "/usr/bin/g++",
            "cStandard": "c17",
            "cppStandard": "c++17",
            "intelliSenseMode": "linux-gcc-x64"
        }
    ],
    "version": 4
}
```

For Raspberry Pi (ARM64), change `intelliSenseMode` to `"linux-gcc-arm64"` and `compilerPath` to `/usr/bin/aarch64-linux-gnu-g++` if cross-compiling.

### Step 7 — Configure Build Tasks (tasks.json)

Create `.vscode/tasks.json` to build directly from VS Code with `Ctrl+Shift+B`:

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "CMake Configure",
            "type": "shell",
            "command": "cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug -DCMAKE_CXX_STANDARD=17",
            "group": "build",
            "problemMatcher": []
        },
        {
            "label": "CMake Build",
            "type": "shell",
            "command": "cmake --build build --parallel",
            "group": {
                "kind": "build",
                "isDefault": true
            },
            "problemMatcher": "$gcc",
            "dependsOn": "CMake Configure"
        }
    ]
}
```

### Step 8 — Configure Launch/Debug (launch.json)

Create `.vscode/launch.json` to enable the VS Code debugger (`F5`):

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug IoT Sensor Hub",
            "type": "cppdbg",
            "request": "launch",
            "program": "${workspaceFolder}/build/examples/06_iot_sensor_hub/iot_sensor_hub",
            "args": [],
            "stopAtEntry": false,
            "cwd": "${workspaceFolder}",
            "environment": [],
            "externalConsole": false,
            "MIMode": "gdb",
            "setupCommands": [
                {
                    "description": "Enable pretty-printing for gdb",
                    "text": "-enable-pretty-printing",
                    "ignoreFailures": true
                }
            ],
            "preLaunchTask": "CMake Build"
        }
    ]
}
```

### Step 9 — (Optional) Install MQTT Library — Eclipse Paho

For real IoT deployments the Paho MQTT C++ library is the standard choice:

```bash
# Install the C library first
sudo apt install -y libssl-dev

git clone https://github.com/eclipse/paho.mqtt.c.git
cd paho.mqtt.c
cmake -S . -B build -DPAHO_WITH_SSL=ON -DPAHO_BUILD_STATIC=ON
cmake --build build --parallel
sudo cmake --install build

# Now install the C++ wrapper
cd ..
git clone https://github.com/eclipse/paho.mqtt.cpp.git
cd paho.mqtt.cpp
cmake -S . -B build -DPAHO_BUILD_STATIC=ON
cmake --build build --parallel
sudo cmake --install build
```

To detect and link Paho in CMakeLists.txt add:

```cmake
find_package(PahoMqttCpp REQUIRED)
target_link_libraries(my_target PRIVATE PahoMqttCpp::paho-mqttpp3)
```

---

## Building the Examples

Clone or navigate to this directory, then build all examples with CMake:

```bash
cd C++

# Configure (Debug build, C++17)
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug

# Build all targets in parallel
cmake --build build --parallel

# Binaries are placed under build/examples/
ls build/examples/
```

To build a single example:

```bash
cmake --build build --target iot_sensor_hub --parallel
```

To enable ThreadSanitizer (detects data races at runtime):

```bash
cmake -S . -B build_tsan \
    -DCMAKE_BUILD_TYPE=Debug \
    -DCMAKE_CXX_FLAGS="-fsanitize=thread -g"
cmake --build build_tsan --parallel
./build_tsan/examples/06_iot_sensor_hub/iot_sensor_hub
```

---

## Running on Raspberry Pi — Step-by-Step

### Step 1 — Prepare the Raspberry Pi

- Flash **Raspberry Pi OS Lite (64-bit)** (Bookworm or Bullseye) to a microSD card using **Raspberry Pi Imager**.
- Enable SSH in Raspberry Pi Imager advanced options before flashing (or create an empty file named `ssh` in the `/boot` partition).
- Connect the Pi to your network via Ethernet or configure Wi-Fi credentials in Imager.
- Find the Pi's IP address: check your router's DHCP table, or use `ping raspberrypi.local` from your desktop.

### Step 2 — Install Build Tools on the Pi

SSH into the Pi:

```bash
ssh pi@<pi-ip-address>
```

Update the system and install the toolchain:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y build-essential g++ cmake git gdb htop
g++ --version   # should show GCC 12+ on Bookworm
```

### Step 3 — Transfer and Build on the Pi

Option A — Clone directly on the Pi (if the project is in a Git repository):

```bash
git clone <your-repo-url> IoT_Concurrency
cd IoT_Concurrency/C++
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel 4
```

Option B — Copy files from your desktop using `scp`:

```bash
# Run on your desktop
scp -r C++ pi@<pi-ip-address>:~/IoT_Concurrency/
ssh pi@<pi-ip-address>
cd ~/IoT_Concurrency/C++
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel 4
```

The `-DCMAKE_BUILD_TYPE=Release` flag enables `-O2` optimizations and strips debug symbols, reducing binary size — important on the Pi's limited storage.

### Step 4 — Run the Program

```bash
./build/examples/06_iot_sensor_hub/iot_sensor_hub
```

Expected output:

```
IoT Sensor Hub starting (C++17 Concurrency Demo)
Hardware threads available: 4

[FSM] INIT -> READING
[Processor] Processed 8 readings, 0 errors
[FSM] PROCESSING -> TRANSMITTING
[Publisher] Sending 8 readings...
[Publisher] Response: Published 8 readings to cloud (total publishes: 1)
[FSM] TRANSMITTING -> READING
[Monitor] State: READING | Total readings: 12 | Publishes: 1 | Queue depth: 0
...
[Main] Initiating shutdown...
[Main] All threads joined. Final stats:
  Total readings collected: 48
  Total publishes completed: 9
[Main] Shutdown complete.
```

Monitor CPU usage while running:

```bash
# In a separate SSH session
htop
# or
top -d 1
```

Monitor thread count:

```bash
ps -T -p $(pgrep iot_sensor_hub)
```

### Step 5 — (Optional) Remote Development via VS Code SSH

Install the **Remote - SSH** extension in VS Code on your desktop. Then:

1. Open the Command Palette (`Ctrl+Shift+P`) and select **Remote-SSH: Connect to Host**.
2. Enter `pi@<pi-ip-address>`.
3. VS Code opens a new window connected to the Pi — file browsing, IntelliSense, terminal, and the debugger all run on the Pi's filesystem.
4. Install the C/C++ extension on the remote host when prompted.
5. Open the `C++` folder and use the CMake Tools extension to configure and build as normal.

This approach gives you full IDE support while the code compiles and runs natively on the ARM hardware, eliminating cross-compilation complexity.

---

## Examples Overview

| Directory                  | Concept                             | Key Primitives                                    |
|----------------------------|-------------------------------------|---------------------------------------------------|
| `examples/01_threads/`     | Basic thread creation and joining   | `std::thread`, `join()`                           |
| `examples/02_mutex/`       | Shared resource protection          | `std::mutex`, `std::lock_guard`                   |
| `examples/03_atomic/`      | Lock-free counter and stop flag     | `std::atomic<T>`                                  |
| `examples/04_async_future/`| Non-blocking async task             | `std::async`, `std::future`                       |
| `examples/05_condition_variable/` | Producer-consumer pipeline   | `std::condition_variable`, `std::unique_lock`     |
| `examples/06_iot_sensor_hub/`| Full IoT simulation (sensors + FSM) | All primitives combined, FSM, thread-safe queue  |

---

## Key Takeaways

- Use `std::thread` to parallelize independent I/O-bound tasks (sensor reads, network sends) and keep the main loop responsive.
- Use `std::mutex` with `std::lock_guard` to protect any shared data structure (GPIO state, sensor buffers, I2C bus) accessed from more than one thread. Keep critical sections short.
- Use `std::atomic` for simple flags and counters where a mutex would be excessive overhead. It is lock-free on ARM hardware and faster than a mutex for single-variable updates.
- Use `std::async` + `std::future` to offload slow operations (cloud publish, DNS lookup) without blocking the sensor read loop.
- Use `std::condition_variable` with a predicate to implement efficient producer-consumer queues; avoid busy-waiting.
- Model device behavior as a concurrent FSM — each state transition is protected by a mutex, preventing inconsistent state from racing threads.
- On the Raspberry Pi, `std::thread::hardware_concurrency()` returns the number of physical cores. On a Pi Zero (single core), concurrency is achieved through time-slicing rather than true parallelism, which is still valuable for decoupling I/O-bound tasks.
- Compile with `-fsanitize=thread` during development to detect data races early. Remove the sanitizer for production builds.
- When using AI agents to generate concurrent C++ code, always specify the C++ standard, target hardware, and memory constraints in the prompt. Review generated code for thread lifetime issues and missing join calls.


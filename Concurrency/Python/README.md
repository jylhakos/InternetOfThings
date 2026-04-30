# Concurrency in Python

In Python, concurrency refers to the ability to handle multiple tasks seemingly at the same time, even if they are not actually executed in parallel on separate CPU cores because of the Global Interpreter Lock (GIL).

Python provides libraries for writing programs that make use of different forms of concurrency. The asyncio is a library for dealing with asynchronous tasks and coroutines. threading provides access to operating system threads and multiprocessing to operating system processes. Multi-core processors can execute threads and processes on different CPU cores at the same time

Python is maintained and officially released by the Python Software Foundation (PSF). The latest stable release is Python 3.14.4. Refer to the official downloads page for all active and historical releases: https://www.python.org/downloads/

---

## Table of Contents

1. [Folder Structure](#folder-structure)
2. [Concepts](#concepts)
   - [Threading](#threading)
   - [Multiprocessing](#multiprocessing)
   - [The asyncio library (overview)](#the-asyncio-library-overview)
3. [The Global Interpreter Lock (GIL)](#the-global-interpreter-lock-gil)
   - [Why the GIL Restricts Parallelism](#why-the-gil-restricts-parallelism)
   - [Thread States and the GIL](#thread-states-and-the-gil)
   - [Overcoming the GIL Limitations](#overcoming-the-gil-limitations)
4. [How Operating Systems Interpret Python Scripts](#how-operating-systems-interpret-python-scripts)
5. [Setting Up a Virtual Environment](#setting-up-a-virtual-environment)
   - [Why Python Uses a Virtual Environment](#why-python-uses-a-virtual-environment)
   - [Virtual Environments and Performance](#virtual-environments-and-performance)
   - [Creating a Virtual Environment](#creating-a-virtual-environment)
   - [Ubuntu/Linux Step-by-Step Setup](#ubuntulinux-step-by-step-setup)
   - [Using Virtual Environments in VS Code](#using-virtual-environments-in-vs-code)
6. [Threads and Multithreading](#threads-and-multithreading)
   - [Python Threads](#python-threads)
   - [Java Threads](#java-threads)
   - [JavaScript Threads](#javascript-threads)
   - [C Threads](#c-threads)
   - [C++ Threads](#c-threads-1)
   - [Go Goroutines](#go-goroutines)
   - [Threading Model Comparison by Language](#threading-model-comparison-by-language)
7. [The asyncio library](#the-asyncio-library)
   - [Coroutines and Tasks](#coroutines-and-tasks)
   - [Event Loop](#event-loop)
   - [Tasks](#tasks)
   - [async/await](#asyncawait)
8. [Example: A web application with FastAPI](#example-a-web-application-with-fastapi)
9. [Conclusion: asyncio, Celery, and Redis Queue](#conclusion-asyncio-celery-and-redis-queue)
10. [References](#references)

---

## Folder Structure

```
▸ Python/
  ◈ README.md
  ▸ asyncio/
    ◈ docker-compose.yml
    ◈ example_fastapi_app.py
    ◈ gunicorn_config.py
    ◈ lifespan_demo.py
    ◈ project_structure.txt
    ◈ README.md
    ◈ requirements.txt
    ▸ app/
      ◈ crud.py
      ◈ database.py
      ◈ main.py
      ◈ models.py
      ◈ schemas.py
      ▸ routers/
        ◈ users.py
  ▸ Celery/
    ◈ API.md
    ◈ DEPLOYMENT.md
    ◈ docker-compose.yml
    ◈ README.md
    ◈ requirements.txt
    ◈ SETUP.md
    ◈ setup.sh
    ◈ start_dev.sh
    ◈ test_system.py
    ▸ langchain-service/
      ◈ Dockerfile
      ◈ llm_service.js
      ◈ package.json
      ◈ prompt_templates.js
      ◈ server.js
    ▸ python-app/
      ◈ celery_app.py
      ◈ config.py
      ◈ Dockerfile
      ◈ main.py
      ◈ tasks.py
  ▸ Redis Queue/
    ◈ API.md
    ◈ docker-compose.yml
    ◈ Dockerfile.langchain
    ◈ Dockerfile.python
    ◈ langchain_script.js
    ◈ langchain_service.js
    ◈ main.py
    ◈ open_webui_tests.py
    ◈ OPEN_WEBUI.md
    ◈ open_webui.sh
    ◈ openai_api.py
    ◈ package.json
    ◈ prompt_templates_example.py
    ◈ prompt_templates_library.py
    ◈ README.md
    ◈ requirements.txt
    ◈ SETUP.md
    ◈ start.sh
    ◈ test_api_curl.sh
    ◈ test_client.py
    ◈ test_curl_api.py
    ◈ test_new_api.py
    ◈ test_openwebui_integration.py
    ◈ validate_api.py
    ◈ worker.py
```

---

## Concepts

### Threading

The `threading` module allows you to create and manage threads within a single process.

Threads share the same memory space, making communication between them relatively easy.

However, the GIL in CPython limits true parallelism, meaning only one thread can execute Python bytecode at a time, even on multi-core processors.

Threading is well-suited for I/O-bound tasks (e.g., network requests, file operations) where the program spends a lot of time waiting for external resources.

### Multiprocessing

The `multiprocessing` module allows you to create and manage separate processes.

Each process has its own independent memory space, bypassing the GIL and enabling true parallelism across multiple CPU cores.

This makes multiprocessing ideal for CPU-bound tasks (e.g., heavy computations) that can benefit from distributed processing.

### The asyncio library (overview)

Introduced in Python 3.4, `asyncio` is a library for writing concurrent code using the `async`/`await` syntax.

It facilitates cooperative multitasking within a single thread using an event loop.

Coroutines defined with `async def` can `await` other operations, yielding control back to the event loop and allowing other tasks to run.

The asyncio library is primarily designed for I/O-bound tasks and is highly efficient for managing a large number of concurrent connections or operations.

---

## The Global Interpreter Lock (GIL)

### Why the GIL Restricts Parallelism

The Global Interpreter Lock (GIL) restricts Python parallelism by ensuring only one thread executes Python bytecode at a time within a single process, even on multi-core processors.

The GIL, used in the standard CPython interpreter, is a mutex (mutual exclusion lock) that protects internal CPython data structures — particularly reference counts used for memory management — from unsafe simultaneous access by multiple threads.

Without the GIL, concurrent threads could corrupt internal data structures. For example, if two threads simultaneously increment the reference count of the same object, the count could end up being incremented only once instead of twice, leading to premature object deallocation and memory corruption.

While the GIL allows for easy concurrency for I/O-bound tasks (where threads frequently release the lock while waiting for external resources), it is a major bottleneck for computational tasks.

**CPU-Bound Limitations**

The GIL significantly degrades performance for CPU-bound tasks (e.g., numerical calculations, data processing) because threads spend time waiting for the lock rather than working in parallel. Even on a machine with 8 CPU cores, a multithreaded Python program performing heavy calculations will not utilise more than one core effectively at any given instant.

**Reference Counting Safety**

CPython's memory management uses reference counting. Each Python object maintains a counter tracking how many references point to it. This mechanism is not thread-safe. Without the GIL, concurrent threads could produce race conditions that corrupt these counts, causing memory leaks or crashes.

### Thread States and the GIL

According to the CPython C API, the Python interpreter is generally not thread-safe (unless using a free-threaded build). The GIL must be held by a thread before it can access Python objects or invoke Python's C API.

Each thread maintains a `PyThreadState` data structure holding thread-local information. A thread state referenced by a thread's local pointer is considered "attached", which is analogous to holding the GIL on standard builds.

The interpreter regularly switches threads between bytecode instructions (governed by `sys.setswitchinterval()`), providing an approximation of concurrency for I/O-bound tasks.

The GIL is released around blocking I/O operations. From the C extension API, this is done by calling `PyEval_SaveThread()` (via the `Py_BEGIN_ALLOW_THREADS` macro) before the blocking operation, and `PyEval_RestoreThread()` (via `Py_END_ALLOW_THREADS`) afterwards. This allows other threads to run while the current thread waits for I/O completion.

### Overcoming the GIL Limitations

**Use multiprocessing**

The most effective workaround is the `multiprocessing` module, which creates separate processes — each with its own Python interpreter and GIL — allowing full CPU core utilisation. Inter-process communication is achieved through shared memory, pipes, or queues.

**Use C-Extensions**

Libraries such as NumPy and SciPy frequently release the GIL during heavy numerical computation. When a C extension calls `Py_BEGIN_ALLOW_THREADS`, other Python threads can run concurrently for the duration of that native code block.

**Free-Threaded CPython (Experimental)**

Python 3.13 introduced an experimental free-threaded build (disabled by default) that removes the GIL, enabling true multi-core parallelism for threads. This is an active area of CPython development.

---

## How Operating Systems Interpret Python Scripts

When an operating system (OS) runs a Python script, it goes through a structured pipeline from source code to execution. The following flow diagram illustrates this process in an academic context.

```
  PYTHON SCRIPT EXECUTION PIPELINE ON LINUX/UNIX
  ================================================

  +-----------------------+
  |  Python Source File   |   (e.g., script.py)
  |  script.py            |   Plain text UTF-8 source code
  +-----------+-----------+
              |
              |  Step 1: OS locates interpreter
              |  Shell reads shebang line: #!/usr/bin/env python3
              |  Or explicit invocation:   $ python3 script.py
              v
  +-----------------------+
  |  OS Kernel / Shell    |   fork() + exec() system calls
  |  Process Loader       |   Loads CPython binary into memory
  +-----------+-----------+
              |
              |  Step 2: CPython process initialised
              |  Interpreter state and GIL initialised
              v
  +-----------------------+
  |  Lexer (Tokeniser)    |   Converts source characters into tokens
  |                       |   Identifies keywords, operators, literals
  +-----------+-----------+
              |
              |  Step 3: Tokenised stream passed to parser
              v
  +-----------------------+
  |  Parser               |   Constructs Abstract Syntax Tree (AST)
  |  (AST Generation)     |   Validates syntactic structure
  +-----------+-----------+
              |
              |  Step 4: AST passed to compiler
              v
  +-----------------------+
  |  Bytecode Compiler    |   Transforms AST into CPython bytecode
  |                       |   Cached in .pyc files (pycache/)
  +-----------+-----------+
              |
              |  Step 5: Bytecode loaded into the PVM
              v
  +-----------------------+
  |  Python Virtual       |   Bytecode evaluation loop (ceval.c)
  |  Machine (PVM)        |   Interprets opcodes sequentially
  |                       |   Manages stack frames, GIL scheduling
  +-----------+-----------+
              |
              |  Step 6: Runtime interactions
              v
  +-----------------------+
  |  OS System Calls      |   File I/O, network sockets, memory
  |  (Kernel Space)       |   allocation via OS interfaces
  +-----------+-----------+
              |
              |  Step 7: Results returned to user space
              v
  +-----------------------+
  |  Program Output /     |   stdout, stderr, return codes
  |  Side Effects         |   Files written, network packets sent
  +-----------------------+
```

**Key stages explained:**

▪ **Shebang and invocation** — The OS shell (e.g., Bash) or a parent process invokes the CPython executable. On Unix-like systems, a shebang line (`#!/usr/bin/env python3`) at the top of the script instructs the OS kernel to use that interpreter.

▪ **Lexical analysis** — The CPython lexer scans the source text character by character, producing a stream of tokens (identifiers, keywords, literals, operators, delimiters).

▪ **Parsing and AST construction** — The parser processes the token stream and builds an Abstract Syntax Tree (AST), a hierarchical representation of the program's grammatical structure.

▪ **Bytecode compilation** — The AST is compiled into platform-independent CPython bytecode (`.pyc` files). Bytecode is a lower-level, compact representation executed by the Python Virtual Machine.

▪ **Python Virtual Machine (PVM)** — The PVM iterates over bytecode instructions in an evaluation loop (`ceval.c`). It manages call stacks, local and global namespaces, and the GIL scheduler.

▪ **OS system calls** — Any I/O operations, memory allocations, or network communications invoke OS system calls, crossing from user space into kernel space and back.

---

## Setting Up a Virtual Environment

A virtual environment is an isolated Python environment that allows project-specific packages to be installed without affecting the system-wide Python installation. This is essential for reproducible, conflict-free development.

Using a virtual environment is a standard best practice that creates an isolated workspace for each project. This prevents projects from interfering with one another or with the system's global Python installation. Virtual environments come in several forms — the built-in `venv` module, the third-party `virtualenv` package, and `conda` (from the Anaconda/Miniconda distributions) — but all share the same fundamental purpose: dependency isolation.

References: [Python Tutorial — Virtual Environments and Packages](https://docs.python.org/3/tutorial/venv.html) | [venv — Creation of virtual environments](https://docs.python.org/3/library/venv.html)

### Why Python Uses a Virtual Environment

Python uses virtual environments to create isolated directory trees that each contain their own Python interpreter, libraries, and scripts. This prevents version conflicts between different projects and avoids cluttering the global system installation.

**Dependency isolation**

Different projects often require different — and sometimes incompatible — versions of the same library. For example, if application A requires `requests==2.6.0` and application B requires `requests==2.7.0`, installing either version globally will break the other application. A virtual environment gives each project its own `site-packages` directory, fully resolving this conflict.

**Privilege-free local installation**

On many systems (such as Linux), users cannot install packages into the global Python installation without administrative (`sudo`) privileges. Virtual environments allow packages to be installed in user-owned folders without requiring elevated permissions.

**Interpreter selection**

The environment contains a symlink or copy of the Python binary. When activated, the shell's `PATH` is updated to prioritise this local interpreter. When a Python interpreter is running from within a virtual environment, `sys.prefix` and `sys.exec_prefix` point to the virtual environment's directories, while `sys.base_prefix` and `sys.base_exec_prefix` point to the base Python installation used to create the environment. This distinction allows tools to detect whether they are running inside a virtual environment.

**Reproducibility**

Virtual environments encourage capturing exact dependency versions in a `requirements.txt` file. This allows any developer (or a CI/CD pipeline) to recreate an identical environment from scratch using `pip install -r requirements.txt`.

**Project boundaries**

A virtual environment is considered disposable — it should be simple to delete and recreate from scratch. Project code is never placed inside the environment directory itself. The environment is not checked into version control (it should be listed in `.gitignore`).

### Virtual Environments and Performance

Virtual environments (`venv`, `virtualenv`, `conda`) do not significantly affect the execution performance of Python scripts or threads.

Unlike a Virtual Machine (VM), which emulates hardware or an operating system and adds a full virtualisation layer between code and hardware, a virtual environment is simply an isolation tool for managing dependencies. It does not add any virtualisation layer between Python code and the underlying hardware or OS kernel.

**Runtime speed**

There is no runtime performance cost for Python code executing inside a virtual environment. A virtual environment simply tells the Python interpreter where to look for installed libraries by adjusting `sys.path` and `sys.prefix`. Once the libraries are located and loaded, the script runs at exactly the same speed it would when run against a global Python installation.

**Thread performance**

The performance of threads remains managed by Python's Global Interpreter Lock (GIL) and the system's hardware — not the environment setup. The GIL scheduling, I/O release behaviour, and OS thread management operate identically whether the interpreter was launched from inside a virtual environment or from a system-wide installation.

**Comparison: Virtual Environment vs Virtual Machine**

| Aspect | Virtual Environment | Virtual Machine (VM) |
|---|---|---|
| Isolation scope | Python packages and interpreter path | Entire OS and hardware resources |
| Performance overhead | Negligible — no additional execution layer | Significant — hardware emulation or hypervisor overhead |
| Purpose | Dependency and project isolation | Full OS isolation, sandboxing, infrastructure |
| Examples | `venv`, `virtualenv`, `conda` env | VirtualBox, VMware, QEMU, Docker (for containers) |
| Affects GIL? | No | N/A (separate OS instance) |

### Creating a Virtual Environment

The built-in `venv` module (available since Python 3.3, recommended since Python 3.5) is the standard tool for creating virtual environments. Reference: [venv — Creation of virtual environments](https://docs.python.org/3/library/venv.html)

**Creation**

Use the `venv` module to create a new environment folder. The conventional name for the environment directory is `.venv` (hidden by default in most shells) or `venv`:

```bash
python -m venv .venv
```

This creates the `.venv/` directory containing:

▪ A copy or symlink of the Python binary (`bin/python`)  
▪ A `lib/pythonX.Y/site-packages/` directory for installed packages  
▪ A `pyvenv.cfg` configuration file with a `home` key pointing to the base Python installation  
▪ Activation scripts (`bin/activate` for POSIX shells)  

**Activation**

Activating the environment updates the shell's `PATH` to prioritise the local interpreter and `pip`:

| Platform | Shell | Command |
|---|---|---|
| macOS / Linux | bash / zsh | `source .venv/bin/activate` |
| macOS / Linux | fish | `source .venv/bin/activate.fish` |
| macOS / Linux | csh / tcsh | `source .venv/bin/activate.csh` |
| Windows | cmd.exe | `.venv\Scripts\activate.bat` |
| Windows | PowerShell | `.venv\Scripts\Activate.ps1` |

While the environment is active, `pip install` commands place packages only within that specific environment's `site-packages` directory, leaving all other environments and the global installation untouched.

**Deactivation**

```bash
deactivate
```

**Verification**

To confirm the active interpreter is from the virtual environment:

```python
import sys
print(sys.prefix)           # path to the virtual environment
print(sys.base_prefix)      # path to the base Python installation
print(sys.prefix != sys.base_prefix)  # True when inside a venv
```

### Ubuntu/Linux Step-by-Step Setup

**Step 1: Verify Python installation**

```bash
python3 --version
```

If Python 3 is not installed:

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv -y
```

**Step 2: Navigate to your project directory**

```bash
cd /path/to/your/project
```

**Step 3: Create a virtual environment**

```bash
python3 -m venv venv
```

This creates a `venv/` directory containing an isolated Python interpreter and pip.

**Step 4: Activate the virtual environment**

```bash
source venv/bin/activate
```

The shell prompt will change to show the active environment name, for example:

```
(venv) user@machine:~/project$
```

**Step 5: Install project dependencies**

```bash
pip install -r requirements.txt
```

Or install packages individually:

```bash
pip install fastapi uvicorn celery redis
```

**Step 6: Verify installed packages**

```bash
pip list
```

**Step 7: Deactivate the virtual environment when done**

```bash
deactivate
```

**Step 8: (Optional) Freeze dependencies to a requirements file**

```bash
pip freeze > requirements.txt
```

### Using Virtual Environments in VS Code

VS Code integrates directly with Python virtual environments, enabling automatic activation and IntelliSense support.

**Selecting the Python interpreter:**

1. Open the Command Palette: `Ctrl+Shift+P`
2. Type and select: `Python: Select Interpreter`
3. Choose the interpreter inside your `venv/` directory, for example:
   `./venv/bin/python`

VS Code will store this selection in `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python"
}
```

**Terminal auto-activation:**

VS Code's integrated terminal automatically activates the selected virtual environment when a new terminal session is opened. This can be verified by checking the `(venv)` prefix in the terminal prompt.

**Using the Python Extension:**

Install the official Python extension (`ms-python.python`) from the Extensions panel. This extension provides:

▪ Interpreter selection and switching  
▪ Linting (Pylint, Flake8, Ruff)  
▪ IntelliSense and code completion scoped to the virtual environment  
▪ Integrated test discovery and debugging  

**Workspace settings example:**

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
    "python.terminal.activateEnvironment": true
}
```

---

## Threads and Multithreading

A thread is the smallest unit of execution within a process. Multithreading is the ability of a CPU (or a single core within it) to execute multiple threads concurrently. The behaviour and capabilities of threads differ significantly depending on the programming language and its runtime environment.

The primary difference between Python, JavaScript, and Java lies in how their runtimes manage CPU cores and memory sharing.

### Python Threads

Python uses OS-level threads via the `threading` module, but the CPython GIL prevents truly parallel bytecode execution within a single process. Python threads are cooperative for CPU-bound tasks — only one thread runs at a time — but preemptive for I/O-bound tasks, since the GIL is released during blocking I/O.

```python
import threading

def worker(name):
    print(f"Thread {name} is running")

threads = [threading.Thread(target=worker, args=(i,)) for i in range(4)]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

▪ Threads share the same memory space within a process.  
▪ The GIL allows only one thread to execute Python bytecode at any given time.  
▪ For CPU-bound parallelism, use `multiprocessing` instead.  

### Java Threads

Java is a multi-threaded language where the Java Virtual Machine (JVM) allows multiple threads to run simultaneously on different CPU cores. It is designed for high-performance enterprise systems that require true parallel execution and shared memory across threads.

```java
public class Worker extends Thread {
    public void run() {
        System.out.println("Thread " + getName() + " is running");
    }
    public static void main(String[] args) throws InterruptedException {
        Worker[] workers = new Worker[4];
        for (int i = 0; i < 4; i++) {
            workers[i] = new Worker();
            workers[i].start();
        }
        for (Worker w : workers) w.join();
    }
}
```

▪ Java threads are truly parallel on multi-core systems without any GIL equivalent.  
▪ Shared memory requires synchronisation primitives (`synchronized`, `ReentrantLock`).  
▪ The `java.util.concurrent` package provides high-level abstractions (thread pools, futures).  

### JavaScript Threads

JavaScript is fundamentally single-threaded, using an Event Loop to handle asynchronous operations without blocking the main execution thread. While it does not use traditional threads like Java, it can achieve parallelism through Web Workers in browsers or `worker_threads` in Node.js.

```javascript
// Node.js Worker Threads example
const { Worker, isMainThread, parentPort } = require('worker_threads');

if (isMainThread) {
    const worker = new Worker(__filename);
    worker.on('message', (msg) => console.log('Received:', msg));
} else {
    parentPort.postMessage('Hello from worker thread');
}
```

▪ The main thread uses a non-blocking event loop for all async I/O.  
▪ Workers run in separate V8 isolates with no shared memory by default.  
▪ Communication between workers uses message passing (`postMessage`).  

### C Threads

C uses POSIX threads (`pthreads`) on Unix/Linux systems for native OS-level threading. There is no runtime GIL; threads can execute fully in parallel on multiple cores, but the programmer is entirely responsible for synchronisation.

```c
#include <pthread.h>
#include <stdio.h>

void *worker(void *arg) {
    printf("Thread %ld running\n", (long)arg);
    return NULL;
}

int main() {
    pthread_t threads[4];
    for (long i = 0; i < 4; i++)
        pthread_create(&threads[i], NULL, worker, (void *)i);
    for (int i = 0; i < 4; i++)
        pthread_join(threads[i], NULL);
    return 0;
}
```

▪ Full hardware parallelism — no interpreter lock.  
▪ Manual synchronisation required: mutexes, semaphores, condition variables.  
▪ Memory safety is the programmer's responsibility; race conditions can cause undefined behaviour.  

### C++ Threads

C++ provides a portable thread API via `<thread>` (C++11 and later), built upon OS threads. Like C, there is no GIL; threads run fully in parallel and memory is shared between all threads in a process.

```cpp
#include <iostream>
#include <thread>
#include <vector>

void worker(int id) {
    std::cout << "Thread " << id << " running\n";
}

int main() {
    std::vector<std::thread> threads;
    for (int i = 0; i < 4; i++)
        threads.emplace_back(worker, i);
    for (auto &t : threads)
        t.join();
    return 0;
}
```

▪ `std::thread`, `std::mutex`, `std::atomic`, and `std::future` provide concurrency primitives.
▪ High-performance computing, game engines, and system software favour C++ for its true parallelism and low overhead.

### Go Goroutines

Go uses lightweight concurrency units called goroutines, multiplexed onto OS threads by the Go runtime scheduler (M:N threading model). Go is designed for highly concurrent network services.

```go
package main

import (
    "fmt"
    "sync"
)

func worker(id int, wg *sync.WaitGroup) {
    defer wg.Done()
    fmt.Printf("Goroutine %d running\n", id)
}

func main() {
    var wg sync.WaitGroup
    for i := 0; i < 4; i++ {
        wg.Add(1)
        go worker(i, &wg)
    }
    wg.Wait()
}
```

▪ Goroutines are extremely lightweight (initial stack ~2KB vs. ~1MB for OS threads).  
▪ The Go runtime scheduler maps goroutines onto available OS threads using the GOMAXPROCS setting.  
▪ Communication between goroutines uses channels (`chan`), following the CSP (Communicating Sequential Processes) model.  

### Threading Model Comparison by Language

| Feature | Python | Java | JavaScript | C | C++ | Go |
|---|---|---|---|---|---|---|
| Thread Model | OS threads + GIL | OS threads (JVM) | Single-threaded (Event Loop) | POSIX threads | `std::thread` (OS) | Goroutines (M:N) |
| True CPU Parallelism | Via Multiprocessing | Yes | Via Workers / Child Processes | Yes | Yes | Yes |
| Memory Sharing | Shared (threads) / Isolated (processes) | Shared among threads | Isolated (workers) | Shared | Shared | Shared + Channels |
| Synchronisation | `threading.Lock`, `Queue` | `synchronized`, `java.util.concurrent` | Promises, async/await | `pthread_mutex` | `std::mutex`, `std::atomic` | Channels, `sync.Mutex` |
| GIL Equivalent | Yes (CPython GIL) | None | None | None | None | None |
| Best Use Case | I/O-bound tasks, scripting, data science | CPU-heavy enterprise apps | Real-time web, high I/O | System programming, embedded | High-performance systems | Network services, microservices |
| Concurrency Abstraction | `threading`, `asyncio`, `multiprocessing` | `ExecutorService`, `CompletableFuture` | Promises, `async/await`, Workers | Manual `pthreads` | `std::async`, `std::future` | Goroutines, Channels |

---

## The asyncio library

The `asyncio` library is a Python library used for writing concurrent code using the `async`/`await` syntax, primarily designed for I/O-bound and high-level structured network code.

The asyncio library enables cooperative multitasking within a single thread, meaning tasks yield control to the event loop during I/O operations, allowing other tasks to run.

The concurrency using the asyncio library is not the same as multithreading, where thread switching is managed by the operating system.

Instead of relying on multiple threads, the asyncio library uses a single-threaded event loop.

When a coroutine encounters an `await` statement (e.g., waiting for a network request or file I/O), it yields control back to the event loop.

The event loop then switches to another ready task, effectively performing cooperative multitasking.

**When to use the asyncio library?**

The appropriate choice of the asyncio library will depend on the task to be executed (CPU-bound vs I/O-bound).

Applications that need concurrent input/output processes, such as web servers and clients, database connection libraries, distributed task queues, and real-time streaming systems, are ideally suited for the asyncio library.

The asyncio library is less suitable for CPU-bound tasks, as these would block the single event loop, negating the benefits of concurrency.

For CPU-bound tasks, multiprocessing is generally a more appropriate choice.

### Coroutines and Tasks

Coroutines declared with the `async`/`await` syntax is the preferred way of writing asyncio applications (see: https://docs.python.org/3/library/asyncio-task.html).

To actually run a coroutine, asyncio provides the following mechanisms:

**1. `asyncio.run()`**

The `asyncio.run()` function runs the top-level entry point `main()` function:

```python
import asyncio
import time

async def say_after(delay, what):
    await asyncio.sleep(delay)
    print(what)

async def main():
    print(f"started at {time.strftime('%X')}")

    await say_after(1, 'hello')
    await say_after(2, 'world')

    print(f"finished at {time.strftime('%X')}")

asyncio.run(main())
```

Expected output:

```
started at 17:13:52
hello
world
finished at 17:13:55
```

**2. `asyncio.create_task()`**

The `asyncio.create_task()` function runs coroutines concurrently as asyncio Tasks. The following example runs two `say_after` coroutines concurrently, completing in approximately 2 seconds rather than 3:

```python
async def main():
    task1 = asyncio.create_task(say_after(1, 'hello'))
    task2 = asyncio.create_task(say_after(2, 'world'))

    print(f"started at {time.strftime('%X')}")
    await task1
    await task2
    print(f"finished at {time.strftime('%X')}")
```

**3. `asyncio.TaskGroup` (Python 3.11+)**

`asyncio.TaskGroup` provides a modern alternative to `create_task()` with stronger safety guarantees. If any task raises an exception, remaining tasks in the group are cancelled:

```python
async def main():
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(say_after(1, 'hello'))
        task2 = tg.create_task(say_after(2, 'world'))
    print(f"finished at {time.strftime('%X')}")
```

**Awaitables**

There are three main types of awaitable objects in asyncio:

▪ **Coroutines** — Functions defined with `async def`. A coroutine object is created by calling a coroutine function; it must be awaited to run.  
▪ **Tasks** — Wrap coroutines and schedule them to run on the event loop. Created with `asyncio.create_task()`.  
▪ **Futures** — Low-level objects representing an eventual result of an asynchronous operation. Rarely created directly in application-level code.  

**Running tasks concurrently with `asyncio.gather()`**

`asyncio.gather()` runs multiple awaitables concurrently and returns their results as a list:

```python
import asyncio

async def factorial(name, number):
    f = 1
    for i in range(2, number + 1):
        print(f"Task {name}: Compute factorial({number}), currently i={i}...")
        await asyncio.sleep(1)
        f *= i
    print(f"Task {name}: factorial({number}) = {f}")
    return f

async def main():
    results = await asyncio.gather(
        factorial("A", 2),
        factorial("B", 3),
        factorial("C", 4),
    )
    print(results)  # [2, 6, 24]

asyncio.run(main())
```

**Task cancellation**

Tasks can be cancelled using the `cancel()` method. When cancelled, `asyncio.CancelledError` is raised inside the coroutine at the next `await` point:

```python
async def main():
    task = asyncio.create_task(asyncio.sleep(3600))
    await asyncio.sleep(1)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("Task was cancelled")
```

### Event Loop

The central component of asyncio that manages and schedules coroutines, handling I/O events and switching between tasks.

The event loop uses cooperative scheduling: it runs one Task at a time. While a Task awaits a Future or I/O operation, the event loop runs other Tasks, callbacks, or performs I/O operations.

### Tasks

Objects that wrap coroutines and are scheduled to run on the event loop. They are created using `asyncio.create_task()` or `asyncio.TaskGroup`. Save a reference to created tasks to prevent garbage collection before completion.

### async/await

Keywords used to define and manage coroutines, enabling explicit control over concurrency.

The `async` keyword defines a coroutine function. The `await` keyword pauses execution until an awaitable (like another coroutine, a Task, or an I/O operation) completes.

`await` can only be used inside functions created with the `async` keyword.

---

## Example: A web application with FastAPI

FastAPI handles concurrent web application requests using Python's asyncio library and ASGI (Asynchronous Server Gateway Interface) servers.

This allows FastAPI to process multiple requests seemingly simultaneously, especially beneficial for I/O-bound operations like database queries or API calls.

FastAPI achieves concurrency by leveraging an event loop within the ASGI server (e.g., Uvicorn) to manage asynchronous tasks, enabling it to switch between requests while waiting for I/O operations to complete.

FastAPI utilises `async` and `await` keywords in Python, allowing functions to be non-blocking.

This means that when a request is being processed and encounters an I/O operation (like a database query), the event loop can switch to handling another request instead of waiting for the first one to finish.

Once the I/O operation is complete, the first request resumes its execution.

FastAPI is built on Starlette, which uses ASGI as its interface.

ASGI servers like Uvicorn manage the event loop, which is the core of how concurrency is handled.

The event loop schedules and manages asynchronous tasks, allowing for concurrent request processing.

When a request arrives, the ASGI server (e.g., Uvicorn) puts it on the event loop as a task.

If the request involves an I/O operation, the event loop can switch to another task, allowing other requests to be processed.

```python
from fastapi import FastAPI
import asyncio

app = FastAPI()

@app.get("/data")
async def read_data():
    # Simulate a time-consuming operation (e.g., database query)
    await asyncio.sleep(1)
    return {"data": "your data"}
```

In this example, the `read_data` endpoint uses `await asyncio.sleep(1)`, which simulates an I/O operation.

---

## Conclusion: asyncio, Celery, and Redis Queue

Python provides multiple concurrency and distributed task execution strategies. The following table summarises `asyncio`, `Celery`, and `Redis Queue (RQ)` — their architectural model, strengths, and primary use cases:

| Feature | asyncio | Celery | Redis Queue (RQ) |
|---|---|---|---|
| Execution Model | Single-threaded cooperative multitasking (event loop) | Distributed task queue (multi-process/multi-worker) | Distributed task queue (worker processes) |
| Parallelism Type | Concurrent I/O within one process | True parallel execution across workers/machines | True parallel execution across worker processes |
| Transport / Broker | No broker (in-process) | RabbitMQ, Redis, Amazon SQS | Redis (required) |
| Best For | High-concurrency I/O: web servers, API clients, WebSockets, real-time streaming | Long-running background tasks, periodic schedules (Celery Beat), distributed microservices | Simple background job queues, deferred tasks, lightweight worker pools |
| Typical Use Case | FastAPI web handlers, async database queries, HTTP client pools | Email sending, report generation, ML inference pipelines, ETL jobs | Image processing queues, file export tasks, deferred API calls |
| Overhead | Minimal — single process, no broker | Higher — requires broker infrastructure and worker management | Low to moderate — requires Redis, straightforward setup |
| Result Backend | In-process (Futures/Tasks) | Redis, RabbitMQ, database (configurable) | Redis |
| Monitoring | Custom instrumentation | Flower (web dashboard) | RQ Dashboard |
| Language Support | Python only | Python only | Python only |

**asyncio** is best suited for applications that must handle a large number of concurrent I/O operations within a single process, such as high-throughput web APIs and real-time data streaming. It eliminates the overhead of managing multiple processes or external brokers for I/O-dominated workloads.

**Celery** is the preferred choice for enterprise-grade distributed task processing where tasks may be CPU-intensive, long-running, or require scheduling (e.g., periodic jobs with Celery Beat). It integrates with multiple message brokers and provides robust retry, routing, and monitoring capabilities.

**Redis Queue (RQ)** offers a simpler, Redis-native alternative to Celery for teams that need background job processing without the complexity of a full Celery deployment. Its straightforward API and Redis dependency make it well-suited for small to medium-scale workloads.

---

## References

1. Python Software Foundation — Official Python Downloads: https://www.python.org/downloads/
2. Python 3 Official Documentation: https://docs.python.org/3/
3. Concurrent Execution (Python Standard Library): https://docs.python.org/3/library/concurrency.html
4. Coroutines and Tasks (asyncio): https://docs.python.org/3/library/asyncio-task.html
5. Thread States and the Global Interpreter Lock (CPython C API): https://docs.python.org/3/c-api/threads.html#threads
6. MIT 6.102 Software Construction — Reading 14: Concurrency: https://web.mit.edu/6.102/www/sp25/classes/14-concurrency/
7. Python Developer's Guide — Version Status: https://devguide.python.org/versions/

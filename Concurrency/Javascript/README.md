# Concurrency in JavaScript and TypeScript

## Table of Contents

1. [Overview](#1-overview)
2. [JavaScript Execution Model](#2-javascript-execution-model)
   - [The Engine and the Host](#the-engine-and-the-host)
   - [Agent Execution Model](#agent-execution-model)
   - [Stack and Execution Contexts](#stack-and-execution-contexts)
3. [Event Loop and Call Stack](#3-event-loop-and-call-stack)
4. [Promises](#4-promises)
5. [Async/Await](#5-asyncawait)
6. [Web Workers](#6-web-workers)
   - [Dedicated Workers](#dedicated-workers)
   - [Shared Workers](#shared-workers)
   - [Thread Safety](#thread-safety)
7. [Concurrency Models](#7-concurrency-models)
   - [Shared Memory](#shared-memory)
   - [Message Passing](#message-passing)
8. [Processes, Threads, and Time-Slicing](#8-processes-threads-and-time-slicing)
9. [Workers in TypeScript](#9-workers-in-typescript)
10. [Race Conditions and Interleaving](#10-race-conditions-and-interleaving)
    - [Bank Account Example](#bank-account-example)
    - [Interleaving](#interleaving)
    - [Race Condition](#race-condition)
11. [Practical Example: Race Condition in TypeScript](#11-practical-example-race-condition-in-typescript)
    - [Source Code](#source-code)
    - [Setup in VS Code](#setup-in-vs-code)
    - [Install Dependencies](#install-dependencies)
    - [Compile TypeScript](#compile-typescript)
    - [Run the Example](#run-the-example)
12. [Key Tools and APIs](#12-key-tools-and-apis)
13. [Summary](#13-summary)
14. [References](#14-references)

---

## 1. Overview

JavaScript concurrency enables non-blocking, asynchronous tasks using the event loop, Promises, and async/await to speed up applications. Key tools include `Promise.all` for parallel execution and `Promise.allSettled` for handling mixed outcomes. Core topics to study include the event loop, web APIs, worker threads, and avoiding blocking I/O.

JavaScript and TypeScript utilize a concurrency model based on an event loop, which enables them to handle multiple tasks like network requests or user interactions without blocking the main execution thread. While TypeScript adds static typing and enhanced tooling, it relies on the same underlying JavaScript execution mechanisms.

---

## 2. JavaScript Execution Model

The JavaScript engine implements the ECMAScript (JavaScript) language, providing the core functionality. It takes source code, parses it, and executes it. To interact with the outside world — such as to produce meaningful output, interface with external resources, or implement security and performance mechanisms — additional environment-specific mechanisms are provided by the host environment. The HTML DOM is the host environment when JavaScript is executed in a web browser. Node.js is another host environment that allows JavaScript to be run on the server side.

**Reference:** [JavaScript execution model - MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Execution_model)

### The Engine and the Host

The JavaScript engine and the host environment cooperate to run JavaScript programs. The engine implements the ECMAScript language specification; the host provides APIs for I/O, timers, networking, and DOM manipulation.

### Agent Execution Model

Each autonomous executor of JavaScript is called an **agent**, which maintains three facilities for code execution:

- **Heap** — a region of memory where objects are allocated
- **Queue (Job Queue / Event Loop)** — a first-in-first-out queue of tasks to execute
- **Stack (Call Stack)** — a last-in-first-out structure tracking active execution contexts

Each agent is analogous to a thread. In a browser, an agent can be one of:

- A similar-origin window agent (containing `Window` objects)
- A dedicated worker agent (containing a `DedicatedWorkerGlobalScope`)
- A shared worker agent (containing a `SharedWorkerGlobalScope`)
- A service worker agent (containing a `ServiceWorkerGlobalScope`)
- A worklet agent (containing a `WorkletGlobalScope`)

In Node.js, the equivalent concept is called [worker threads](https://nodejs.org/api/worker_threads.html).

### Stack and Execution Contexts

Each function call creates an **execution context** (stack frame) that tracks:

- Code evaluation state
- The function, module, or script being executed
- The current realm
- Variable bindings (via `var`, `let`, `const`, `function`, `class`, etc.)
- The `this` reference

---

## 3. Event Loop and Call Stack

JavaScript uses a single-threaded **"run-to-completion"** model. Each task (job) is processed entirely before the next one starts, ensuring that functions cannot be preempted by other code. This differs from languages like C, where a function running in a thread may be stopped at any point to run other code in another thread.

**Run-to-completion:** Each job in the queue runs entirely before the next job is pulled. Code inside a running function cannot be interrupted by other JavaScript code. This makes reasoning about sequential logic predictable.

**Never blocking:** JavaScript's event loop model ensures execution is never blocking. Handling I/O is performed via events and callbacks. When the application waits for a network request, IndexedDB query, or `fetch()` call, it can still process other things like user input.

The event loop continuously:

1. Pulls a job from the task queue
2. Executes it to completion (stack empties)
3. Drains the microtask queue (higher priority, e.g., Promise callbacks)
4. Pulls the next job from the task queue

---

## 4. Promises

Promises are the standard for managing asynchronous operations in JavaScript. A Promise represents an asynchronous action's eventual success (fulfilled) or failure (rejected), and allows developers to associate handlers with each outcome.

```typescript
const fetchData = (): Promise<string> => {
  return new Promise((resolve, reject) => {
    setTimeout(() => resolve('Data loaded'), 1000);
  });
};

// Parallel execution — all must succeed
Promise.all([fetchData(), fetchData()])
  .then(([result1, result2]) => console.log(result1, result2));

// Handling mixed outcomes — waits for all, regardless of success or failure
Promise.allSettled([fetchData(), Promise.reject('Error')])
  .then(results => results.forEach(r => console.log(r.status)));
```

---

## 5. Async/Await

Async/Await is syntactic sugar for Promises that makes asynchronous code appear and behave more like synchronous code, improving readability and maintainability.

```typescript
async function loadData(): Promise<void> {
  try {
    const result = await fetchData();
    console.log(result);
  } catch (error) {
    console.error('Failed to load:', error);
  }
}

// Running tasks concurrently with async/await
async function loadAll(): Promise<void> {
  const [a, b] = await Promise.all([fetchData(), fetchData()]);
  console.log(a, b);
}
```

---

## 6. Web Workers

For true parallel execution, **Web Workers** allow scripts to run in background threads separate from the main execution thread, preventing UI lag during heavy computations.

**Reference:** [Using Web Workers - MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Using_web_workers)

### Dedicated Workers

A dedicated worker is accessible only by the script that created it. Data is sent between workers and the main thread via `postMessage()` and the `onmessage` event handler. The data is copied, not shared.

```javascript
// main.js — spawning a worker
const myWorker = new Worker('worker.js');

myWorker.postMessage({ value: 42 });

myWorker.onmessage = (event) => {
  console.log('Worker replied:', event.data);
};

myWorker.onerror = (error) => {
  console.error('Worker error:', error.message);
};

// worker.js — inside the worker thread
onmessage = (event) => {
  const result = event.data.value * 2;
  postMessage(result);
};
```

To terminate a worker from the main thread:

```javascript
myWorker.terminate();
```

### Shared Workers

A shared worker can be accessed from multiple scripts — even from different windows, iframes, or workers — as long as they share the same origin. Communication goes through an explicit port object.

```javascript
const myWorker = new SharedWorker('worker.js');

myWorker.port.postMessage('hello');

myWorker.port.onmessage = (event) => {
  console.log('Shared worker responded:', event.data);
};
```

### Thread Safety

Web workers spawn real OS-level threads, but they have carefully controlled communication points. There is no direct access to non-thread-safe components or the DOM. Data is passed as serialized objects via `postMessage()`. This design makes concurrency problems much harder to introduce compared to unrestricted shared memory.

---

## 7. Concurrency Models

There are two common models for concurrent programming: **shared memory** and **message passing**.

### Shared Memory

In the shared memory model, concurrent modules interact by reading and writing shared objects in memory. Both modules have access to the same memory space.

Examples:

- Two processors sharing the same physical memory
- Two programs sharing a common filesystem with files they can read and write
- Two threads in the same program sharing the same objects

### Message Passing

In the message-passing model, concurrent modules interact by sending messages to each other through a communication channel. Incoming messages are queued for handling one at a time.

Examples:

- Two computers in a network communicating via network connections
- A web browser and a web server exchanging HTTP requests and responses
- Two programs whose input and output are connected by a pipe (e.g., `ls | grep`)

---

## 8. Processes, Threads, and Time-Slicing

**Process:** A process is an instance of a running program isolated from other processes on the same machine. It has its own private section of the machine's memory. Processes normally share no memory between them. A process can be thought of as a virtual computer — the program feels like it has the entire machine to itself.

**Thread:** A thread is a locus of control inside a running program. It represents a virtual processor inside the virtual computer. Threads in the same process share all memory. Whenever you run a TypeScript/JavaScript program, the program starts with one thread.

**Time-slicing:** When there are more threads than processors, concurrency is simulated by time-slicing. The processor switches between threads. When threads run at the same time on different processors, they are said to be running **in parallel**. Even without parallelism, concurrency can be tricky — on most systems, time-slicing happens unpredictably and nondeterministically.

**Reference:** [Reading 14: Concurrency - MIT 6.102 Software Construction](https://web.mit.edu/6.102/www/sp23/classes/14-concurrency/)

---

## 9. Workers in TypeScript

TypeScript does not have user-accessible threads, but it has an abstraction called `Worker`. Sometimes called **Web Workers** because the API first appeared in web browsers, it is also supported by Node.js via the [`worker_threads`](https://nodejs.org/api/worker_threads.html) module.

A `Worker` behaves like a **lightweight process**:

- Like threads, workers can access shared memory using `SharedArrayBuffer` to share binary data
- Like processes, each new `Worker` runs its JavaScript file in a fresh global environment — it loads a fresh private copy of imported modules
- Workers generally communicate by message-passing via a built-in bidirectional channel

```typescript
import { Worker, isMainThread } from 'worker_threads';

if (isMainThread) {
  const worker = new Worker('./worker.js');
  worker.on('message', (msg) => console.log('Received:', msg));
  worker.postMessage('start');
} else {
  // Worker code runs here
}
```

Note: `new Worker` expects a JavaScript file (`.js`). TypeScript source must first be compiled before a worker can be started from it.

---

## 10. Race Conditions and Interleaving

### Bank Account Example

The following example uses the filesystem as shared memory. It illustrates how concurrent programs can produce incorrect results when reads and writes are not coordinated.

```typescript
import fs from 'fs';

// Suppose all the cash machines share a single bank account, stored in a file named 'account'
function readBalance(): number {
  return parseFloat(fs.readFileSync('account').toString());
}

function writeBalance(balance: number): void {
  fs.writeFileSync('account', balance.toString());
}

function deposit(): void {
  let balance = readBalance();
  balance = balance + 1;
  writeBalance(balance);
}

function withdraw(): void {
  let balance = readBalance();
  balance = balance - 1;
  writeBalance(balance);
}
```

Customers use the cash machines to do transactions like this:

```typescript
deposit(); // put a dollar in
withdraw(); // take it back out
```

Each transaction is a one-dollar deposit followed by a one-dollar withdrawal, so it should leave the balance unchanged. But when multiple workers run concurrently, the result is unpredictable.

### Interleaving

When two cash machine workers A and B work concurrently, the steps of `deposit()` can be interleaved:

**Safe interleaving — correct result:**

```
A: readBalance() returns 200
A: add 1
A: writeBalance(201)
B: readBalance() returns 201
B: add 1
B: writeBalance(202)
```

**Dangerous interleaving — race condition:**

```
A: readBalance() returns 200
B: readBalance() returns 200    <- B reads before A writes
A: add 1
B: add 1
A: writeBalance(201)
B: writeBalance(201)            <- A's deposit is lost!
```

The balance ends at 201 instead of 202. A's dollar was lost because both workers read the balance before either wrote it back.

### Race Condition

A **race condition** means that the correctness of the program (the satisfaction of its specifications and preservation of its invariants) depends on the relative timing of events in concurrent computations A and B. When this happens, we say "A is in a race with B."

Some interleavings of events may be consistent with what a single, non-concurrent process would produce, but other interleavings produce wrong answers — violating specifications or invariants.

**Concurrency bugs have very poor reproducibility.** Each time you run a program containing a race condition, you may get different behavior. These bugs are called **heisenbugs** — nondeterministic and hard to reproduce. A heisenbug may even disappear when you try to look at it with `console.log` or a debugger, because printing and debugging are often 100–1000x slower than regular operations, dramatically changing the timing and interleaving.

---

## 11. Practical Example: Race Condition in TypeScript

### Source Code

The practical example is located in [`src/race-condition.ts`](src/race-condition.ts).

It demonstrates:

- The filesystem used as shared memory (the `account` file)
- Multiple Node.js `Worker` threads acting as concurrent cash machines
- How interleaved reads and writes produce incorrect final balances

### Setup in VS Code

**Prerequisites:**

- [Node.js](https://nodejs.org/) v18 or later
- [npm](https://www.npmjs.com/) (included with Node.js)
- [VS Code](https://code.visualstudio.com/)

Recommended VS Code extensions (install via the Extensions panel, `Ctrl+Shift+X`):

- `ms-vscode.vscode-typescript-next` — TypeScript language features and IntelliSense
- `dbaeumer.vscode-eslint` — ESLint integration
- `esbenp.prettier-vscode` — Code formatting

### Install Dependencies

Open the integrated terminal in VS Code (`Ctrl+`` ` `` or **View > Terminal**) and run:

```bash
npm install
```

This installs the development dependencies declared in `package.json`:

- `typescript` — the TypeScript compiler (`tsc`)
- `@types/node` — TypeScript type definitions for Node.js built-in modules (`fs`, `path`, `worker_threads`, etc.)

### Compile TypeScript

Compile the TypeScript source to JavaScript using the configuration in `tsconfig.json`:

```bash
npm run build
```

This runs `tsc` and outputs compiled `.js` files to the `dist/` directory.

To watch for changes and recompile automatically during development:

```bash
npx tsc --watch
```

### Run the Example

After compiling, run the example:

```bash
npm start
```

Or directly:

```bash
node dist/race-condition.js
```

**Expected output (race condition present):**

```
Initial balance: $200
Running 5 cash machines, each doing 100 deposit/withdraw cycles...

Final balance:   $194
Result: RACE CONDITION detected - balance changed by $-6
Explanation: Concurrent workers interleaved their read/write operations.
```

The final balance and difference will vary between runs due to the nondeterministic nature of race conditions. On occasion the balance may appear correct, demonstrating the heisenbug nature of these bugs.

---

## 12. Key Tools and APIs

| Tool / API | Description |
|---|---|
| Event Loop | Single-threaded job queue; processes tasks one at a time |
| Call Stack | Tracks active execution contexts (stack frames) |
| Promises | Standard for async operations; `.then()` / `.catch()` / `.finally()` |
| `async` / `await` | Syntactic sugar over Promises for readable async code |
| `Promise.all()` | Runs multiple Promises in parallel; fails fast on first rejection |
| `Promise.allSettled()` | Runs multiple Promises; waits for all to settle regardless of outcome |
| `Promise.race()` | Resolves or rejects as soon as the first Promise settles |
| Web Workers (Browser) | Background threads in browsers; communicate via `postMessage()` |
| `worker_threads` (Node.js) | Background threads in Node.js; lightweight processes |
| `SharedArrayBuffer` | Shared binary memory accessible by multiple agents |
| `Atomics` | Atomic operations for synchronizing access to shared memory |

---

## 13. Summary

- **Concurrency:** multiple computations running simultaneously
- **Shared memory** and **message passing** are the two fundamental concurrency paradigms
- **Processes** are like virtual computers; **threads** are like virtual processors inside them
- A TypeScript `Worker` behaves like a lightweight process
- **Time-slicing** allows a processor to switch between multiple threads
- **Race conditions** occur when program correctness depends on the relative timing of concurrent events
- **Heisenbugs** are nondeterministic race condition bugs that are hard to reproduce and may disappear under observation
- The JavaScript event loop guarantees **run-to-completion** and **never-blocking** execution
- For heavy computation without blocking the main thread, use **Web Workers**
- Avoid **blocking I/O** in the main thread to keep applications responsive

---

## 14. References

- [JavaScript execution model - MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Execution_model)
- [Using Web Workers - MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Using_web_workers)
- [Reading 14: Concurrency - MIT 6.102 Software Construction](https://web.mit.edu/6.102/www/sp23/classes/14-concurrency/)
- [Worker Threads - Node.js Documentation](https://nodejs.org/api/worker_threads.html)
- [SharedArrayBuffer - MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/SharedArrayBuffer)
- [Atomics - MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Atomics)
- [Web Workers API - MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API)

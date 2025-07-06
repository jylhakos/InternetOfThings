# Concurrency in Python

Python concurrency refers to the ability to handle multiple tasks seemingly at the same time, even if they are not truly executing in parallel on separate CPU cores due to the Global Interpreter Lock (GIL).

Threading

The threading module allows you to create and manage threads within a single process.

Threads share the same memory space, making communication between them relatively easy.

However, the GIL in CPython limits true parallelism, meaning only one thread can execute Python bytecode at a time, even on multi-core processors.

Threading is well-suited for I/O-bound tasks (e.g., network requests, file operations) where the program spends a lot of time waiting for external resources.

Multiprocessing

The multiprocessing module allows you to create and manage separate processes.

Each process has its own independent memory space, bypassing the GIL and enabling true parallelism across multiple CPU cores.

This makes multiprocessing ideal for CPU-bound tasks (e.g., heavy computations) that can benefit from distributed processing.

The asyncio library

Introduced in Python 3.4, asyncio is a library for writing concurrent code using the async/await syntax.

It facilitates cooperative multitasking within a single thread using an event loop.

Coroutines defined with async def can await other operations, yielding control back to the event loop and allowing other tasks to run.

The asyncio library is primarily designed for I/O-bound tasks and is highly efficient for managing a large number of concurrent connections or operations.

## The asyncio library

The asyncio library is a Python library used for writing concurrent code using the async/await syntax, primarily designed for I/O-bound and high-level structured network code.

The asyncio library enables cooperative multitasking within a single thread, meaning tasks yield control to the event loop during I/O operations, allowing other tasks to run.

The concurrency using the asyncio library is not the same as multithreading, where thread switching is managed by the operating system.

Instead of relying on multiple threads, the asyncio library uses a single-threaded event loop. 

When a coroutine encounters an await statement (e.g., waiting for a network request or file I/O), it yields control back to the event loop.

The event loop then switches to another ready task, effectively performing cooperative multitasking. 

When to use the asyncio library?

The appropriate choice of the asyncio library will depend on the task to be executed (CPU bound vs IO bound).

Applications that need concurrent input/output processes, such as web servers and clients, database connection libraries, distributed task queues, and real-time streaming systems, are ideally suited for the asyncio library.

The asyncio library is less suitable for CPU bound tasks, as these would block the single event loop, negating the benefits of concurrency. 

For CPU-bound tasks, multiprocessing is generally a more appropriate choice.

### Coroutines

Functions defined with async def that can pause their execution with await and resume later.

### Event Loop

The central component of asyncio that manages and schedules coroutines, handling I/O events and switching between tasks.

### Tasks

Objects that wrap coroutines and are scheduled to run on the event loop. They are created using asyncio.create_task() or asyncio.TaskGroup.

### async/await

Keywords used to define and manage coroutines, enabling explicit control over concurrency. 

The async keyword defines a coroutine, and await pauses execution until an awaitable (like another coroutine or an I/O operation) completes.

You can only use await inside of functions created with async keyword.

## Example: A web application with FastAPI

FastAPI handles concurrent web application requests using Python's asyncio library and ASGI (Asynchronous Server Gateway Interface) servers. 

This allows FastAPI to process multiple requests seemingly simultaneously, especially beneficial for I/O-bound operations like database queries or API calls. 

FastAPI achieves concurrency by leveraging an event loop within the ASGI server (e.g., Uvicorn) to manage asynchronous tasks, enabling it to switch between requests while waiting for I/O operations to complete.

FastAPI utilizes async and await keywords in Python, allowing functions to be non-blocking.

This means that when a request is being processed and encounters an I/O operation (like a database query), the event loop can switch to handling another request instead of waiting for the first one to finish.

Once the I/O operation is complete, the first request resumes its execution. 

FastAPI is built on Starlette, which uses ASGI as its interface.

ASGI servers like Uvicorn manage the event loop, which is the core of how concurrency is handled.

The event loop schedules and manages asynchronous tasks, allowing for concurrent request processing. 

When a request arrives, the ASGI server (e.g., Uvicorn) puts it on the event loop as a task.

If the request involves an I/O operation, the event loop can switch to another task, allowing other requests to be processed.

```

	from fastapi import FastAPI
	import asyncio

	app = FastAPI()

	@app.get("/data")
	async def read_data():
	    # Simulate a time-consuming operation (e.g., database query)
	    await asyncio.sleep(1)
	    return {"data": "your data"}

```

In this example, the read_data endpoint uses await asyncio.sleep(1), which simulates an I/O operation.

References

Concurrent Execution

https://docs.python.org/3/library/concurrency.html

# Concurrency in Java

Java concurrency allows multiple tasks to execute simultaneously within a single program to improve performance and resource utilization.

## Process vs. Thread

A process is an independent program in execution with its own memory space, whereas a thread is a lightweight "sub-process" within a process that shares resources.

## Threads

The fundamental unit of concurrency in Java. Every application starts with a "main" thread, but additional threads can be created to perform background work.

### Thread Lifecycle

Threads move through five distinct states:

- **New** (born)
- **Runnable** (ready to run)
- **Running** (executing)
- **Waiting/Blocked** (inactive)
- **Dead/Terminated** (finished)

### Extending the Thread Class

Create a subclass, override the `run()` method with your task code, and call `.start()` on an instance of that subclass.

```java
class MyThread extends Thread {
    @Override
    public void run() {
        System.out.println("Thread running: " + Thread.currentThread().getName());
    }
}

MyThread t = new MyThread();
t.start();
```

### Implementing the Runnable Interface

Create a class that implements `Runnable`, pass its instance to a `Thread` constructor, and then call `.start()`. This is generally preferred as it allows the class to extend another class.

```java
class MyRunnable implements Runnable {
    @Override
    public void run() {
        System.out.println("Runnable running: " + Thread.currentThread().getName());
    }
}

Thread t = new Thread(new MyRunnable());
t.start();
```

## Multithreading

A specific technique where a single process executes multiple independent threads that share the same resources.

## Thread Safety

The requirement that shared data must be protected so that multiple threads can access it without causing data corruption or inconsistent states.

## Race Conditions

Occur when multiple threads access shared data simultaneously, and the final state depends on the unpredictable timing of their execution.

## Deadlocks

Situations where two or more threads are permanently blocked, each waiting for a resource held by the other.

## Java Library: `java.util.concurrent`

The `java.util.concurrent` package is the foundation of modern Java concurrency. It provides high-level concurrency utilities such as thread pools, locks, concurrent collections, and synchronization primitives.

## External Resources

- [Lesson: Concurrency (Oracle Java Tutorials)](https://docs.oracle.com/javase/tutorial/essential/concurrency/index.html)
- [Defining and Starting a Thread](https://docs.oracle.com/javase/tutorial/essential/concurrency/runthread.html)


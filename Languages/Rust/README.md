# Rust

## Table of Contents

- [Introduction](#introduction)
- [Getting Started](#getting-started)
- [Examples](#examples)
  - [Basic Hello World](#basic-hello-world)
  - [Rocket Framework](#rocket-framework)
  - [Yew Framework](#yew-framework)
  - [Actix Web Framework](#actix-web-framework)
- [References](#references)


![alt text](https://github.com/jylhakos/InternetOfThings/blob/main/Languages/Rust/rust.svgs?raw=true)

## Introduction

Rust is a systems programming language that provides memory safety without using garbage collection. Developed by Mozilla, Rust is designed to prevent common programming errors such as dangling pointers and null pointer dereferences. While initially created for browser development, Rust has become popular for various applications including device drivers, web servers, and system utilities.

### Key Features

- Memory safety without garbage collection
- Zero-cost abstractions
- Concurrency without data races
- Minimal runtime
- Efficient C bindings

## Getting Started

Before running any examples, ensure you have Rust installed on your system. Visit the official Rust website to install Rust and Cargo (Rust's package manager).

```bash
# Install Rust (if not already installed)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

## Examples

### Basic Hello World

The simplest Rust program that prints "Hello, World!" to the console.

**Location:** `sources/hello-world/`

**Build and Run:**

```bash
cd sources/hello-world
cargo build
cargo run
```

**Expected Output:**
```
Hello, World!
```

### Rocket Framework

Rocket is a web framework for Rust that makes it simple to write fast, secure web applications. This example creates a basic web server that responds with "Hello, World!" on the root path.

**Location:** `sources/rocket-example/`

**Features:**
- Type-safe routing
- Easy-to-use API
- Automatic serialization/deserialization

**Build and Run:**

```bash
cd sources/rocket-example
cargo build
cargo run
```

The server will start at `http://localhost:8000`. Open your browser and navigate to this address to see the response.

**Tutorial:** The example demonstrates:
- Using the `#[get("/")]` macro to define routes
- Creating a launch function with `#[launch]`
- Mounting routes to the Rocket application

### Yew Framework

Yew is a modern Rust framework for creating multi-threaded frontend web applications using WebAssembly. It provides a component-based architecture similar to React.

**Location:** `sources/yew-example/`

**Features:**
- WebAssembly-based frontend
- Component-based architecture
- Virtual DOM for efficient rendering

**Build and Run:**

First, install Trunk (Yew's build tool):

```bash
cargo install trunk
```

Then build and serve the application:

```bash
cd sources/yew-example
trunk serve
```

The application will be available at `http://localhost:8080`.

**Tutorial:** The example demonstrates:
- Creating a functional component with `#[function_component]`
- Using the `html!` macro for JSX-like syntax
- Rendering the application with `yew::Renderer`

### Actix Web Framework

Actix is a powerful, actor-based web framework for Rust. It is one of the fastest web frameworks available and is inspired by the actor model in concurrent programming.

**Location:** `sources/actix-example/`

**Features:**
- High performance and low overhead
- Actor-based architecture
- Asynchronous request handling
- WebSocket support

**Build and Run:**

```bash
cd sources/actix-example
cargo build
cargo run
```

The server will start at `http://127.0.0.1:8080`. Access it through your browser or use curl:

```bash
curl http://127.0.0.1:8080
```

**Tutorial:** The example demonstrates:
- Defining async route handlers with `#[get("/")]`
- Creating an HTTP server with `HttpServer::new()`
- Binding to a specific address and port
- Running the server with the Actix runtime

## References

- [The Rust Programming Language](https://doc.rust-lang.org/book/title-page.html) - Official Rust book
- [Rust by Example](https://doc.rust-lang.org/rust-by-example/) - Learn Rust with examples
- [The Rocket Programming Guide](https://rocket.rs/guide/v0.5/) - Complete guide for Rocket framework
- [Rocket Getting Started](https://rocket.rs/guide/v0.5/getting-started/) - Quick start guide
- [Yew Documentation](https://yew.rs/docs/tutorial) - Official Yew tutorial
- [Yew GitHub Repository](https://github.com/yewstack/yew) - Source code and examples
- [Actix Web Documentation](https://actix.rs/) - Official Actix documentation
- [Actix Getting Started](https://actix.rs/docs/getting-started) - Quick start guide

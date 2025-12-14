# Debugging with GDB

## What is GDB?

GDB (GNU Debugger) is a debugging tool for programs written in various languages including C, C++, and Rust. It allows developers to see what's happening inside a program while it executes or what a program was doing at the moment it crashed. With GDB, you can start your program with specific conditions, stop it at designated points, examine program state, and change variables to test different scenarios.

## Setting up Rust with GDB

To debug Rust programs with GDB, you need to compile your code with debug information enabled. Here's how to set it up:

### Prerequisites

1. Install GDB on your system:
   ```bash
   # On Ubuntu/Debian
   sudo apt-get install gdb
   
   # On Fedora
   sudo dnf install gdb
   
   # On macOS
   brew install gdb
   ```

2. Install Rust (if not already installed):
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   ```

### Compiling Rust Programs for Debugging

To compile Rust programs with debug symbols:

```bash
# Debug build (includes debug symbols by default)
cargo build

# The debug binary will be in target/debug/
```

For release builds with debug information:

```bash
cargo build --release
```

Note: Debug builds automatically include debug symbols, while release builds optimize the code and may remove some debugging information.

### Running GDB with Rust

```bash
# Start GDB with your Rust binary
gdb target/debug/your_program_name

# Or run directly
rust-gdb target/debug/your_program_name
```

The `rust-gdb` wrapper provides better pretty-printing for Rust types.

## Debugging Support in the Rust Compiler

The Rust compiler (rustc) includes extensive debugging support to help developers understand and debug their code. This support includes:

- **DWARF Debug Information**: Rust generates DWARF debugging information that GDB and other debuggers can use to map machine code back to source code.

- **Debug Assertions**: The compiler includes runtime checks in debug builds that help catch bugs early.

- **Symbol Mangling**: Rust uses name mangling for functions and types, but debug information includes demangled names for easier debugging.

- **Pretty Printers**: Rust provides GDB pretty-printers that display Rust data structures in a more readable format.

- **Backtrace Support**: The compiler integrates with the backtrace library to provide detailed stack traces when panics occur.

The Rust compiler team continuously improves debugging support to make the development experience better. Debug builds include additional metadata and runtime checks that help identify issues during development.

## Basic GDB Commands

Here are some essential GDB commands for debugging:

- `run` or `r` - Start the program
- `break <location>` or `b <location>` - Set a breakpoint
- `continue` or `c` - Continue execution
- `next` or `n` - Execute next line (step over)
- `step` or `s` - Execute next line (step into)
- `print <variable>` or `p <variable>` - Print variable value
- `backtrace` or `bt` - Show call stack
- `quit` or `q` - Exit GDB

## References

- [GDB Official Documentation](https://www.sourceware.org/gdb/documentation/)
- [Debugging Support in Rust Compiler](https://rustc-dev-guide.rust-lang.org/debugging-support-in-rustc.html)
- [How to Use GDB - Rust Embedded Discovery Book](https://docs.rust-embedded.org/discovery/microbit/appendix/2-how-to-use-gdb/index.html)



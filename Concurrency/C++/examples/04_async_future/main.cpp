// Example 04 — Async and Future (std::async, std::future)
//
// Demonstrates launching tasks asynchronously and retrieving their
// results later without blocking the main sensor-read loop.
//
// IoT use case: the main thread continues reading sensors while a
// slow network publish operation runs in the background.
// When the result is needed, future.get() blocks only for the
// remaining duration of the async task — not its full runtime.
//
// Build:
//   g++ -std=c++17 main.cpp -pthread -o async_demo
// Run:
//   ./async_demo

#include <iostream>
#include <future>
#include <thread>
#include <string>
#include <vector>
#include <chrono>
#include <sstream>
#include <stdexcept>

using namespace std::chrono_literals;

// ------------------------------------------------------------
// Simulated slow network operations
// ------------------------------------------------------------

struct CloudResponse {
    int    status;     // HTTP-like status: 200 = OK, 503 = error
    int    records_written;
    std::string message;
};

CloudResponse upload_batch(int batch_id, int record_count) {
    // Simulate variable network latency (200-400 ms)
    std::this_thread::sleep_for(std::chrono::milliseconds(200 + batch_id * 50));

    if (batch_id == 3) {
        // Simulate a transient server error on batch 3
        return {503, 0, "Service temporarily unavailable"};
    }
    return {200, record_count, "OK"};
}

std::string dns_lookup(const std::string& hostname) {
    std::this_thread::sleep_for(150ms);   // simulate DNS latency
    return "192.168.1." + std::to_string(hostname.size());  // fake IP
}

// ------------------------------------------------------------
// Simulated sensor read (fast, local I/O)
// ------------------------------------------------------------
double read_temperature(int reading_id) {
    std::this_thread::sleep_for(10ms);
    return 20.0 + (reading_id % 10) * 0.5;
}

// ------------------------------------------------------------
// Demonstrate std::async with std::launch::async
// ------------------------------------------------------------
void demo_basic_async() {
    std::cout << "--- Basic async demo ---\n";

    // Launch DNS lookup asynchronously — does NOT block here
    std::future<std::string> dns_fut = std::async(
        std::launch::async,
        dns_lookup,
        "iot.example.com"
    );

    // Main thread continues doing sensor work while DNS resolves
    std::cout << "[Main] DNS resolving in background...\n";
    double temp = read_temperature(1);
    std::cout << "[Main] Temperature reading: " << temp << " C\n";

    // Retrieve DNS result — blocks only if not yet complete
    std::string ip = dns_fut.get();
    std::cout << "[Main] DNS resolved to: " << ip << "\n\n";
}

// ------------------------------------------------------------
// Demonstrate multiple concurrent futures
// ------------------------------------------------------------
void demo_multiple_futures() {
    std::cout << "--- Multiple futures demo ---\n";

    // Launch several upload batches concurrently
    std::vector<std::future<CloudResponse>> futures;
    for (int i = 1; i <= 5; ++i) {
        futures.push_back(
            std::async(std::launch::async, upload_batch, i, i * 10)
        );
    }

    std::cout << "[Main] " << futures.size()
              << " upload batches running concurrently\n";

    // Collect results in order
    for (int i = 0; i < static_cast<int>(futures.size()); ++i) {
        CloudResponse resp = futures[i].get();
        std::cout << "[Batch " << (i + 1) << "] status=" << resp.status
                  << "  records=" << resp.records_written
                  << "  msg=" << resp.message << "\n";
    }
    std::cout << "\n";
}

// ------------------------------------------------------------
// Demonstrate exception propagation through std::future
// ------------------------------------------------------------
std::string risky_operation(bool should_fail) {
    std::this_thread::sleep_for(100ms);
    if (should_fail) {
        throw std::runtime_error("Sensor communication timeout");
    }
    return "Data collected";
}

void demo_future_exception() {
    std::cout << "--- Future exception propagation demo ---\n";

    std::future<std::string> fut = std::async(
        std::launch::async, risky_operation, true
    );

    try {
        std::string result = fut.get();   // exception re-thrown here
        std::cout << "[Main] Result: " << result << "\n";
    } catch (const std::runtime_error& e) {
        std::cout << "[Main] Caught exception from async task: "
                  << e.what() << "\n";
    }
    std::cout << "\n";
}

// ------------------------------------------------------------
// Demonstrate std::packaged_task — decouple task from thread
// ------------------------------------------------------------
void demo_packaged_task() {
    std::cout << "--- packaged_task demo ---\n";

    // Package a callable and obtain its future before scheduling it
    std::packaged_task<CloudResponse(int, int)> task(upload_batch);
    std::future<CloudResponse> fut = task.get_future();

    // Move the task onto a thread (or into a thread pool)
    std::thread worker(std::move(task), 10, 50);
    worker.detach();   // task manages its own lifetime via the future

    // Retrieve result when ready
    CloudResponse resp = fut.get();
    std::cout << "[PackagedTask] status=" << resp.status
              << "  records=" << resp.records_written << "\n\n";
}

int main() {
    std::cout << "std::async / std::future demo\n\n";

    demo_basic_async();
    demo_multiple_futures();
    demo_future_exception();
    demo_packaged_task();

    std::cout << "[Main] All demos complete.\n";
    return 0;
}

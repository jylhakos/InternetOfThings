// Example 03 — Atomic Operations (std::atomic)
//
// Demonstrates lock-free thread-safe operations using std::atomic.
// On ARM (Raspberry Pi), atomic operations compile to LDREX/STREX
// instructions — no OS-level lock is taken. This is faster than
// std::mutex for simple counters, flags, and single-value status.
//
// Comparison:
//   std::atomic  — lock-free for single-variable updates (counter, flag)
//   std::mutex   — required for compound updates across multiple variables
//
// Build:
//   g++ -std=c++17 main.cpp -pthread -o atomic_demo
// Run:
//   ./atomic_demo

#include <iostream>
#include <thread>
#include <atomic>
#include <vector>
#include <chrono>

using namespace std::chrono_literals;

// ------------------------------------------------------------
// Global atomic variables — safe to read/write from any thread
// without a mutex
// ------------------------------------------------------------
std::atomic<bool>     g_running{true};       // stop flag for all threads
std::atomic<uint64_t> g_readings_total{0};   // total sensor readings collected
std::atomic<uint64_t> g_error_count{0};      // total read errors
std::atomic<int>      g_last_temperature{0}; // last temperature value (integer x10)

// ------------------------------------------------------------
// Sensor thread — increments counters atomically
// ------------------------------------------------------------
void sensor_worker(int id, int num_readings) {
    int fake_temp_base = 200 + id * 10;  // e.g., 210, 220, 230 (tenths of Celsius)

    for (int i = 0; i < num_readings && g_running.load(); ++i) {
        // Simulate occasional read error
        if ((i + id) % 7 == 0) {
            ++g_error_count;                // atomic increment
            std::this_thread::sleep_for(30ms);
            continue;
        }

        ++g_readings_total;                 // atomic increment — no mutex needed
        g_last_temperature.store(fake_temp_base + i);  // atomic store

        std::this_thread::sleep_for(50ms);
    }
}

// ------------------------------------------------------------
// Monitor thread — reads atomics without locking
// ------------------------------------------------------------
void monitor_worker(int polls) {
    for (int i = 0; i < polls; ++i) {
        std::this_thread::sleep_for(150ms);

        // All loads are atomic — consistent snapshot of each individual value
        uint64_t readings = g_readings_total.load();
        uint64_t errors   = g_error_count.load();
        int      temp     = g_last_temperature.load();

        std::cout << "[Monitor] readings=" << readings
                  << "  errors=" << errors
                  << "  last_temp=" << (temp / 10.0) << " C\n";
    }
}

// ------------------------------------------------------------
// Demonstrate fetch_add and compare_exchange
// ------------------------------------------------------------
void demonstrate_cas() {
    std::atomic<int> counter{0};

    // fetch_add returns the value BEFORE the add
    int prev = counter.fetch_add(5);
    std::cout << "[CAS demo] fetch_add(5): prev=" << prev
              << "  now=" << counter.load() << "\n";

    // compare_exchange_strong: only stores new_val if current == expected
    int expected = 5;
    int new_val  = 100;
    bool success = counter.compare_exchange_strong(expected, new_val);
    std::cout << "[CAS demo] CAS(expected=5, new=100): success=" << success
              << "  now=" << counter.load() << "\n";

    // Try again with wrong expected value
    expected = 5;   // counter is now 100, so this will fail
    success  = counter.compare_exchange_strong(expected, 200);
    std::cout << "[CAS demo] CAS(expected=5, new=200): success=" << success
              << "  now=" << counter.load()
              << "  (expected was updated to " << expected << ")\n";
}

int main() {
    std::cout << "Atomic demo starting\n";
    std::cout << "std::atomic<bool> is lock-free: "
              << std::atomic<bool>{}.is_lock_free() << "\n";
    std::cout << "std::atomic<uint64_t> is lock-free: "
              << std::atomic<uint64_t>{}.is_lock_free() << "\n\n";

    // Spawn sensor threads
    std::vector<std::thread> sensors;
    for (int i = 1; i <= 4; ++i) {
        sensors.emplace_back(sensor_worker, i, 20);
    }

    // Spawn monitor thread
    std::thread monitor(monitor_worker, 6);

    for (auto& t : sensors) t.join();
    monitor.join();

    std::cout << "\n[Main] Final totals:\n";
    std::cout << "  Readings : " << g_readings_total.load() << "\n";
    std::cout << "  Errors   : " << g_error_count.load()    << "\n\n";

    demonstrate_cas();

    return 0;
}

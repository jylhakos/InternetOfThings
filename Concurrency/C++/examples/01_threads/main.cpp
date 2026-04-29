// Example 01 — Basic Threads (std::thread)
//
// Demonstrates creating, running, and joining threads.
// On Raspberry Pi, each std::thread maps to a POSIX pthread.
//
// Build:
//   g++ -std=c++17 main.cpp -pthread -o threads_demo
// Run:
//   ./threads_demo

#include <iostream>
#include <thread>
#include <chrono>
#include <vector>

using namespace std::chrono_literals;

// ------------------------------------------------------------
// Simulated sensor read function — runs on its own thread
// ------------------------------------------------------------
void read_sensor(int sensor_id, int interval_ms) {
    for (int i = 0; i < 5; ++i) {
        std::cout << "[Sensor " << sensor_id << "] Reading #" << (i + 1)
                  << " on thread " << std::this_thread::get_id() << "\n";
        std::this_thread::sleep_for(std::chrono::milliseconds(interval_ms));
    }
    std::cout << "[Sensor " << sensor_id << "] Done.\n";
}

// ------------------------------------------------------------
// Lambda on a thread — simulated actuator control
// ------------------------------------------------------------
void run_actuator_thread() {
    std::thread t([]() {
        std::cout << "[Actuator] Thread started, id="
                  << std::this_thread::get_id() << "\n";
        std::this_thread::sleep_for(200ms);
        std::cout << "[Actuator] GPIO pin toggled\n";
    });
    t.join();
}

int main() {
    std::cout << "Main thread id: " << std::this_thread::get_id() << "\n";
    std::cout << "Hardware threads available: "
              << std::thread::hardware_concurrency() << "\n\n";

    // Spawn multiple sensor threads — each runs concurrently
    // Sensor 1 reads every 300 ms, Sensor 2 every 500 ms, Sensor 3 every 200 ms
    std::vector<std::thread> threads;
    threads.emplace_back(read_sensor, 1, 300);
    threads.emplace_back(read_sensor, 2, 500);
    threads.emplace_back(read_sensor, 3, 200);

    // Main thread continues while sensors run in the background
    std::cout << "[Main] Sensors are running concurrently...\n";

    // Wait for all sensor threads to finish
    for (auto& t : threads) {
        t.join();
    }

    std::cout << "\n[Main] All sensor threads joined.\n";

    // Demonstrate a lambda thread for actuator control
    run_actuator_thread();

    std::cout << "[Main] Actuator thread joined. Program complete.\n";
    return 0;
}

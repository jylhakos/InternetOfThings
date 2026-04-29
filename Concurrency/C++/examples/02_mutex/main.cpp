// Example 02 — Mutex and lock_guard (std::mutex, std::lock_guard)
//
// Demonstrates protecting shared state accessed from multiple threads.
// Without the mutex, the accumulator and log lines would be corrupted
// by data races. With std::lock_guard, the mutex is released
// automatically even if an exception occurs (RAII).
//
// Build:
//   g++ -std=c++17 main.cpp -pthread -o mutex_demo
// Run:
//   ./mutex_demo
//
// To observe a data race: comment out the lock_guard lines and rebuild
// with ThreadSanitizer:
//   g++ -std=c++17 -fsanitize=thread -g main.cpp -pthread -o mutex_tsan
//   ./mutex_tsan

#include <iostream>
#include <thread>
#include <mutex>
#include <vector>
#include <chrono>
#include <sstream>

using namespace std::chrono_literals;

// ------------------------------------------------------------
// Shared sensor data buffer — accessed from multiple threads
// ------------------------------------------------------------
struct SensorBuffer {
    std::vector<double> readings;
    double              sum   = 0.0;
    int                 count = 0;
    std::mutex          mutex;          // protects all fields above
};

SensorBuffer g_buffer;

// Output mutex — prevents interleaved console output lines
std::mutex g_console_mutex;

void log(const std::string& msg) {
    std::lock_guard<std::mutex> lock(g_console_mutex);
    std::cout << msg << "\n";
}

// ------------------------------------------------------------
// Sensor thread — writes to the shared buffer
// ------------------------------------------------------------
void sensor_thread(int id, double base_value, int num_readings) {
    for (int i = 0; i < num_readings; ++i) {
        double value = base_value + (i * 0.1);

        // Critical section: only one thread at a time can modify g_buffer
        {
            std::lock_guard<std::mutex> lock(g_buffer.mutex);
            g_buffer.readings.push_back(value);
            g_buffer.sum   += value;
            g_buffer.count += 1;
        }
        // lock released here — other threads can now acquire it

        std::ostringstream oss;
        oss << "[Sensor " << id << "] Wrote value=" << value
            << "  buffer_size=" << g_buffer.count;
        log(oss.str());

        std::this_thread::sleep_for(50ms);
    }
}

// ------------------------------------------------------------
// Reader thread — reads summary from shared buffer
// ------------------------------------------------------------
void reader_thread(int read_count) {
    for (int i = 0; i < read_count; ++i) {
        std::this_thread::sleep_for(120ms);

        double avg  = 0.0;
        int    cnt  = 0;
        {
            std::lock_guard<std::mutex> lock(g_buffer.mutex);
            cnt = g_buffer.count;
            if (cnt > 0) {
                avg = g_buffer.sum / cnt;
            }
        }

        std::ostringstream oss;
        oss << "[Reader]   count=" << cnt << "  average=" << avg;
        log(oss.str());
    }
}

int main() {
    log("Mutex demo starting");
    log("Each sensor writes to a shared buffer protected by std::mutex");

    // Three sensor threads write concurrently to the shared buffer
    std::thread t1(sensor_thread, 1, 20.0,  8);
    std::thread t2(sensor_thread, 2, 100.0, 8);
    std::thread t3(sensor_thread, 3, 55.0,  8);

    // One reader thread samples the buffer periodically
    std::thread reader(reader_thread, 5);

    t1.join();
    t2.join();
    t3.join();
    reader.join();

    // Final summary — no thread is running; no lock needed here
    std::cout << "\n[Main] Final buffer state:\n";
    std::cout << "  Readings count : " << g_buffer.count  << "\n";
    std::cout << "  Sum            : " << g_buffer.sum    << "\n";
    std::cout << "  Average        : " << (g_buffer.sum / g_buffer.count) << "\n";

    return 0;
}

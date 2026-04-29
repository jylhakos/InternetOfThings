// Example 05 — Condition Variable (std::condition_variable)
//
// Demonstrates efficient producer-consumer synchronization.
// A condition_variable lets the consumer thread sleep with zero CPU
// usage until the producer signals that new data is available.
// This eliminates busy-waiting (spinning), which wastes CPU cycles
// and drains battery on edge devices.
//
// IoT use case:
//   - Sensor threads (producers) push readings into a shared queue.
//   - A processing thread (consumer) wakes only when data arrives.
//   - A second condition_variable demonstrates a "data processed"
//     notification back to the producer (back-pressure).
//
// Build:
//   g++ -std=c++17 main.cpp -pthread -o cv_demo
// Run:
//   ./cv_demo

#include <iostream>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <queue>
#include <atomic>
#include <chrono>
#include <string>
#include <sstream>

using namespace std::chrono_literals;

// ------------------------------------------------------------
// Thread-safe queue using condition_variable
// ------------------------------------------------------------
template<typename T>
class BlockingQueue {
public:
    explicit BlockingQueue(size_t max_size = 64)
        : max_size_(max_size) {}

    // Push item. Blocks if the queue is full (back-pressure).
    void push(T item) {
        std::unique_lock<std::mutex> lock(mutex_);
        not_full_cv_.wait(lock, [this] {
            return queue_.size() < max_size_ || shutdown_;
        });
        if (shutdown_) return;
        queue_.push(std::move(item));
        lock.unlock();
        not_empty_cv_.notify_one();   // wake one consumer
    }

    // Pop item. Blocks until data is available or queue is shut down.
    // Returns false if the queue is shut down and empty.
    bool pop(T& out) {
        std::unique_lock<std::mutex> lock(mutex_);
        not_empty_cv_.wait(lock, [this] {
            return !queue_.empty() || shutdown_;
        });
        if (queue_.empty()) return false;
        out = std::move(queue_.front());
        queue_.pop();
        lock.unlock();
        not_full_cv_.notify_one();    // wake one blocked producer
        return true;
    }

    // Timed pop — returns false on timeout
    bool pop_for(T& out, std::chrono::milliseconds timeout) {
        std::unique_lock<std::mutex> lock(mutex_);
        bool ready = not_empty_cv_.wait_for(lock, timeout, [this] {
            return !queue_.empty() || shutdown_;
        });
        if (!ready || queue_.empty()) return false;
        out = std::move(queue_.front());
        queue_.pop();
        lock.unlock();
        not_full_cv_.notify_one();
        return true;
    }

    void shutdown() {
        {
            std::lock_guard<std::mutex> lock(mutex_);
            shutdown_ = true;
        }
        not_empty_cv_.notify_all();
        not_full_cv_.notify_all();
    }

    size_t size() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return queue_.size();
    }

private:
    mutable std::mutex      mutex_;
    std::condition_variable not_empty_cv_;
    std::condition_variable not_full_cv_;
    std::queue<T>           queue_;
    size_t                  max_size_;
    bool                    shutdown_ = false;
};

// ------------------------------------------------------------
// Sensor reading structure
// ------------------------------------------------------------
struct Reading {
    int         sensor_id;
    double      value;
    std::string unit;
};

// Shared queue between producers and consumer
BlockingQueue<Reading> g_queue(8);   // max 8 items (back-pressure demo)

std::atomic<bool>     g_running{true};
std::mutex            g_console_mutex;

void log(const std::string& msg) {
    std::lock_guard<std::mutex> lock(g_console_mutex);
    std::cout << msg << "\n";
}

// ------------------------------------------------------------
// Producer — sensor thread
// ------------------------------------------------------------
void sensor_producer(int id, double base, const std::string& unit, int count) {
    for (int i = 0; i < count && g_running.load(); ++i) {
        Reading r{id, base + (i % 20) * 0.5, unit};

        std::ostringstream oss;
        oss << "[Sensor " << id << "] Pushing value=" << r.value
            << " " << r.unit << "  queue_depth=" << g_queue.size();
        log(oss.str());

        g_queue.push(r);   // blocks if queue is full

        std::this_thread::sleep_for(std::chrono::milliseconds(80 + id * 20));
    }
}

// ------------------------------------------------------------
// Consumer — data processing thread
// ------------------------------------------------------------
void data_consumer() {
    int processed = 0;
    Reading r;

    while (true) {
        // Blocks here (zero CPU usage) until a reading is available
        // or the queue is shut down
        if (!g_queue.pop(r)) {
            break;   // queue shut down and empty
        }

        std::ostringstream oss;
        oss << "[Consumer] Processing sensor_id=" << r.sensor_id
            << "  value=" << r.value << " " << r.unit
            << "  (#" << ++processed << ")";
        log(oss.str());

        // Simulate processing time (e.g., FFT, filtering)
        std::this_thread::sleep_for(60ms);
    }

    log("[Consumer] Finished. Total processed: " + std::to_string(processed));
}

// ------------------------------------------------------------
// One-shot condition variable — demonstrates event signaling
// ------------------------------------------------------------
std::mutex              g_event_mutex;
std::condition_variable g_event_cv;
bool                    g_calibration_done = false;

void calibration_task() {
    std::this_thread::sleep_for(400ms);   // simulate calibration time
    {
        std::lock_guard<std::mutex> lock(g_event_mutex);
        g_calibration_done = true;
    }
    g_event_cv.notify_all();
    log("[Calibration] Complete — all waiting threads notified.");
}

void wait_for_calibration(int id) {
    std::unique_lock<std::mutex> lock(g_event_mutex);
    g_event_cv.wait(lock, [] { return g_calibration_done; });
    log("[Worker " + std::to_string(id) + "] Calibration received, starting work.");
}

int main() {
    std::cout << "Condition variable demo\n\n";

    // --- Part 1: Producer-consumer queue ---
    std::cout << "--- Producer-consumer queue ---\n";

    std::thread t_temp(sensor_producer, 1, 20.0, "C",   15);
    std::thread t_hum (sensor_producer, 2, 50.0, "%RH", 15);
    std::thread t_pres(sensor_producer, 3, 1010.0, "hPa", 10);
    std::thread t_cons(data_consumer);

    t_temp.join();
    t_hum.join();
    t_pres.join();

    // Signal consumer to stop after all producers are done
    g_queue.shutdown();
    t_cons.join();

    // --- Part 2: One-shot event notification ---
    std::cout << "\n--- One-shot event (calibration signal) ---\n";

    std::thread calib(calibration_task);
    std::thread w1(wait_for_calibration, 1);
    std::thread w2(wait_for_calibration, 2);
    std::thread w3(wait_for_calibration, 3);

    calib.join();
    w1.join();
    w2.join();
    w3.join();

    std::cout << "\n[Main] All demos complete.\n";
    return 0;
}

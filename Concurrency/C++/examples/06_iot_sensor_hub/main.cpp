// Example 06 — IoT Sensor Hub (Full Concurrency Demo)
//
// A realistic IoT sensor hub simulation for Raspberry Pi.
// Combines all C++17 concurrency primitives into one integrated program.
//
// Architecture:
//
//   [temperature_sensor_thread]  ---|
//   [humidity_sensor_thread]     ---|---> SensorBuffer (mutex) --> [data_processor_thread]
//   [gps_sensor_thread]          ---|                                      |
//                                                                          | (batch)
//                                                          BlockingQueue<batch>
//                                                                          |
//                                                     [network_publisher_thread]
//                                                       (uses std::async internally)
//
//   [stats_monitor_thread] — reads atomics, queries FSM (lock-free stats)
//
//   DeviceStateMachine — FSM protected by mutex
//     INIT -> READING -> PROCESSING -> TRANSMITTING -> READING -> ...
//
// Build:
//   mkdir -p build && cd build
//   cmake .. -DCMAKE_BUILD_TYPE=Release
//   cmake --build . --parallel
//   ./iot_sensor_hub
//
// Or directly:
//   g++ -std=c++17 main.cpp -pthread -O2 -o iot_sensor_hub
//   ./iot_sensor_hub
//
// To detect data races during development:
//   g++ -std=c++17 -fsanitize=thread -g main.cpp -pthread -o iot_sensor_hub_tsan
//   ./iot_sensor_hub_tsan

#include <iostream>
#include <thread>
#include <mutex>
#include <atomic>
#include <future>
#include <condition_variable>
#include <queue>
#include <vector>
#include <chrono>
#include <random>
#include <string>
#include <sstream>
#include <iomanip>
#include <stdexcept>

using namespace std::chrono_literals;

// ============================================================
// Utility — thread-safe console output
// ============================================================

std::mutex g_console_mutex;

void log(const std::string& msg) {
    std::lock_guard<std::mutex> lock(g_console_mutex);
    std::cout << msg << "\n";
}

// ============================================================
// Sensor Reading
// ============================================================

struct SensorReading {
    std::string sensor_id;
    double      value;
    std::string unit;
    bool        valid;
};

// ============================================================
// Thread-Safe Bounded Queue (condition_variable + mutex)
// ============================================================

template<typename T>
class BlockingQueue {
public:
    explicit BlockingQueue(size_t max_size = 32)
        : max_size_(max_size) {}

    void push(T item) {
        std::unique_lock<std::mutex> lock(mutex_);
        not_full_cv_.wait(lock, [this] {
            return queue_.size() < max_size_ || stopped_;
        });
        if (stopped_) return;
        queue_.push(std::move(item));
        lock.unlock();
        not_empty_cv_.notify_one();
    }

    bool pop(T& out, std::chrono::milliseconds timeout = 1500ms) {
        std::unique_lock<std::mutex> lock(mutex_);
        bool ready = not_empty_cv_.wait_for(lock, timeout, [this] {
            return !queue_.empty() || stopped_;
        });
        if (!ready || queue_.empty()) return false;
        out = std::move(queue_.front());
        queue_.pop();
        lock.unlock();
        not_full_cv_.notify_one();
        return true;
    }

    void stop() {
        {
            std::lock_guard<std::mutex> lock(mutex_);
            stopped_ = true;
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
    bool                    stopped_ = false;
};

// ============================================================
// Shared Sensor Buffer (mutex-protected)
// Collects raw readings from multiple sensor threads.
// The data_processor_thread flushes and processes them.
// ============================================================

class SensorBuffer {
public:
    void write(SensorReading reading) {
        std::lock_guard<std::mutex> lock(mutex_);
        readings_.push_back(std::move(reading));
    }

    // Move all current readings out of the buffer atomically
    std::vector<SensorReading> flush() {
        std::lock_guard<std::mutex> lock(mutex_);
        std::vector<SensorReading> result;
        result.swap(readings_);
        return result;
    }

    size_t count() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return readings_.size();
    }

private:
    mutable std::mutex         mutex_;
    std::vector<SensorReading> readings_;
};

// ============================================================
// Device State Machine (FSM)
// States: INIT -> READING -> PROCESSING -> TRANSMITTING -> READING
//         Any state -> ERROR
// ============================================================

enum class DeviceState {
    INIT,
    READING,
    PROCESSING,
    TRANSMITTING,
    ERROR,
    SHUTDOWN
};

static const char* state_name(DeviceState s) noexcept {
    switch (s) {
        case DeviceState::INIT:         return "INIT";
        case DeviceState::READING:      return "READING";
        case DeviceState::PROCESSING:   return "PROCESSING";
        case DeviceState::TRANSMITTING: return "TRANSMITTING";
        case DeviceState::ERROR:        return "ERROR";
        case DeviceState::SHUTDOWN:     return "SHUTDOWN";
        default:                        return "UNKNOWN";
    }
}

class DeviceStateMachine {
public:
    DeviceState get() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return state_;
    }

    // Transition only if the current state matches `expected`.
    // Returns true on success, false if already in a different state.
    bool transition(DeviceState expected, DeviceState next) {
        std::string msg;
        {
            std::lock_guard<std::mutex> lock(mutex_);
            if (state_ != expected) return false;
            msg  = std::string("[FSM] ") + state_name(expected)
                 + " -> " + state_name(next);
            state_ = next;
        }
        // Log outside the lock — no mutex held during I/O
        log(msg);
        return true;
    }

    // Force transition regardless of current state (for ERROR handling)
    void force(DeviceState next) {
        std::string from;
        {
            std::lock_guard<std::mutex> lock(mutex_);
            from   = state_name(state_);
            state_ = next;
        }
        log(std::string("[FSM] FORCED ") + from + " -> " + state_name(next));
    }

private:
    mutable std::mutex mutex_;
    DeviceState        state_ = DeviceState::INIT;
};

// ============================================================
// Simulated cloud publish (used inside std::async)
// ============================================================

struct PublishResult {
    int  http_status;
    int  records_accepted;
    bool success;
};

PublishResult publish_to_cloud(std::vector<SensorReading> batch) {
    // Simulate network round-trip latency
    std::this_thread::sleep_for(250ms);

    // Simulate an occasional transient failure
    static std::atomic<int> call_count{0};
    int call = ++call_count;
    if (call % 5 == 0) {
        return {503, 0, false};
    }
    return {200, static_cast<int>(batch.size()), true};
}

// ============================================================
// Global state accessible across threads
// ============================================================

std::atomic<bool>     g_running{true};
std::atomic<uint64_t> g_readings_total{0};   // lock-free counter
std::atomic<uint64_t> g_publish_ok{0};       // successful publishes
std::atomic<uint64_t> g_publish_err{0};      // failed publishes
std::atomic<uint64_t> g_sensor_errors{0};    // invalid sensor readings dropped

SensorBuffer                          g_buffer;
BlockingQueue<std::vector<SensorReading>> g_publish_queue(4);
DeviceStateMachine                    g_fsm;

// ============================================================
// Sensor Threads (Producers)
// ============================================================

void temperature_sensor_thread() {
    std::mt19937                       rng(std::random_device{}());
    std::uniform_real_distribution<>   dist(18.0, 36.0);

    while (g_running.load(std::memory_order_relaxed)) {
        SensorReading r;
        r.sensor_id = "TEMP_01";
        r.value     = dist(rng);
        r.unit      = "C";
        r.valid     = true;

        g_buffer.write(r);
        ++g_readings_total;

        std::this_thread::sleep_for(500ms);
    }
}

void humidity_sensor_thread() {
    std::mt19937                       rng(std::random_device{}());
    std::uniform_real_distribution<>   dist(30.0, 90.0);
    int tick = 0;

    while (g_running.load(std::memory_order_relaxed)) {
        SensorReading r;
        r.sensor_id = "HUM_01";
        r.unit      = "%RH";

        // Simulate occasional I2C bus error (invalid reading)
        if (tick % 9 == 0 && tick > 0) {
            r.value = -1.0;
            r.valid = false;
        } else {
            r.value = dist(rng);
            r.valid = true;
        }

        g_buffer.write(r);
        ++g_readings_total;
        ++tick;

        std::this_thread::sleep_for(700ms);
    }
}

void gps_sensor_thread() {
    std::mt19937                       rng(std::random_device{}());
    std::uniform_real_distribution<>   lat_dist(51.48, 51.52);  // London area
    std::uniform_real_distribution<>   lon_dist(-0.12, 0.05);
    int tick = 0;

    while (g_running.load(std::memory_order_relaxed)) {
        if (tick % 11 == 0 && tick > 0) {
            // Simulate GPS fix lost
            SensorReading err;
            err.sensor_id = "GPS_01";
            err.value     = -999.0;
            err.unit      = "FIX_LOST";
            err.valid     = false;
            g_buffer.write(err);
            ++g_readings_total;
        } else {
            SensorReading lat, lon;
            lat.sensor_id = "GPS_LAT"; lat.value = lat_dist(rng);
            lat.unit      = "deg";     lat.valid  = true;
            lon.sensor_id = "GPS_LON"; lon.value = lon_dist(rng);
            lon.unit      = "deg";     lon.valid  = true;

            g_buffer.write(lat);
            g_buffer.write(lon);
            g_readings_total += 2;
        }
        ++tick;
        std::this_thread::sleep_for(1000ms);
    }
}

// ============================================================
// Data Processor Thread
// Wakes every 2 seconds, flushes the sensor buffer, validates
// readings, and pushes valid batches to the publish queue.
// ============================================================

void data_processor_thread() {
    while (g_running.load(std::memory_order_relaxed)) {
        std::this_thread::sleep_for(2000ms);

        g_fsm.transition(DeviceState::READING, DeviceState::PROCESSING);

        std::vector<SensorReading> raw = g_buffer.flush();
        if (raw.empty()) {
            g_fsm.transition(DeviceState::PROCESSING, DeviceState::READING);
            continue;
        }

        // Validate — filter out invalid readings
        std::vector<SensorReading> valid;
        valid.reserve(raw.size());
        int errors = 0;
        for (auto& r : raw) {
            if (r.valid) {
                valid.push_back(std::move(r));
            } else {
                ++errors;
                ++g_sensor_errors;
            }
        }

        std::ostringstream oss;
        oss << "[Processor] raw=" << raw.size()
            << "  valid=" << valid.size()
            << "  dropped=" << errors;
        log(oss.str());

        if (!valid.empty()) {
            g_fsm.transition(DeviceState::PROCESSING, DeviceState::TRANSMITTING);
            g_publish_queue.push(std::move(valid));
        } else {
            g_fsm.transition(DeviceState::PROCESSING, DeviceState::READING);
        }
    }
}

// ============================================================
// Network Publisher Thread
// Pops batches from the queue and publishes them asynchronously
// using std::async so the thread does not block during network I/O.
// ============================================================

void network_publisher_thread() {
    while (g_running.load(std::memory_order_relaxed)) {
        std::vector<SensorReading> batch;

        if (!g_publish_queue.pop(batch, 1500ms)) {
            continue;   // timeout — check g_running and retry
        }

        std::ostringstream oss;
        oss << "[Publisher] Sending batch of " << batch.size() << " records...";
        log(oss.str());

        // Launch publish asynchronously — this thread does not block during I/O
        std::future<PublishResult> fut = std::async(
            std::launch::async,
            publish_to_cloud,
            batch   // copy into async task
        );

        // Retrieve result (waits only for remaining network time)
        PublishResult result = fut.get();

        std::ostringstream oss2;
        oss2 << "[Publisher] HTTP " << result.http_status;
        if (result.success) {
            oss2 << "  accepted=" << result.records_accepted;
            ++g_publish_ok;
        } else {
            oss2 << "  FAILED (will retry next cycle)";
            ++g_publish_err;
        }
        log(oss2.str());

        g_fsm.transition(DeviceState::TRANSMITTING, DeviceState::READING);
    }
}

// ============================================================
// Stats Monitor Thread
// Reads all statistics via std::atomic (lock-free) and prints
// a periodic summary. Does not acquire any mutexes.
// ============================================================

void stats_monitor_thread() {
    int tick = 0;
    while (g_running.load(std::memory_order_relaxed)) {
        std::this_thread::sleep_for(5000ms);
        ++tick;

        std::ostringstream oss;
        oss << "[Monitor #" << tick << "]"
            << "  state="    << state_name(g_fsm.get())
            << "  readings=" << g_readings_total.load()
            << "  pub_ok="   << g_publish_ok.load()
            << "  pub_err="  << g_publish_err.load()
            << "  dropped="  << g_sensor_errors.load()
            << "  q_depth="  << g_publish_queue.size();
        log(oss.str());
    }
}

// ============================================================
// Main
// ============================================================

int main() {
    log("IoT Sensor Hub starting — C++17 Concurrency Demo");

    std::ostringstream hw;
    hw << "Hardware threads available: " << std::thread::hardware_concurrency();
    log(hw.str());
    log("");

    g_fsm.transition(DeviceState::INIT, DeviceState::READING);

    // Launch all concurrent threads
    std::thread t_temp(temperature_sensor_thread);
    std::thread t_hum (humidity_sensor_thread);
    std::thread t_gps (gps_sensor_thread);
    std::thread t_proc(data_processor_thread);
    std::thread t_pub (network_publisher_thread);
    std::thread t_mon (stats_monitor_thread);

    // Run for 20 seconds, then initiate graceful shutdown
    std::this_thread::sleep_for(20s);

    log("\n[Main] Initiating graceful shutdown...");
    g_running.store(false, std::memory_order_relaxed);
    g_publish_queue.stop();   // unblock any waiting pop() calls

    t_temp.join();
    t_hum.join();
    t_gps.join();
    t_proc.join();
    t_pub.join();
    t_mon.join();

    g_fsm.force(DeviceState::SHUTDOWN);

    log("[Main] All threads joined. Final statistics:");

    std::ostringstream summary;
    summary << "  Total readings collected  : " << g_readings_total.load() << "\n"
            << "  Successful publishes      : " << g_publish_ok.load()     << "\n"
            << "  Failed publishes          : " << g_publish_err.load()    << "\n"
            << "  Sensor errors dropped     : " << g_sensor_errors.load();
    log(summary.str());
    log("[Main] Shutdown complete.");

    return 0;
}

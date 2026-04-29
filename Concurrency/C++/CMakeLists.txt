cmake_minimum_required(VERSION 3.14)
project(cpp_iot_concurrency CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(Threads REQUIRED)

# Build all examples
add_subdirectory(examples/01_threads)
add_subdirectory(examples/02_mutex)
add_subdirectory(examples/03_atomic)
add_subdirectory(examples/04_async_future)
add_subdirectory(examples/05_condition_variable)
add_subdirectory(examples/06_iot_sensor_hub)

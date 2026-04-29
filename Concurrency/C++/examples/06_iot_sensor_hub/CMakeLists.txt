cmake_minimum_required(VERSION 3.14)
project(iot_sensor_hub CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Threads REQUIRED)

add_executable(iot_sensor_hub main.cpp)
target_link_libraries(iot_sensor_hub PRIVATE Threads::Threads)

# Enable all warnings in Debug builds
target_compile_options(iot_sensor_hub PRIVATE
    $<$<CONFIG:Debug>:-Wall -Wextra -Wpedantic>
)

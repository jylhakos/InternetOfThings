cmake_minimum_required(VERSION 3.14)
project(atomic_demo CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Threads REQUIRED)

add_executable(atomic_demo main.cpp)
target_link_libraries(atomic_demo PRIVATE Threads::Threads)

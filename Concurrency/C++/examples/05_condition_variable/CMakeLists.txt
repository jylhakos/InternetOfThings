cmake_minimum_required(VERSION 3.14)
project(cv_demo CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Threads REQUIRED)

add_executable(cv_demo main.cpp)
target_link_libraries(cv_demo PRIVATE Threads::Threads)

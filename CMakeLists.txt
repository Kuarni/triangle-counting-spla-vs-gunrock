cmake_minimum_required(VERSION 3.30)
project(spla-gunrock-graph-analysis LANGUAGES CXX CUDA)

set(CMAKE_CXX_STANDARD 17)

option(ENABLE_GUNROCK "Enable gunrock build and benchmark" ON)
option(ENABLE_SPLA "Enable spla build and benchmark" ON)

add_subdirectory(deps)
add_subdirectory(src)

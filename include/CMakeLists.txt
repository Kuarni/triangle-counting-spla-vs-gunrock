set(SPLA_BUILD_TESTS OFF)
set(SPLA_BUILD_EXAMPLES OFF)
add_subdirectory(spla)

include(FetchContent)

set(BENCHMARK_ENABLE_GTEST_TESTS OFF)
FetchContent_Declare(
        benchmark
        GIT_REPOSITORY https://github.com/google/benchmark
        GIT_TAG v1.9.3
        OVERRIDE_FIND_PACKAGE
)
find_package(benchmark REQUIRED)

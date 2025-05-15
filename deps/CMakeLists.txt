if (ENABLE_SPLA)
    set(SPLA_BUILD_TESTS OFF)
    set(SPLA_BUILD_EXAMPLES OFF)
    add_subdirectory(spla EXCLUDE_FROM_ALL)
endif ()

if (ENABLE_GUNROCK)
    set(ESSENTIALS_BUILD_TESTS OFF)
    set(ESSENTIALS_BUILD_BENCHMARKS OFF)
    list(APPEND CMAKE_MODULE_PATH
            "${CMAKE_CURRENT_SOURCE_DIR}/gunrock/externals/cmake_modules-src/"
    )
    add_subdirectory(gunrock EXCLUDE_FROM_ALL)
endif ()

include(FetchContent)

set(BENCHMARK_ENABLE_GTEST_TESTS OFF)
FetchContent_Declare(
        benchmark
        GIT_REPOSITORY https://github.com/google/benchmark
        GIT_TAG v1.9.3
        OVERRIDE_FIND_PACKAGE
        EXCLUDE_FROM_ALL
)
find_package(benchmark REQUIRED)

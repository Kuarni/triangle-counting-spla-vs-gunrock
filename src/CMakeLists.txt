add_library(common INTERFACE)
target_include_directories(common INTERFACE ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(common INTERFACE benchmark::benchmark)

if (ENABLE_GUNROCK)
    add_subdirectory(gunrock)
endif ()

if (ENABLE_SPLA)
    add_subdirectory(spla)
endif ()

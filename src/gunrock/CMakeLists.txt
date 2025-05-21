find_package(CUDAToolkit REQUIRED)
enable_language(CUDA)

set_source_files_properties(algo.cu PROPERTIES LANGUAGE CUDA)
add_executable(gunrock-measure gunrock-measure.cpp algo.cu)
set_target_properties(gunrock-measure PROPERTIES
        CUDA_SEPARABLE_COMPILATION ON
)
target_link_libraries(gunrock-measure PUBLIC essentials benchmark::benchmark common)
target_include_directories(gunrock-measure PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

install(TARGETS gunrock-measure
        RUNTIME DESTINATION .
)

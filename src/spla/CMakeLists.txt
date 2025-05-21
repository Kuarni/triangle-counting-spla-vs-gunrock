add_executable(spla-measure spla-measure.cpp)
target_link_libraries(spla-measure PUBLIC common spla benchmark::benchmark)
target_include_directories(spla-measure PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})


add_custom_command(TARGET spla-measure POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
        $<TARGET_RUNTIME_DLLS:spla-measure>
        $<TARGET_FILE_DIR:spla-measure>
        COMMAND_EXPAND_LISTS
)

install(TARGETS spla-measure spla
        RUNTIME DESTINATION .
)

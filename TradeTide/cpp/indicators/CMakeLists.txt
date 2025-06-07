# cpp/indicators/CMakeLists.txt

set(NAME "indicators")

add_subdirectory(base_indicator)
add_subdirectory(moving_average_crossings)


# Create a Python module, if needed.
pybind11_add_module("interface_${NAME}" MODULE interface.cpp)
set_target_properties("interface_${NAME}" PROPERTIES OUTPUT_NAME "interface_${NAME}")
target_link_libraries("interface_${NAME}" PUBLIC cpp_base_indicator cpp_moving_average_crossings)


install(
    TARGETS interface_${NAME}
    LIBRARY DESTINATION ${TRADETIDE_BIN_DIR}
    ARCHIVE DESTINATION ${TRADETIDE_BIN_DIR}
    RUNTIME DESTINATION ${TRADETIDE_BIN_DIR}
)

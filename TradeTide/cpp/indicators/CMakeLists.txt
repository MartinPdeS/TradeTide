# cpp/indicators/CMakeLists.txt

set(NAME "indicators")

add_subdirectory(base_indicator)
add_subdirectory(moving_average_crossings)
add_subdirectory(bollinger_bands)
add_subdirectory(relative_momentum_index)


# Create a Python module, if needed.
pybind11_add_module("interface_${NAME}" MODULE interface.cpp)
set_target_properties("interface_${NAME}" PROPERTIES OUTPUT_NAME "interface_${NAME}")

target_link_libraries(
    "interface_${NAME}"
    PUBLIC
    cpp_base_indicator
    cpp_moving_average_crossings
    cpp_bollinger_bands
    cpp_relative_momentum_index
    pybind11::module
)


install(
    TARGETS interface_${NAME}
    LIBRARY DESTINATION ${LOCAL_BIN_DIR}
    ARCHIVE DESTINATION ${LOCAL_BIN_DIR}
    RUNTIME DESTINATION ${LOCAL_BIN_DIR}
)

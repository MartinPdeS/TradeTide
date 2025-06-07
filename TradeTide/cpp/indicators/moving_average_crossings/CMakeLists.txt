# # cpp/indicators/moving_average_crossings/CMakeLists.txt

set(NAME "moving_average_crossings")

# Create a shared library for functionality.
add_library("cpp_${NAME}" STATIC "${NAME}.cpp")

target_link_libraries("cpp_${NAME}" PUBLIC pybind11::module cpp_position)


install(
    TARGETS cpp_${NAME}
    LIBRARY DESTINATION ${TRADETIDE_BIN_DIR}
    ARCHIVE DESTINATION ${TRADETIDE_BIN_DIR}
    RUNTIME DESTINATION ${TRADETIDE_BIN_DIR}
)
# # cpp/indicators/moving_average_crossings/CMakeLists.txt

set(NAME "moving_average_crossings")

# Create a shared library for functionality.
add_library("cpp_${NAME}" STATIC "${NAME}.cpp")

target_link_libraries("cpp_${NAME}" PUBLIC cpp_base_indicator)

install(
    TARGETS cpp_${NAME}
    LIBRARY DESTINATION ${LOCAL_BIN_DIR}
    ARCHIVE DESTINATION ${LOCAL_BIN_DIR}
    RUNTIME DESTINATION ${LOCAL_BIN_DIR}
)
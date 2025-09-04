# cpp/indicators/base_indicator/CMakeLists.txt

# Create a shared library for functionality.
add_library(cpp_base_indicator STATIC "base_indicator.cpp")



install(
    TARGETS cpp_base_indicator
    LIBRARY DESTINATION ${LOCAL_BIN_DIR}
    ARCHIVE DESTINATION ${LOCAL_BIN_DIR}
    RUNTIME DESTINATION ${LOCAL_BIN_DIR}
)

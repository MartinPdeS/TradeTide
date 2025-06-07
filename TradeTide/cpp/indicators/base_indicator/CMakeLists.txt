# cpp/indicators/base_indicator/CMakeLists.txt

# Create a shared library for functionality.
add_library(cpp_base_indicator STATIC "base_indicator.cpp")



install(
    TARGETS cpp_base_indicator
    LIBRARY DESTINATION ${TRADETIDE_BIN_DIR}
    ARCHIVE DESTINATION ${TRADETIDE_BIN_DIR}
    RUNTIME DESTINATION ${TRADETIDE_BIN_DIR}
)
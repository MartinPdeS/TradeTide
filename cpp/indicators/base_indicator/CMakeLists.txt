# cpp/indicators/base_indicator/CMakeLists.txt
set(NAME "base_indicator")

# Create a shared library for functionality.
add_library("${NAME}" STATIC "${NAME}.cpp")

set_property(GLOBAL APPEND PROPERTY TRADETIDE_TARGETS "${NAME}")

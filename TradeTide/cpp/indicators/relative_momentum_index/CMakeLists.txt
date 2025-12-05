# # cpp/indicators/relative_momentum_index/CMakeLists.txt

set(NAME "relative_momentum_index")

# Create a shared library for functionality.
add_library("${NAME}" STATIC "${NAME}.cpp")

target_link_libraries("${NAME}" PUBLIC base_indicator)

set_property(GLOBAL APPEND PROPERTY TRADETIDE_TARGETS "${NAME}")

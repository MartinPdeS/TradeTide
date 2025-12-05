# # cpp/indicators/moving_average_crossings/CMakeLists.txt

set(NAME "moving_average_crossings")

# Create a shared library for functionality.
add_library("${NAME}" STATIC "${NAME}.cpp")

target_link_libraries("${NAME}" PUBLIC base_indicator)

set_property(GLOBAL APPEND PROPERTY TRADETIDE_TARGETS "${NAME}")

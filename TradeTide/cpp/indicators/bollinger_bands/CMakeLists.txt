# # cpp/indicators/bollinger_bands/CMakeLists.txt

set(NAME "bollinger_bands")

# Create a shared library for functionality.
add_library("${NAME}" STATIC "${NAME}.cpp")

target_link_libraries("${NAME}" PUBLIC base_indicator)

set_property(GLOBAL APPEND PROPERTY TRADETIDE_TARGETS "${NAME}")

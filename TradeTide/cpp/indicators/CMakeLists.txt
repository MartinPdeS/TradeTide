# cpp/indicators/CMakeLists.txt

set(NAME "indicators")

add_subdirectory(base_indicator)
add_subdirectory(moving_average_crossings)
add_subdirectory(bollinger_bands)
add_subdirectory(relative_momentum_index)
add_subdirectory(relative_strength_index)
add_subdirectory(macd)


# Create a Python module, if needed.
pybind11_add_module("interface_${NAME}" MODULE interface.cpp)
set_target_properties("interface_${NAME}" PROPERTIES OUTPUT_NAME "${NAME}")

target_link_libraries(
    "interface_${NAME}"
    PUBLIC
    base_indicator
    moving_average_crossings
    bollinger_bands
    relative_momentum_index
    relative_strength_index
    macd
    pybind11::module
)

set_property(GLOBAL APPEND PROPERTY TRADETIDE_TARGETS "interface_${NAME}")

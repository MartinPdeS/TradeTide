# cpp/capital_managment/CMakeLists.txt

set(NAME "capital_management")

# Create a shared library for functionality.
add_library("${NAME}" STATIC "${NAME}.cpp")

target_link_libraries("${NAME}" PUBLIC pybind11::module position exit_strategy)

# Create a Python module, if needed.
pybind11_add_module("interface_${NAME}" MODULE interface.cpp)
set_target_properties("interface_${NAME}" PROPERTIES OUTPUT_NAME "interface_${NAME}")
target_link_libraries("interface_${NAME}" PUBLIC "${NAME}")

set_property(GLOBAL APPEND PROPERTY TRADETIDE_TARGETS "${NAME}" "interface_${NAME}")

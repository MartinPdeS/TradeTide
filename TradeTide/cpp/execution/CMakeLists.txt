set(NAME "execution")

pybind11_add_module("interface_${NAME}" MODULE interface.cpp)
set_target_properties("interface_${NAME}" PROPERTIES OUTPUT_NAME "${NAME}")
target_link_libraries("interface_${NAME}" PRIVATE position pybind11::module)

set_property(GLOBAL APPEND PROPERTY TRADETIDE_TARGETS "interface_${NAME}")

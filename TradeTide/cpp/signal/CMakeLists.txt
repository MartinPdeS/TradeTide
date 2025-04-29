# cpp/detector/CMakeLists.txt

set(NAME "signal")

# Create a shared library for functionality.
add_library("cpp_${NAME}" STATIC "${NAME}.cpp")

target_link_libraries("cpp_${NAME}" PUBLIC pybind11::module cpp_market)

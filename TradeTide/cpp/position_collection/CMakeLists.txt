# cpp/detector/CMakeLists.txt

set(NAME "position_collection")

# Create a shared library for functionality.
add_library("cpp_${NAME}" STATIC "${NAME}.cpp")

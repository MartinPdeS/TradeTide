cmake_minimum_required(VERSION 3.10)
project(TradeTide CXX)

# CMake settings
set(CMAKE_VERBOSE_MAKEFILE ON)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(CMAKE_BUILD_TYPE "Release" CACHE STRING "Type of build" FORCE)


# Directories
set(TRADETIDE_CXX_DIR "TradeTide/cpp")
set(TRADETIDE_BIN_DIR "${CMAKE_SOURCE_DIR}/TradeTide/binary")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${TRADETIDE_BIN_DIR}")

# Include directories
include_directories("${TRADETIDE_CXX_DIR}")

find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)
find_package(pybind11 CONFIG REQUIRED)

# Function to add PyMieSim modules
function(add_pymiesim_module name source)
    pybind11_add_module(${name} MODULE "${TRADETIDE_CXX_DIR}/${source}")
    set_target_properties(${name} PROPERTIES OUTPUT_NAME ${name})
endfunction()

add_pymiesim_module(PortfolioInterface "interface.cpp")

cmake_minimum_required(VERSION 3.31)
project(TradeTide CXX)

# CMake settings
set(CMAKE_VERBOSE_MAKEFILE ON)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(CMAKE_BUILD_TYPE "Release" CACHE STRING "Type of build" FORCE)


# Set the output directory for libraries
set(TRADETIDE_CXX_DIR "${CMAKE_SOURCE_DIR}/TradeTide/cpp")
set(TRADETIDE_BIN_DIR "${CMAKE_SOURCE_DIR}/TradeTide/binary")


# Compiler and linker options
add_compile_options(-fPIC -Wall -Wextra -Wno-uninitialized)

find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)
find_package(pybind11 CONFIG REQUIRED)
find_package(OpenMP REQUIRED)

# Print some messages
message(STATUS "TradeTide version is: ${TRADETIDE_VERSION}")
message(STATUS "TradeTide includes directory is: ${TRADETIDE_CXX_DIR}")
message(STATUS "Python version to be compiled against: ${PYBIND11_PYTHON_VERSION}")
message(STATUS "Binary will be installed in location: ${TRADETIDE_BIN_DIR}")

add_subdirectory(TradeTide/cpp/market)               # market
add_subdirectory(TradeTide/cpp/position)             # position
add_subdirectory(TradeTide/cpp/signal)               # signal
add_subdirectory(TradeTide/cpp/state)                # state
add_subdirectory(TradeTide/cpp/record)               # record
add_subdirectory(TradeTide/cpp/exit_strategy)        # exit_strategy
add_subdirectory(TradeTide/cpp/capital_management)   # capital_manag
add_subdirectory(TradeTide/cpp/portfolio)            # portfolio
add_subdirectory(TradeTide/cpp/position_collection)  # position collection
# add_subdirectory(TradeTide/cpp/backtester)         # backtester

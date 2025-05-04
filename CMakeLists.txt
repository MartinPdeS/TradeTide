cmake_minimum_required(VERSION 3.10)
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

# Print some messages
message(STATUS "TradeTide version is: ${TRADETIDE_VERSION}")
message(STATUS "TradeTide includes directory is: ${TRADETIDE_CXX_DIR}")
message(STATUS "Python version to be compiled against: ${PYBIND11_PYTHON_VERSION}")
message(STATUS "Binary will be installed in location: ${TRADETIDE_BIN_DIR}")


add_subdirectory(TradeTide/cpp/position)             # position
add_subdirectory(TradeTide/cpp/market)               # market
add_subdirectory(TradeTide/cpp/signal)               # signal
add_subdirectory(TradeTide/cpp/risk_managment)       # risk_managment
add_subdirectory(TradeTide/cpp/portfolio)            # portfolio
add_subdirectory(TradeTide/cpp/position_collection)  # backtester
add_subdirectory(TradeTide/cpp/backtester)           # backtester


set(
    ALL_TARGETS
    cpp_position cpp_market cpp_signal cpp_risk_managment cpp_backtester cpp_signal cpp_position_collection
    interface_position interface_market interface_risk_managment interface_signal interface_risk_managment interface_position_collection
)

install(
    TARGETS ${ALL_TARGETS}
    LIBRARY DESTINATION ${TRADETIDE_BIN_DIR}
    ARCHIVE DESTINATION ${TRADETIDE_BIN_DIR}
    RUNTIME DESTINATION ${TRADETIDE_BIN_DIR}
)
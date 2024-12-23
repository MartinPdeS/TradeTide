cmake_minimum_required(VERSION 3.10)
project(TradeTide CXX)

# CMake settings
set(CMAKE_VERBOSE_MAKEFILE ON)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(CMAKE_BUILD_TYPE "Release" CACHE STRING "Type of build" FORCE)


# Directories
set(TRADETIDE_INCLUDE_DIR "${CMAKE_SOURCE_DIR}/TradeTide/cpp/includes")
set(TRADETIDE_INTERFACE_DIR "${CMAKE_SOURCE_DIR}/TradeTide/cpp/interfaces")
set(TRADETIDE_BIN_DIR "${CMAKE_SOURCE_DIR}/TradeTide/binary")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${TRADETIDE_BIN_DIR}")

find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)
find_package(pybind11 CONFIG REQUIRED)

# Function to add PyMieSim modules
function(add_pymiesim_module name source)
    pybind11_add_module(${name} MODULE "${TRADETIDE_CXX_DIR}/${source}")
    set_target_properties(${name} PROPERTIES OUTPUT_NAME ${name})
    target_include_directories(${name} PRIVATE "${TRADETIDE_INCLUDE_DIR}")
endfunction()

add_pymiesim_module(MarketInterface "${TRADETIDE_INTERFACE_DIR}/_market.cpp")
add_pymiesim_module(PositionInterface "${TRADETIDE_INTERFACE_DIR}/_position.cpp")
add_pymiesim_module(RiskManagmentInterface "${TRADETIDE_INTERFACE_DIR}/_risk_managment.cpp")
add_pymiesim_module(PortfolioInterface "${TRADETIDE_INTERFACE_DIR}/_portfolio.cpp")

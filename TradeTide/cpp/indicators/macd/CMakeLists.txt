set(NAME "macd")
add_library("${NAME}" STATIC "${NAME}.cpp")
target_link_libraries("${NAME}" PUBLIC base_indicator)
set_property(GLOBAL APPEND PROPERTY TRADETIDE_TARGETS "${NAME}")
